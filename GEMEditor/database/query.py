import logging
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QInputDialog, QWidget, QMessageBox, QDialogButtonBox, QDialog, QHBoxLayout, QCheckBox, QVBoxLayout, QTabWidget, QPushButton, QGroupBox, QProgressDialog
from PyQt5.QtSql import QSqlQuery, QSqlQueryModel, QSql
from collections import OrderedDict
from GEMEditor.base.functions import generate_copy_id, invert_mapping, get_annotation_to_item_map, convert_to_bool
from GEMEditor.base.dialogs import DialogMapCompartment, CustomStandardDialog
from GEMEditor.base.classes import Settings
from GEMEditor.database.base import DatabaseWrapper, pyqt_database_connection, factory_entry_widget
from GEMEditor.database.ui import Ui_AnnotationSettingsDialog, Ui_DatabaseSearchWidget, Ui_ItemSettingWidget
from GEMEditor import DB_GET_MET_NAME, DB_NEW_MET_PREFIX, DB_GET_FL_AND_CH, DB_NEW_REACT_PREFIX, DB_GET_REACT_NAME


LOGGER = logging.getLogger(__name__)


class DialogDatabaseSelection(CustomStandardDialog):

    def __init__(self, model, data_type, parent=None):
        """ Setup dialog

        Parameters
        ----------
        model: GEMEditor.cobraClasses.Model
        data_type: str
        parent: QWidget
        """

        super(DialogDatabaseSelection, self).__init__(parent)

        # Store type
        self.model = model
        self.data_type = data_type

        # Add widgets
        self.search_widget = factory_search_widget(data_type, parent)
        self.settings_widget = factory_setting_widget(data_type, parent)
        self.entry_widget = factory_entry_widget(data_type, parent)

        # Setup ui
        self.central_layout = QVBoxLayout(self)
        self.tabwidget = QTabWidget(self)

        # Add the search tab
        self.search_tab = QWidget()
        search_layout = QHBoxLayout(self)
        search_layout.addWidget(self.search_widget)
        search_layout.addWidget(self.entry_widget)
        self.search_tab.setLayout(search_layout)

        # Ad pages to layout
        self.tabwidget.addTab(self.search_tab, "Search")
        self.tabwidget.addTab(self.settings_widget, "Settings")

        # Setup layout
        self.central_layout.addWidget(self.tabwidget)

        # Add buttonbox
        self.buttonbox = QDialogButtonBox()
        self.central_layout.addWidget(self.buttonbox)

        # Add add button
        add_button = QPushButton("Add {0!s}".format(self.data_type))
        add_button.clicked.connect(self.search_widget.slot_emit_add_item)
        self.buttonbox.addButton(add_button, QDialogButtonBox.ActionRole)

        # Add close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.reject)
        self.buttonbox.addButton(close_button, QDialogButtonBox.RejectRole)

        # Set layout
        self.setLayout(self.central_layout)
        self.entry_widget.hide()

        # Connect signals
        self.search_widget.signal_current_selection.connect(self.entry_widget.update_from_database_id)
        self.search_widget.signal_add_item.connect(self.add_item_from_database)
        self.finished.connect(self.save_dialog_geometry)

        # Set window title
        self.setWindowTitle("Select {0!s}".format(data_type))
        self.restore_dialog_geometry()

    @QtCore.pyqtSlot(int)
    def add_item_from_database(self, identifier):
        LOGGER.debug("Adding {0!s} from database id '{1!s}'".format(self.data_type, identifier))
        if self.data_type.lower() == "metabolite":
            add_metabolite_from_database(self.model, identifier)
        elif self.data_type.lower() == "reaction":
            add_reaction_from_database(self.model, identifier)
        else:
            QMessageBox().critical(None, "Error",
                                   "Unexpected type {0!s} to add to database".format(self.data_type))


