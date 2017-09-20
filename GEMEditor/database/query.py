import sqlite3
import logging
from PyQt5 import QtSql, QtCore
from PyQt5.QtWidgets import QTableWidgetItem, QProgressDialog, QApplication, QInputDialog, QWidget, QMessageBox, QDialogButtonBox, QDialog, QPushButton
from GEMEditor.database.ui import Ui_DatabaseSelectionDialog
from GEMEditor.cobraClasses import Metabolite, generate_copy_id, find_duplicate_metabolite
from GEMEditor.data_classes import Annotation
from GEMEditor.base.dialogs import CustomStandardDialog
from GEMEditor.database.ui.MetaboliteEntryDisplayWidget import Ui_MetaboliteEntryDisplayWidget
from GEMEditor.database.ui.ManualMetaboliteMatchDialog import Ui_ManualMatchDialog
from GEMEditor.database import database_path
from GEMEditor import setup_database

LOGGER = logging.getLogger(__name__)


query_identifier_from_metabolite_id = """SELECT resource_id, name, identifier 
FROM (SELECT * FROM metabolite_ids WHERE metabolite_id = ?) AS temp 
LEFT JOIN resources ON temp.resource_id = resources.id;"""

query_identifier_from_reaction_id = """SELECT resource_id, name, identifier 
FROM (SELECT * FROM reaction_ids WHERE reaction_id = ?) AS temp 
LEFT JOIN resources ON temp.resource_id = resources.id;"""

query_metabolite_synonyms_from_id = """SELECT DISTINCT(name) 
FROM metabolite_names 
WHERE metabolite_id = ?;"""

query_reaction_synonyms_from_id = """SELECT DISTINCT(name) 
FROM reaction_names 
WHERE reaction_id = ?;"""

query_resource_id_and_type_from_collection = """SELECT id, type 
FROM resources 
WHERE miriam_collection = ?;"""

query_metabolite_id_from_annotation = """SELECT DISTINCT(metabolite_id) 
FROM metabolite_ids 
WHERE identifier = ? AND resource_id = ?;"""

query_reaction_id_from_annotation = """SELECT DISTINCT(reaction_id) 
FROM reaction_ids 
WHERE identifier = ? AND resource_id = ?;"""

query_metabolite_info_from_id = """SELECT name, formula, charge 
FROM metabolites 
WHERE id = ?;"""

query_annotation_from_metabolite_id = """SELECT miriam_collection, identifier 
FROM (SELECT * FROM metabolite_ids WHERE metabolite_id = ?) AS temp 
LEFT JOIN resources ON temp.resource_id = resources.id;"""

query_metabolite_id_from_name = """"SELECT metabolite_id 
FROM metabolite_names 
WHERE name=? 
COLLATE NOCASE;"""

query_reaction_id_from_name = """"SELECT reaction_id 
FROM reaction_names 
WHERE name=? 
COLLATE NOCASE;"""

query_metabolite_id_from_formula = """SELECT id 
FROM metabolites 
WHERE formula = ?;"""


