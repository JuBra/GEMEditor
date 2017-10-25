import os
import sqlite3
import logging
from PyQt5 import QtCore, QtSql
from PyQt5.QtWidgets import QMessageBox, QWidget, QTableWidgetItem
from GEMEditor.cobraClasses import Metabolite, Reaction
from GEMEditor.data_classes import Annotation
from GEMEditor.database import database_path as DB_PATH
from GEMEditor.database.ui import Ui_MetaboliteEntryDisplayWidget, Ui_ReactionEntryDisplayWidget


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

query_reaction_info_from_id = """SELECT * 
FROM reactions 
WHERE id = ?;"""

query_annotation_from_metabolite_id = """SELECT miriam_collection, identifier 
FROM (SELECT * FROM metabolite_ids WHERE metabolite_id = ?) AS temp 
LEFT JOIN resources ON temp.resource_id = resources.id 
WHERE miriam_collection IS NOT NULL
AND use_resource = 1;"""

query_all_annotation_from_metabolite_id = """SELECT miriam_collection, identifier 
FROM (SELECT * FROM metabolite_ids WHERE metabolite_id = ?) AS temp 
LEFT JOIN resources ON temp.resource_id = resources.id 
WHERE miriam_collection IS NOT NULL;"""

query_annotation_from_reaction_id = """SELECT miriam_collection, identifier 
FROM (SELECT * FROM reaction_ids WHERE reaction_id = ?) AS temp 
LEFT JOIN resources ON temp.resource_id = resources.id 
WHERE miriam_collection IS NOT NULL
AND use_resource = 1;"""

query_all_annotation_from_reaction_id = """SELECT miriam_collection, identifier 
FROM (SELECT * FROM reaction_ids WHERE reaction_id = ?) AS temp 
LEFT JOIN resources ON temp.resource_id = resources.id 
WHERE miriam_collection IS NOT NULL;"""

query_metabolite_id_from_name = """SELECT metabolite_id 
FROM metabolite_names 
WHERE name=? 
COLLATE NOCASE;"""

query_reaction_id_from_name = """SELECT reaction_id 
FROM reaction_names 
WHERE name=? 
COLLATE NOCASE;"""

query_metabolite_id_from_formula = """SELECT id 
FROM metabolites 
WHERE formula = ?;"""

query_miriam_resources = """SELECT * 
FROM resources 
WHERE type=? AND miriam_collection IS NOT NULL;"""

query_update_resource = """UPDATE resources
SET use_resource = ?
WHERE id = ?;"""

query_reaction_participants_from_id = """SELECT * FROM 
(SELECT * FROM reaction_participants WHERE reaction_id = ?) AS a 
LEFT JOIN metabolites 
WHERE a.metabolite_id = metabolites.id;"""

query_reaction_ids_from_participating_metabolite_ids = """SELECT DISTINCT(reaction_id) 
FROM reaction_participants 
WHERE metabolite_id = ?;"""