class AnnotationSettingsDialog(QDialog, Ui_AnnotationSettingsDialog):

    def __init__(self, parent=None):
        """ Setup the dialog

        Parameters
        ----------
        parent: QWidget
        """

        super(AnnotationSettingsDialog, self).__init__(parent)
        self.setupUi(self)
        self.metabolite_widget = factory_setting_widget("metabolite", self)
        self.reaction_widget = factory_setting_widget("reaction", self)

        self.setup_layout()

    def setup_layout(self):
        # Add the widgets to the layouts
        self.verticalLayout_metabolites.addWidget(self.metabolite_widget)
        self.verticalLayout_reactions.addWidget(self.reaction_widget)

        # Hide reaction annotations
        self.reaction_widget.groupBox_attributes.hide()
        self.metabolite_widget.lineEdit_prefix.hide()
        self.metabolite_widget.label.hide()

    def get_settings(self):
        settings = dict()
        settings["formula_charge"] = self.metabolite_widget.checkBox_use_formula.isChecked()
        settings["update_metabolite_name"] = self.metabolite_widget.checkBox_use_name.isChecked()
        settings["reaction_resources"] = self.reaction_widget.get_selected_annotations()
        settings["metabolite_resources"] = self.metabolite_widget.get_selected_annotations()
        return settings


class DatabaseSettingWidget(QWidget, Ui_ItemSettingWidget):

    def __init__(self, resource_type, parent=None):
        super(DatabaseSettingWidget, self).__init__(parent)
        self.setupUi(self)
        self.widget_resource_mapping = {}

        self.populate_annotations(resource_type)

    def populate_annotations(self, resource_type="metabolite"):
        """ Populate annotation groupBox with checkboxes for users to choose

        Parameters
        ----------
        resources: dict, keys are used as text in the checkboxes

        Returns
        -------
        set
        """

        layout = QVBoxLayout()

        # Get resources from database
        with DatabaseWrapper() as database:
            resources = database.get_miriam_collections(resource_type)

        # Populate widget with one checkbox per resource
        for entry in sorted(resources, key=lambda x: x["name"]):
            new_checkbox = QCheckBox(entry["name"], self)
            new_checkbox.setChecked(bool(entry["use_resource"]))

            # Connect checkbox in order to update state in database
            new_checkbox.stateChanged.connect(self.update_resource_state)
            layout.addWidget(new_checkbox)

            # Update mapping of checkbox to id
            self.widget_resource_mapping[new_checkbox] = entry["id"]

        layout.addStretch(1)
        self.groupBox_annotation.setLayout(layout)

    def populate_widget(self):
        raise NotImplementedError

    def store_settings(self):
        raise NotImplementedError

    def get_selected_annotations(self):
        return set(value for checkbox, value in
                   self.widget_resource_mapping.items() if checkbox.isChecked())

    @QtCore.pyqtSlot()
    def update_resource_state(self):
        checkbox = self.sender()
        resource_id = self.widget_resource_mapping[checkbox]
        with DatabaseWrapper() as database:
            database.update_use_resource(resource_id, checkbox.isChecked())


class MetaboliteSettingWidget(DatabaseSettingWidget):

    def __init__(self, resources, parent=None):
        super(MetaboliteSettingWidget, self).__init__(resources, parent)

        # Populate widgets from settings
        self.populate_widget()

        # Connect update of widgets to update of settings
        self.lineEdit_prefix.textChanged.connect(self.store_settings)
        self.checkBox_use_name.stateChanged.connect(self.store_settings)
        self.checkBox_use_formula.stateChanged.connect(self.store_settings)

    def populate_widget(self):
        settings = Settings()

        # Update prefix
        prefix = settings.value("DB_NEW_MET_PREFIX", DB_NEW_MET_PREFIX)
        self.lineEdit_prefix.setText(prefix)

        # Update checkbox
        name_setting = settings.value("DB_GET_MET_NAME", DB_GET_MET_NAME)
        self.checkBox_use_name.setChecked(convert_to_bool(name_setting))

        formula_charge_setting = settings.value("DB_GET_FL_AND_CH", DB_GET_FL_AND_CH)
        self.checkBox_use_formula.setChecked(convert_to_bool(formula_charge_setting))

    @QtCore.pyqtSlot()
    def store_settings(self):
        settings = Settings()

        settings.setValue("DB_NEW_MET_PREFIX", self.lineEdit_prefix.text())
        settings.setValue("DB_GET_MET_NAME", self.checkBox_use_name.isChecked())
        settings.setValue("DB_GET_FL_AND_CH", self.checkBox_use_formula.isChecked())

        settings.sync()