class DatabaseWrapper:

    def __init__(self):
        self.connection = None
        self.cursor = None
        self.setup_connection()

    def setup_connection(self):
        self.connection = sqlite3.connect(database_path)
        self.cursor = self.connection.cursor()

    def get_synonyms_from_id(self, identifier, entry_type):
        """ Get all synonyms for entry in database with given identifier

        Parameters
        ----------
        identifier: str
        entry_type: str

        Returns
        -------
        list
        """

        if entry_type == "Metabolite":
            self.cursor.execute(query_metabolite_synonyms_from_id, (str(identifier),))
        elif entry_type == "Reaction":
            self.cursor.execute(query_reaction_synonyms_from_id, (str(identifier),))
        else:
            raise ValueError("Unexpected entry_type: '{0!s}'".format(entry_type))

        # Return unpacked synonyms
        return [x[0] for x in self.cursor.fetchall()]

    def get_annotations_from_id(self, identifier, entry_type):
        """ Get all annotations from a database identifier

        Parameters
        ----------
        identifier: str or int
        entry_type: str, "Metabolite" or "Reaction"

        Returns
        -------
        list of Annotation objects
        """

        # Run query depending on the specified type
        if entry_type == "Metabolite":
            self.cursor.execute(query_annotation_from_metabolite_id, (str(identifier),))
        elif entry_type == "Reaction":
            self.cursor.execute(query_identifier_from_reaction_id, (str(identifier),))
        else:
            raise ValueError("Unexpected entry_type: '{0!s}'".format(entry_type))

        # Return annotations
        annotations = []
        for collection, identifier in self.cursor.fetchall():
            annotations.append(Annotation(collection, identifier))
        return annotations

    def get_ids_from_annotation(self, identifier, collection):
        # Get resource type from collection
        self.cursor.execute(query_resource_id_and_type_from_collection, collection)
        resource_id, resource_type = self.cursor.fetchone()

        # Return the identifier from the annotation
        if resource_type == "metabolite":
            self.cursor.execute(query_metabolite_id_from_annotation, (identifier, resource_id))
            return self.cursor.fetchall()
        elif resource_type == "reaction":
            self.cursor.execute(query_reaction_id_from_annotation, (identifier, resource_id))
            return self.cursor.fetchall()
        else:
            raise NotImplementedError

    def get_ids_from_name(self, name, entry_type):
        """ Find matching database entries by name

        Parameters
        ----------
        name: str
        entry_type: str

        Returns
        -------

        """
        if entry_type == "Metabolite":
            self.cursor.execute(query_metabolite_id_from_name, (str(name),))
        elif entry_type == "Reaction":
            self.cursor.execute(query_reaction_id_from_name, (str(name),))
        else:
            raise ValueError("Unexpected entry_type: '{0!s}'".format(entry_type))

        return [x[0] for x in self.cursor.fetchall()]

    def get_ids_from_formula(self, formula):
        self.cursor.execute(query_metabolite_id_from_formula, (str(formula),))
        return [x[0] for x in self.cursor.fetchall()]

    def get_metabolites_from_ids(self, ids):
        raise NotImplementedError

    def get_metabolite_from_id(self, identifier):
        """ Retrieve metabolite from database

        Parameters
        ----------
        identifier: str

        Returns
        -------

        """

        self.cursor.execute(query_metabolite_info_from_id, (str(identifier),))
        metabolite_info = self.cursor.fetchone()

        if metabolite_info:
            metabolite = Metabolite(name=metabolite_info[0],
                                    formula=metabolite_info[1],
                                    charge=metabolite_info[2])
            annotations = self.get_annotations_from_id(identifier, "Metabolite")
            metabolite.annotation.update(annotations)
            return metabolite

    @QtCore.pyqtSlot()
    def close(self):
        self.cursor.close()
        self.connection.close()


class MetaboliteEntryDisplayWidget(QWidget, Ui_MetaboliteEntryDisplayWidget):

    def __init__(self):
        super(MetaboliteEntryDisplayWidget, self).__init__()
        self.setupUi(self)

    def set_information(self, metabolite, synonyms=()):
        """ Update the information from the metabolite
        and the synonyms passed

        Parameters
        ----------
        metabolite: GEMEditor.cobraClasses.Metabolite
        synonyms: list

        Returns
        -------
        None
        """

        # Update labels
        self.label_name.setText(str(metabolite.name))
        self.label_charge.setText(str(metabolite.charge))
        self.label_formula.setText(str(metabolite.formula))

        # Update synonyms
        self.list_synonyms.clear()
        for entry in synonyms:
            self.list_synonyms.addItem(entry)

        # Update identifiers
        self.table_identifiers.setRowCount(len(metabolite.annotation))
        self.table_identifiers.setColumnCount(2)

        # Add identifiers
        n = 0
        for annotation in metabolite.annotation:
            self.table_identifiers.setItem(n, 0, QTableWidgetItem(annotation.collection))
            self.table_identifiers.setItem(n, 1, QTableWidgetItem(annotation.identifier))
            n += 1

        # Reset header items
        self.table_identifiers.setHorizontalHeaderLabels(["Resource", "ID"])


