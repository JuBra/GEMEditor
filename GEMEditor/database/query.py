from PyQt5 import QtSql, QtCore
from PyQt5.QtWidgets import QTableWidgetItem, QProgressDialog, QApplication, QInputDialog, QWidget, QMessageBox, QDialogButtonBox
from collections import OrderedDict
from GEMEditor.database.ui import Ui_DatabaseSelectionDialog
from GEMEditor.cobraClasses import Metabolite, generate_copy_id, find_duplicate_metabolite
from GEMEditor.data_classes import Annotation
from GEMEditor.base.dialogs import CustomStandardDialog
from GEMEditor import setup_database


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
                                                                 same_compartment=True)
                if potential_duplicates:
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
            progress.close()

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