class ReactionSettingWidget(DatabaseSettingWidget):

    def __init__(self, resources, parent=None):
        super(ReactionSettingWidget, self).__init__(resources, parent)

        # Populate widgets from settings
        self.populate_widget()

        # Connect update of widgets to update of settings
        self.lineEdit_prefix.textChanged.connect(self.store_settings)
        self.checkBox_use_name.stateChanged.connect(self.store_settings)

        # Hide non used widgets
        self.checkBox_use_formula.hide()

    def populate_widget(self):
        settings = Settings()

        # Update prefix
        prefix = settings.value("DB_NEW_REACT_PREFIX", DB_NEW_REACT_PREFIX)
        self.lineEdit_prefix.setText(prefix)

        # Update checkbox
        name_setting = settings.value("DB_GET_REACT_NAME", DB_GET_REACT_NAME)
        self.checkBox_use_name.setChecked(convert_to_bool(name_setting))

    @QtCore.pyqtSlot()
    def store_settings(self):
        settings = Settings()

        settings.setValue("DB_NEW_REACT_PREFIX", self.lineEdit_prefix.text())
        settings.setValue("DB_GET_REACT_NAME", self.checkBox_use_name.isChecked())

        settings.sync()


class CombinedSettingsWidget(QWidget):

    def __init__(self, parent=None):
        super(CombinedSettingsWidget, self).__init__(parent)

        layout = QHBoxLayout()
        self.metabolite_widget = factory_setting_widget("metabolite", parent)
        self.reaction_widget = factory_setting_widget("reaction", parent)
        layout.addWidget(self.reaction_widget)
        layout.addWidget(self.metabolite_widget)
        self.setLayout(layout)

    def get_selected_annotations(self):
        metabolite_selection = self.metabolite_widget.get_selected_annotations()
        return metabolite_selection.extend(self.reaction_widget.get_selected_annotations())


class DatabaseSearchWidget(QWidget, Ui_DatabaseSearchWidget):

    # Signal to be emitted when user wants item to be added
    signal_add_item = QtCore.pyqtSignal(int)

    # Signal to be emitted when user selection changes
    signal_current_selection = QtCore.pyqtSignal(int)

    def __init__(self, queries, headers, parent=None):
        super(DatabaseSearchWidget, self).__init__(parent)
        self.setupUi(self)

        # Setup database connection
        self.database = pyqt_database_connection()
        self.database.open()

        self.databaseModel = QSqlQueryModel(self)
        self.dataView_search_results.setModel(self.databaseModel)

        # Store bound queries for usage
        self.queries = queries
        self.combo_search_options.addItems(sorted(queries.keys()))

        # Connect signals
        self.dataView_search_results.selectionModel().selectionChanged.connect(self.slot_emit_selection_changed)
        self.dataView_search_results.doubleClicked.connect(self.slot_emit_add_item)
        self.pushButton_search.clicked.connect(self.update_query)
        self.combo_search_options.currentIndexChanged.connect(self.update_query)

        # Setup header
        for element in headers:
            self.databaseModel.setHeaderData(0, QtCore.Qt.Horizontal, element)

        self.installEventFilter(self)

    @QtCore.pyqtSlot()
    def update_query(self):
        """ Update the query with the search term

        Returns
        -------
        None
        """
        LOGGER.debug("Updating search query..")
        query = self.queries[self.combo_search_options.currentText()]
        # Todo: Slow query setting freezes ui
        self.databaseModel.setQuery(query.format(input=self.lineEdit_search_input.text().strip()))
        LOGGER.debug(str(self.databaseModel.query().executedQuery()))
        LOGGER.debug("Search complete.")

    def selected_id(self):
        """ Return the id of the currently selected item

        Returns
        -------
        int
        """

        selection = self.dataView_search_results.get_selected_rows()
        if len(selection) != 1:
            return -1
        else:
            return int(self.databaseModel.data(self.databaseModel.index(selection[0], 0)))

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.KeyPress and event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            self.update_query()
            return True
        return False

    @QtCore.pyqtSlot()
    def slot_emit_selection_changed(self):
        """ Emit database id of the currently selected item

        Returns
        -------
        None
        """
        self.signal_current_selection.emit(self.selected_id())

    @QtCore.pyqtSlot()
    def slot_emit_add_item(self):
        """ Emit database id of the currently selected item

        Returns
        -------
        None
        """
        self.signal_add_item.emit(self.selected_id())