class DatabaseWrapper:

    def __init__(self, database_path=None, selected_collections=set()):
        self.connection = None
        self.cursor = None
        self.selected_collections = selected_collections
        self.setup_connection(database_path)

    def setup_connection(self, database_path):
        if database_path is None:
            database_path = self.get_database_path()

        if not os.path.isfile(database_path):
            raise FileNotFoundError

        self.connection = sqlite3.connect(database_path)
        # Make results accessible by index and by column
        self.connection.row_factory = sqlite3.Row
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

    def get_annotations_from_id(self, identifier, entry_type, get_all=False):
        """ Get all annotations from a database identifier

        Parameters
        ----------
        identifier: str or int
        entry_type: str, "Metabolite" or "Reaction"
        get_all: bool, Get all annotations irrespective if active or not

        Returns
        -------
        list of Annotation objects
        """

        # Run query depending on the specified type
        if entry_type.lower() == "metabolite":
            if get_all:
                self.cursor.execute(query_all_annotation_from_metabolite_id, (str(identifier),))
            else:
                self.cursor.execute(query_annotation_from_metabolite_id, (str(identifier),))
        elif entry_type.lower() == "reaction":
            if get_all:
                self.cursor.execute(query_all_annotation_from_reaction_id, (str(identifier),))
            else:
                self.cursor.execute(query_annotation_from_reaction_id, (str(identifier),))
        else:
            raise ValueError("Unexpected entry_type: '{0!s}'".format(entry_type))

        # Return annotations
        annotations = [Annotation(collection, identifier) for
                       collection, identifier in self.cursor.fetchall()]
        return annotations

    def get_ids_from_annotation(self, identifier, collection):
        # Get resource type from collection
        self.cursor.execute(query_resource_id_and_type_from_collection, (collection,))
        try:
            resource_id, resource_type = self.cursor.fetchone()
        except TypeError:
            LOGGER.debug("Resource {0!s} not in database.".format(collection))
            return []

        # Return the identifier from the annotation
        if resource_type == "metabolite":
            self.cursor.execute(query_metabolite_id_from_annotation, (identifier, resource_id))
            return [x[0] for x in self.cursor.fetchall()]
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

    def get_metabolite_from_id(self, identifier):
        """ Retrieve metabolite from database

        Parameters
        ----------
        use_selection: bool, Only add annotations from collections specified
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

    def get_reaction_participants_from_id(self, identifier):
        """ Get the reaction participants

        Parameters
        ----------
        identifier

        Returns
        -------

        """
        self.cursor.execute(query_reaction_participants_from_id, (identifier,))
        return self.cursor.fetchall()

    def get_reaction_string_from_id(self, identifier):
        """ Get the reaction information from identifier

        Parameters
        ----------
        identifier: int

        Returns
        -------

        """

        self.cursor.execute(query_reaction_info_from_id, (identifier,))
        result = self.cursor.fetchone()
        if result:
            return result["string"]

    def get_reaction_from_id(self, identifier):
        """ Get an empty reaction from the database for a given identifier

        Parameters
        ----------
        identifier

        Returns
        -------

        """
        reaction = Reaction()
        annotations = self.get_annotations_from_id(identifier, "Reaction")
        reaction.annotation.update(annotations)
        return reaction

    def get_miriam_collections(self, type="metabolite"):
        self.cursor.execute(query_miriam_resources, (type.lower(),))
        return self.cursor.fetchall()

    def set_selected_collections(self, collections):
        """ Set the selected annotation sources

        In order to only add the annotations of a subset of databases
        used in MetaNetX the corresponding

        Parameters
        ----------
        collections: set

        Returns
        -------

        """
        self.selected_collections = collections

    def update_use_resource(self, resource, value):
        """ Update the use resource flag in the resource table

        Parameters
        ----------
        resource: int, id of the corresponding resource
        value: bool, If annotations should be used when adding items from the database

        Returns
        -------

        """

        self.cursor.execute(query_update_resource, (int(value), resource))
        self.connection.commit()

    def get_reaction_id_from_participant_ids(self, metabolite_ids):

        sets = []
        for metabolite_id in metabolite_ids:
            self.cursor.execute(query_reaction_ids_from_participating_metabolite_ids,
                                (metabolite_id,))
            sets.append(set(row["reaction_id"] for row in self.cursor.fetchall()))

        if sets:
            return set.intersection(*sets)
        else:
            return set()

    @QtCore.pyqtSlot()
    def close(self):
        self.cursor.close()
        self.connection.close()

    @staticmethod
    def store_database_path(database_path):
        settings = QtCore.QSettings()
        settings.setValue("DATABASE_PATH", database_path)
        settings.sync()

    @staticmethod
    def get_database_path():
        settings = QtCore.QSettings()
        return settings.value("DATABASE_PATH", DB_PATH)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DatabaseEntryWidget(QWidget):

    def __init__(self, parent=None):
        super(DatabaseEntryWidget, self).__init__(parent)

    @staticmethod
    def update_annotations(table_widget, annotations):
        """ Populate the table with the annotations

        Parameters
        ----------
        table_widget: QTableWidget
        annotations: annotation

        Returns
        -------

        """

        # Update table dimensions
        table_widget.setRowCount(len(annotations))
        table_widget.setColumnCount(2)

        # Add identifiers
        n = 0
        for annotation in annotations:
            table_widget.setItem(n, 0, QTableWidgetItem(annotation.collection))
            table_widget.setItem(n, 1, QTableWidgetItem(annotation.identifier))
            n += 1

        # Reset header items
        table_widget.setHorizontalHeaderLabels(["Resource", "ID"])

    @staticmethod
    def update_synonyms(list_widget, synonyms):
        """ Update the synonyms displayed

        Parameters
        ----------
        list_widget: QListWidget
        synonyms: iterable

        Returns
        -------

        """

        list_widget.clear()
        list_widget.addItems(synonyms)


class MetaboliteEntryDisplayWidget(DatabaseEntryWidget, Ui_MetaboliteEntryDisplayWidget):

    def __init__(self, parent=None):
        super(MetaboliteEntryDisplayWidget, self).__init__(parent)
        self.setupUi(self)

    def update_from_metabolite(self, metabolite, synonyms=()):
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
        self.update_labels(metabolite)

        # Update synonyms
        self.update_synonyms(self.list_synonyms, synonyms)

        # Update identifiers
        self.table_identifiers.populate_annotations(metabolite.annotation)

    @QtCore.pyqtSlot(int)
    def update_from_database_id(self, identifier):
        """ Update information from entry id

        Parameters
        ----------
        identifier: int

        Returns
        -------

        """
        self.setVisible(identifier >= 0)

        if identifier >= 0:
            # Get information
            with DatabaseWrapper() as database:
                # Get metabolite
                metabolite = database.get_metabolite_from_id(identifier)
                annotations = database.get_annotations_from_id(identifier, "Metabolite", get_all=True)
                synonyms = database.get_synonyms_from_id(identifier, "Metabolite")

            # Update display widgets
            self.update_labels(metabolite)
            self.table_identifiers.populate_annotations(annotations)
            self.update_synonyms(self.list_synonyms, synonyms)

    def update_labels(self, metabolite):
        """ Update labels from metabolite

        Parameters
        ----------
        metabolite: GEMEditor.cobraClasses.Metabolite

        Returns
        -------

        """
        self.label_name.setText(str(metabolite.name))
        self.label_charge.setText(str(metabolite.charge))
        self.label_formula.setText(str(metabolite.formula))


class ReactionEntryDisplayWidget(DatabaseEntryWidget, Ui_ReactionEntryDisplayWidget):

    def __init__(self, parent=None):
        super(ReactionEntryDisplayWidget, self).__init__(parent)
        self.setupUi(self)

        self.label_formula.setWordWrap(True)

    def update_from_reaction(self, reaction, synonyms):
        pass

    def update_from_database_id(self, identifier):
        """ Update information from entry id

        Parameters
        ----------
        identifier: int

        Returns
        -------

        """
        self.setVisible(identifier >= 0)

        if identifier >= 0:
            # Get information
            with DatabaseWrapper() as database:
                # Get metabolite
                participants = database.get_reaction_participants_from_id(identifier)
                annotations = database.get_annotations_from_id(identifier, "Reaction", get_all=True)
                synonyms = database.get_synonyms_from_id(identifier, "Reaction")

            # Generate reaction string
            base_str = "{stoichiometry} {name} ({compartment_id})"
            educts, products = [], []
            for element in sorted(participants, key=lambda x: x["name"]):
                content = dict(element)
                if content["stoichiometry"] < 0.:
                    content["stoichiometry"] = abs(content["stoichiometry"])
                    educts.append(base_str.format(**content))
                else:
                    products.append(base_str.format(**content))

            complete_string = " = ".join((" + ".join(educts), " + ".join(products)))

            # Update display widgets
            self.update_synonyms(self.list_synonyms, synonyms)
            self.table_identifiers.populate_annotations(annotations)
            self.label_formula.setText(complete_string)
            self.label_name.setText("Unknown")


def factory_entry_widget(data_type, parent):
    """ Factory for the database entry display widget

    Parameters
    ----------
    data_type: str
    parent: QWidget or None

    Returns
    -------

    """

    if data_type.lower() == "metabolite":
        return MetaboliteEntryDisplayWidget(parent)
    elif data_type.lower() == "reaction":
        return ReactionEntryDisplayWidget(parent)
    else:
        raise ValueError("Unexpected data_type '{0!s}'".format(data_type))


def pyqt_database_connection(database_path=None):
    """ Open the SQLITE database containing the MetaNetX mappings

    Returns
    -------
    db : QtSql.QSqlDatabase or None
    """

    # If not provided get database path from settings
    if database_path is None:
        database_path = DatabaseWrapper.get_database_path()

    # Check that SQLITE driver is installed
    if not QtSql.QSqlDatabase.isDriverAvailable('QSQLITE'):
        QMessageBox.critical(None, "Database driver missing!",
                                   "It appears that the sqlite database driver is missing.\n "
                                   "Please install it in order to use this function!",
                                   QMessageBox.Close)
        return

    # Check that the database is found
    if not os.path.isfile(database_path):
        QMessageBox.critical(None, "Database not found!",
                                   "The database has not been found at the expected location:"
                                   "\n{}".format(database_path),
                                   QMessageBox.Close)
        return

    # Set up database
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(database_path)
    db.setConnectOptions("QSQLITE_OPEN_READONLY=1")
    return db


if __name__ == '__main__':
    with DatabaseWrapper() as database:
        print(database.get_reaction_id_from_participant_ids([5, 6]))