class DatabaseSelectionDialog(CustomStandardDialog, Ui_DatabaseSelectionDialog):
    queries = {"Metabolite name": "SELECT metabolites.id, metabolites.name, metabolites.formula, metabolites.charge "
                                  "FROM metabolite_names JOIN metabolites "
                                  "ON metabolite_names.metabolite_id = metabolites.id "
                                  "WHERE metabolite_names.name LIKE '%{}%' "
                                  "GROUP BY metabolite_names.metabolite_id;",
               "Metabolite identifier": "SELECT metabolites.id, metabolites.name, metabolites.formula, metabolites.charge "
                                        "FROM metabolite_ids JOIN metabolites "
                                        "ON metabolite_ids.metabolite_id = metabolites.id "
                                        "WHERE metabolite_ids.identifier LIKE '%{}%' "
                                        "GROUP BY metabolites.id;"}

    ids_query = "SELECT id, identifier, miriam_collection " \
                "FROM resources " \
                "JOIN (SELECT resource_id, identifier FROM metabolite_ids WHERE metabolite_id = ?) as me " \
                "ON me.resource_id = resources.id;"

    synonyms_query = "SELECT name " \
                     "FROM metabolite_names " \
                     "WHERE metabolite_id = ?;"

    def __init__(self, parent, model):
        super(DatabaseSelectionDialog, self).__init__(parent)
        self.database = setup_database()
        self.databaseModel = QtSql.QSqlQueryModel(self)
        self.model = model

        self.setupUi(self)
        self.dataView.setModel(self.databaseModel)
        self.comboBox.addItems(sorted(self.queries.keys()))

        if self.database is None or not self.database.open():
            raise ConnectionError

        self.query_ids = QtSql.QSqlQuery(self.ids_query, self.database)
        self.query_synonyms = QtSql.QSqlQuery(self.synonyms_query, self.database)

        self.dataView.selectionModel().selectionChanged.connect(self.populate_information_box)

        self.installEventFilter(self)

        self.restore_dialog_geometry()
        self.groupBox_2.hide()
        self.setWindowTitle("Add metabolite")
        self.setup_signals()

    def setup_signals(self):
        self.dataView.doubleClicked.connect(self.add_model_item)

    def setup_table(self):
        self.databaseModel.setHeaderData(0, QtCore.Qt.Horizontal, "ID")
        self.databaseModel.setHeaderData(1, QtCore.Qt.Horizontal, "Name")
        self.databaseModel.setHeaderData(2, QtCore.Qt.Horizontal, "Formula")
        self.databaseModel.setHeaderData(3, QtCore.Qt.Horizontal, "Charge")

    @QtCore.pyqtSlot()
    def update_query(self):
        query = self.queries[self.comboBox.currentText()].format(self.lineEdit.text().strip())
        self.databaseModel.setQuery(query)
        self.setup_table()
        self.populate_information_box()

    @QtCore.pyqtSlot()
    def populate_information_box(self):
        selection = self.dataView.get_selected_rows()
        if len(selection) != 1:
            self.groupBox_2.setVisible(False)
            return
        row = selection[0]
        metabolite_id = self.databaseModel.data(self.databaseModel.index(row, 0))
        name = self.databaseModel.data(self.databaseModel.index(row, 1))

        self.label_charge.setText(str(self.databaseModel.data(self.databaseModel.index(row, 3))))
        self.label_formula.setText(str(self.databaseModel.data(self.databaseModel.index(row, 2))))
        self.label_name.setText("-\n".join((name[0 + i:45 + i] for i in range(0, len(name), 45))))

        self.populate_synonym_list(metabolite_id)
        self.populate_identifier_list(metabolite_id)
        self.groupBox_2.setVisible(True)

    def populate_synonym_list(self, metabolite_id):
        self.list_synonyms.clear()
        self.query_synonyms.addBindValue(metabolite_id)
        self.query_synonyms.exec_()

        n = 0
        while self.query_synonyms.next():
            synonym = self.query_synonyms.value(0)
            self.list_synonyms.addItem(synonym)
            n += 1

    def populate_identifier_list(self, metabolite_id):
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(2)
        self.query_ids.addBindValue(metabolite_id)
        self.query_ids.exec_()

        n = 0
        while self.query_ids.next():
            self.tableWidget.insertRow(n)
            resource = self.query_ids.value(0)
            identifier = self.query_ids.value(1)

            self.tableWidget.setItem(n, 0, QTableWidgetItem(resource))
            self.tableWidget.setItem(n, 1, QTableWidgetItem(identifier))
            n += 1

        self.tableWidget.setHorizontalHeaderLabels(["Resource", "ID"])

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.KeyPress and event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            self.update_query()
            return True
        return False

    @QtCore.pyqtSlot()
    def add_model_item(self, *args):
        # Get selection
        rows = self.dataView.get_selected_rows()
        if rows and self.model:
            # Get the compartment to which the metabolites should be added
            compartment_id, status = QInputDialog().getItem(self, "Select compartment", "Select compartment:",
                                                            sorted(self.model.compartments.keys()), 0, False)
            if not status:
                return

            for i, row in enumerate(rows):

                # Get info from database
                metabolite_id = self.databaseModel.data(self.databaseModel.index(row, 0))
                name = self.databaseModel.data(self.databaseModel.index(row, 1))
                charge = int(self.databaseModel.data(self.databaseModel.index(row, 3)))
                formula = self.databaseModel.data(self.databaseModel.index(row, 2))

                # Generate new metabolite from database entry
                new_metabolite = Metabolite(id=generate_copy_id("New", self.model.metabolites, suffix=""),
                                            formula=formula, charge=charge, name=name, compartment=compartment_id)

                # Add annotations
                self.query_ids.addBindValue(metabolite_id)
                self.query_ids.exec_()
                while self.query_ids.next():
                    identifier = self.query_ids.value(1)
                    collection = self.query_ids.value(2)

                    # Exclude identifier from resources not in MIRIAM registry
                    if identifier and collection:
                        annotation = Annotation(collection=self.query_ids.value(2),
                                                identifier=self.query_ids.value(1))
                        new_metabolite.annotation.add(annotation)

                # Check for possible duplicates
                potential_duplicates = find_duplicate_metabolite(metabolite=new_metabolite,
                                                                 collection=self.model.metabolites,
                                                                 same_compartment=True,
                                                                 ignore_charge=True)
                if potential_duplicates:
                    print(potential_duplicates)
                    metabolite, score = potential_duplicates[0]
                    response = QMessageBox().question(None, "Potential duplicate",
                                                      "A potential duplicate has been found:\n"
                                                      "ID: {metabolite_id}\n"
                                                      "Name: {metabolite_name}\n\n"
                                                      "Do you want to add the metabolite anyway?".format(
                                                          metabolite_id=metabolite.id,
                                                          metabolite_name=metabolite.name))
                    # User does not want to add the metabolite
                    if response == QDialogButtonBox.No:
                        continue

                self.model.add_metabolites([new_metabolite])
                self.model.QtMetaboliteTable.update_row_from_item(new_metabolite)

    def closeEvent(self, QCloseEvent):
        """ Close database connection before closing """

        if self.database.isOpen():
            self.database.close()
        QCloseEvent.accept()