def factory_setting_widget(data_type, parent=None):
    """ Factory for database selectiondialogs

    Parameters
    ----------
    data_type: str

    Returns
    -------

    """
    if data_type.lower() == "metabolite":
        return MetaboliteSettingWidget("metabolite", parent)
    elif data_type.lower() == "reaction":
        return ReactionSettingWidget("reaction", parent)
    elif data_type.lower() == "combined":
        return CombinedSettingsWidget(parent)
    elif data_type.lower() == "pathway":
        raise NotImplementedError
    else:
        raise ValueError("Unknown item_type '{0!s}'".format(data_type))


def factory_search_widget(data_type, parent=None):
    """ Factory function for creating DatabaseSearchWidgets

    Parameters
    ----------
    data_type
    parent

    Returns
    -------
    DatabaseSearchWidget
    """

    if data_type.lower() == "metabolite":
        queries = OrderedDict([
            ("by name", "SELECT metabolites.id, metabolites.name, metabolites.formula, metabolites.charge "
                       "FROM metabolite_names JOIN metabolites "
                       "ON metabolite_names.metabolite_id = metabolites.id "
                       "WHERE metabolite_names.name LIKE '%{input}%' "
                       "GROUP BY metabolite_names.metabolite_id;"),
            ("by identifier", "SELECT metabolites.id, metabolites.name, metabolites.formula, metabolites.charge "
                             "FROM metabolite_ids JOIN metabolites "
                             "ON metabolite_ids.metabolite_id = metabolites.id "
                             "WHERE metabolite_ids.identifier = '{input}'"
                             "GROUP BY metabolites.id;")
        ])

        return DatabaseSearchWidget(queries=queries, headers=["ID", "Name", "Formula", "Charge"], parent=parent)
    elif data_type.lower() == "reaction":
        queries = OrderedDict([
            ("by name", "SELECT reactions.id, reactions.string "
                       "FROM reaction_names JOIN reactions "
                       "ON reaction_names.reaction_id = reactions.id "
                       "WHERE reaction_names.name LIKE '%{input}%' "
                       "GROUP BY reaction_names.reaction_id;"),
            ("by identifier", "SELECT reactions.id, reactions.string "
                             "FROM reaction_ids JOIN reactions "
                             "ON reaction_ids.reaction_id = reactions.id "
                             "WHERE reaction_ids.identifier = '{input}' "
                             "GROUP BY reactions.id;")
            # ("by metabolite identifier", "SELECT * FROM reactions WHERE id IN "
            #                              "(SELECT DISTINCT(reaction_id) FROM reaction_participants WHERE metabolite_id IN "
            #                              "(SELECT DISTINCT(metabolite_id) FROM metabolite_ids "
            #                              "WHERE identifier = '{input}'));")
        ])

        return DatabaseSearchWidget(queries=queries, headers=["ID", "Formula"], parent=parent)
    else:
        raise ValueError("Unknown input_type {0!s}".format(data_type))