class ReactionSelectionDialog(DatabaseSelectionDialog):
    queries = {"EC number": "SELECT reactions.id, reactions.string FROM reaction_ids JOIN reactions "
                            "ON reaction_ids.reaction_id = reactions.id "
                            "WHERE reaction_ids.identifier LIKE '%?%' "
                            "GROUP BY reactions.id;",
               "Name": ""}

    def __init__(self, parent, model):
        super(ReactionSelectionDialog, self).__init__(parent, model)

    def add_item_to_model(self, *args):
        selection = self.dataView.get_selected_rows()
        if len(selection) != 1:
            self.groupBox_2.setVisible(False)
            return
        row = selection[0]
        metabolite_id = self.databaseModel.data(self.databaseModel.index(row, 0))


class ManualMatchDialog(QDialog, Ui_ManualMatchDialog):

    def __init__(self, parent=None, unmatched_items=None):
        super(ManualMatchDialog, self).__init__(parent)
        self.setupUi(self)
        self.unmatched_items = unmatched_items
        self.current_metabolite = None
        self.current_entries = None
        self.manual_mapped = dict()
        self.database = DatabaseWrapper()

        self.button_save = QPushButton("Save match")
        self.button_skip = QPushButton("Skip")
        self.buttonBox.addButton(self.button_save, QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.button_skip, QDialogButtonBox.ActionRole)

        self.connect_signals()
        self.next_metabolite()

    def connect_signals(self):

        # Connect entry buttons
        self.button_next_entry.clicked.connect(self.next_entry)
        self.button_previous_entry.clicked.connect(self.previous_entry)

        # Connect display update when changing index of entries
        self.stackedWidget_database.currentChanged.connect(self.update_entry_label)
        self.stackedWidget_database.currentChanged.connect(self.update_database_buttons)

        # Connect buttonbox buttons
        self.button_save.clicked.connect(self.save_mapping)
        self.button_skip.clicked.connect(self.next_metabolite)

    def populate_model_metabolite(self, metabolite):
        self.display_model_metabolite.set_metabolite(metabolite)

    def populate_database_entries(self, entries):
        """ Populate the stacked widget for database entries

        Parameters
        ----------
        entries: list

        Returns
        -------
        None
        """

        # Clear existing widgets
        for idx in reversed(range(self.stackedWidget_database.count())):
            self.stackedWidget_database.removeWidget(self.stackedWidget_database.widget(idx))

        # Add new widgets
        for entry in entries:
            widget = MetaboliteEntryDisplayWidget()

            # Setup widget
            metabolite = self.database.get_metabolite_from_id(entry)
            synonyms = self.database.get_synonyms_from_id(entry, entry_type="Metabolite")
            annotations = self.database.get_annotations_from_id(entry, entry_type="Metabolite")
            metabolite.annotation.update(annotations)
            widget.set_information(metabolite, synonyms)

            # Add widget to the dialog
            self.stackedWidget_database.addWidget(widget)

        # Update view
        self.update_database_buttons(0)
        self.update_entry_label(0)

    @QtCore.pyqtSlot()
    def next_metabolite(self):
        # Return if no unmatched items are set
        if self.unmatched_items is None:
            return

        try:
            metabolite, entries = self.unmatched_items.popitem()
        except KeyError:
            # Close dialog if there is no more metabolite to match
            self.close()
        else:
            # Update current items
            self.current_metabolite = metabolite
            self.current_entries = entries

            # Update display
            self.populate_model_metabolite(metabolite)
            self.populate_database_entries(entries)

    @QtCore.pyqtSlot()
    def next_entry(self):
        """ Move entry display widget to next entry """
        current_index = self.stackedWidget_database.currentIndex()
        if current_index + 1 < self.stackedWidget_database.count():
            self.stackedWidget_database.setCurrentIndex(current_index+1)

    @QtCore.pyqtSlot()
    def previous_entry(self):
        """ Move entry display widget to previous entry """
        current_index = self.stackedWidget_database.currentIndex()
        if current_index > 0:
            self.stackedWidget_database.setCurrentIndex(current_index-1)

    @QtCore.pyqtSlot(int)
    def update_database_buttons(self, idx):
        """ Disable or enable buttons to switch database item

        Parameters
        ----------
        idx: int

        Returns
        -------

        """
        count = self.stackedWidget_database.count()
        self.button_next_entry.setEnabled(idx+1 < count)
        self.button_previous_entry.setEnabled(idx != 0)

    @QtCore.pyqtSlot(int)
    def update_entry_label(self, idx):
        """ Update label according to the index

        Parameters
        ----------
        idx

        Returns
        -------

        """
        self.label.setText("{0!s} / {1!s}".format(idx+1,
                                                  self.stackedWidget_database.count()))

    @QtCore.pyqtSlot()
    def save_mapping(self):

        entries_idx = self.stackedWidget_database.currentIndex()
        if self.current_metabolite is not None:
            self.manual_mapped[self.current_metabolite] = self.current_entries[entries_idx]

        # Move to next metabolite
        self.next_metabolite()

    def closeEvent(self, QCloseEvent):
        LOGGER.debug("Closing dialog.")
        self.database.close()
        super(ManualMatchDialog, self).closeEvent(QCloseEvent)


def add_items_from_database(model, selection_type):
    """ Add items from the database to the model
    
    Parameters
    ----------
    model: GEMEditor.cobraClasses.Model
    type: str

    Returns
    -------

    """

    # Check that the database is working properly
    database = setup_database()
    if database is None or not database.open():
        return

    # Run actions
    if selection_type == "metabolite":
        raise NotImplementedError
    elif selection_type == "reaction":
        raise NotImplementedError
    elif selection_type == "pathway":
        raise NotImplementedError
    else:
        raise ValueError("Unexpected option '[}' for selection_type".format(str(selection_type)))


if __name__ == '__main__':
    metabolite = Metabolite(id="H2O", formula="H2O", name="Water", charge=0, compartment="c")
    metabolite2 = Metabolite(id="H", formula="H", name="Proton", charge=1, compartment="c")
    app = QApplication([])
    LOGGER.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    LOGGER.addHandler(handler)
    dialog = ManualMatchDialog(unmatched_items={metabolite: ["1", "50", "250"],
                                                metabolite2: ["5", "10", "15", "20", "25"]})
    dialog.exec_()