def add_metabolite_from_database(model, database_id, compartment=None):
    """ Add metabolite from the datase

    Parameters
    ----------
    model: GEMEditor.cobraClasses.Model
    database_id: int or str
    compartment: str

    Returns
    -------

    """

    database = DatabaseWrapper()

    # Get compartment if not provided
    if not compartment:
        compartment, status = QInputDialog().getItem(None, "Select compartment", "Select compartment:",
                                                     sorted(model.gem_compartments.keys()), 0, False)
        if not status:
            LOGGER.debug("User aborted addition on compartment choice")
            return

    # Generate <database_id> : [<Metabolit1>, <Metabolite2>] mapping
    inverted_mapping = invert_mapping(model.database_mapping)

    if database_id in inverted_mapping:
        # Only keep metabolites that are in the target compartment
        possible_duplicates = set([x for x in inverted_mapping[database_id] if x.compartment == compartment])
    else:
        # Generate annotation to metabolite map
        annotation_to_metabolite = get_annotation_to_item_map([x for x in model.metabolites
                                                               if x.compartment == compartment])

        # All annotations of the database metabolite
        metabolite_annotations = database.get_annotations_from_id(database_id, "Metabolite", get_all=True)

        # Collect possible duplicates by overlapping annotations
        possible_duplicates = set()
        for annotation in metabolite_annotations:
            for metabolite in annotation_to_metabolite[annotation]:
                possible_duplicates.add(metabolite)

    # Generate new metabolite
    new_metabolite = database.get_metabolite_from_id(database_id)
    new_metabolite.id = generate_copy_id("New", model.metabolites, suffix="")
    new_metabolite.compartment = compartment

    for metabolite in possible_duplicates:
        # Ask user if metabolite is already present
        response = QMessageBox().question(None, "Potential duplicate",
                                          "A potential duplicate has been found:\n"
                                          "ID: {metabolite_id}\n"
                                          "Name: {metabolite_name}\n\n"
                                          "Do you want to add the metabolite anyway?".format(
                                              metabolite_id=metabolite.id,
                                              metabolite_name=metabolite.name))
        # User does not want to add the metabolite
        if response == QDialogButtonBox.No:
            return metabolite

    # Add metabolite to model
    model.add_metabolites([new_metabolite])
    model.QtMetaboliteTable.update_row_from_item(new_metabolite)
    return new_metabolite


def add_reaction_from_database(model, database_id):
    """ Add a reaction from the database

    Parameters
    ----------
    model: GEMEditor.cobraClasses.Model
    database_id: int

    Returns
    -------

    """
    database = DatabaseWrapper()

    # Setup new reaction
    new_reaction = database.get_reaction_from_id(identifier=database_id)
    if new_reaction is None:
        return None

    new_reaction.id = generate_copy_id("New", model.reactions, suffix="")

    # Get reaction participants
    participants = database.get_reaction_participants_from_id(identifier=database_id)

    # Get mapping of database compartments to model compartments
    dialog = DialogMapCompartment(input_compartments=[x["compartment_id"] for x in participants],
                                  model=model)

    # Aborted by user
    if not dialog.exec_():
        return None

    # Metabolite compartment map
    metabolite_compartment_map = dialog.get_mapping()

    # Add metabolites from model
    stoichiometry = {}
    for participant in participants:
        compartment_id = participant["compartment_id"]
        model_compartment = metabolite_compartment_map[compartment_id]
        metabolite_id = participant["metabolite_id"]
        coefficient = participant["stoichiometry"]

        # Get metabolite
        metabolite = add_metabolite_from_database(model=model,
                                                  database_id=metabolite_id,
                                                  compartment=model_compartment)
        stoichiometry[metabolite] = coefficient

    # Add reaction stoichiometry
    new_reaction.add_metabolites(stoichiometry)

    # Add reaction to model
    model.add_reactions([new_reaction])
    model.QtReactionTable.update_row_from_item(new_reaction)

    return new_reaction

