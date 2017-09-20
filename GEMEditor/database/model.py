import os
import sqlite3
import logging
import re
from collections import defaultdict
from GEMEditor.database import database_path
from PyQt5.QtWidgets import QMessageBox, QDialogButtonBox, QDialog, QVBoxLayout, QCheckBox, QApplication, QProgressDialog
from PyQt5 import QtSql
from GEMEditor.database.create import create_database_de_novo, get_database_connection
from GEMEditor.database.query import DatabaseWrapper
from GEMEditor.database.ui import Ui_AnnotationSettingsDialog
from GEMEditor.cobraClasses import Reaction, Metabolite
from GEMEditor.data_classes import Annotation
from GEMEditor import formula_validator


class AnnotationSettingsDialog(QDialog, Ui_AnnotationSettingsDialog):

    def __init__(self, metabolite_resources, reaction_resources, parent=None):
        """ Setup the dialog
        
        Parameters
        ----------
        reaction_resources: dict - Mapping {resource_name: resource_id}
        metabolite_resources: dict - Mapping {resource_name: resource_id}
        parent: 
        """

        super(AnnotationSettingsDialog, self).__init__(parent)
        self.setupUi(self)
        self.metabolite_resources = metabolite_resources
        self.reaction_resources = reaction_resources

        self.metabolite_checkboxes = []
        self.reaction_checkboxes = []

        self.setup_options()

    def setup_options(self):
        # Setup metabolite options
        layout = QVBoxLayout(self)
        for element in sorted(self.metabolite_resources.keys()):
            checkbox = QCheckBox(element, self)
            layout.addWidget(checkbox)
            self.metabolite_checkboxes.append(checkbox)
        self.groupBox_met_annotation.setLayout(layout)

        # Setup reaction options
        layout = QVBoxLayout(self)
        for element in sorted(self.reaction_resources.keys()):
            checkbox = QCheckBox(element, self)
            layout.addWidget(checkbox)
            self.reaction_checkboxes.append(checkbox)
        self.groupBox_react_annotation.setLayout(layout)

    def get_settings(self):
        settings = dict()
        settings["formula"] = self.checkBox_formula.isChecked()
        settings["charge"] = self.checkBox_charge.isChecked()
        settings["reaction_resources"] = [self.reaction_resources[x.text()] for x in self.reaction_checkboxes
                                            if x.isChecked()]
        settings["metabolite_resources"] = [self.metabolite_resources[x.text()] for x in self.metabolite_checkboxes
                                              if x.isChecked()]
        return settings


def get_pyqt_database(parent=None):

    if not QtSql.QSqlDatabase.isDriverAvailable('QSQLITE'):
        QMessageBox.critical(None, "Database driver missing!",
                                   "It appears that the sqlite database driver is missing.\n "
                                   "Please install it in order to use this function!",
                                   QMessageBox.Close)
        return

    if not os.path.isfile(database_path):
        response = QMessageBox().question(None, "Database not found.", "No database found. Would you like to setup a new one?")
        if not response:
            # User does not want to setup
            return
        elif not create_database_de_novo(parent):
            # Database not created successfully
            return

    # Set up database
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(database_path)
    db.setConnectOptions("QSQLITE_OPEN_READONLY=1")
    return db


def get_annotation_entries(cursor, id, entry_type):
    """ Get all annotations for a database item
    
    Parameters
    ----------
    conn
    id
    type

    Returns
    -------

    """
    if entry_type == "Metabolite":
        cursor.execute("SELECT resource_id, identifier FROM metabolite_ids WHERE metabolite_id=?;", (id,))
    elif entry_type == "Reaction":
        cursor.execute("SELECT resource_id, identifier FROM reaction_ids WHERE reaction_id=?;", (id,))
    else:
        raise ValueError("Unknown entry_type '{}'".format(str(entry_type)))
    return cursor.fetchall()


def get_model_object_attributes(cursor, id, class_name):
    """ Get attribute information from database
    
    Parameters
    ----------
    cursor
    id
    entry_type

    Returns
    -------

    """
    if class_name == "Metabolite":
        cursor.execute("SELECT name, formula, charge FROM metabolites WHERE id=?", (id,))
        entry = cursor.fetchone()
        if entry:
            return {"name": entry[0] or None,
                    "formula": entry[1] or None,
                    "charge": int(entry[2]) if entry[2] else None}
        return {}
    else:
        raise ValueError("Unknown class name '{}'.".format(str(class_name)))


def get_model_object_from_id(cursor, id, cls):
    """ Get a model item from a database id
    
    Parameters
    ----------
    cursor
    id
    cls

    Returns
    -------

    """
    return cls(**get_model_object_attributes(cursor, id, cls.__name__))


def get_metabolite_to_entry_mapping(model, parent=None):
    """ Map all metabolites to database entries

    Parameters
    ----------
    model: GEMEditor.cobraClasses.Model

    Returns
    -------
    dict
    """

    # Resulting metabolite to database mapping
    mapping = dict()

    # Setup database connection
    database = DatabaseWrapper()

    # Set up the progress dialog
    progress = QProgressDialog(parent)
    progress.setMinimumDuration(0.5)
    progress.setWindowTitle("Updating annotations..")
    progress.setLabelText("Updating metabolites..")
    progress.setRange(0, len(model.metabolites))
    QApplication.processEvents()

    # Run the annotation
    for i, metabolite in enumerate(model.metabolites):
        if progress.wasCanceled():
            # Map all remaining items to None
            mapping[metabolite] = None
            continue

        progress.setValue(i)
        QApplication.processEvents()

        # Database entries that the metabolite maps to
        entries = set()

        # Find matches from annotations
        for annotation in metabolite.annotation:
            entries.update(database.get_ids_from_annotation(identifier=annotation.identifier,
                                                            collection=annotation.collection))

        # Metabolite has not been matched by annotation
        if not entries and metabolite.name:
            entries.update(database.get_ids_from_name(name=metabolite.name,
                                                      entry_type="Metabolite"))

        # Find matches by formula
        if not entries and metabolite.formula:
            entries.update(database.get_ids_from_formula(formula=metabolite.formula))

        # Add found entries to mapping
        if len(entries) == 1:
            mapping[metabolite] = entries.pop()
        elif len(entries) > 1:
            mapping[metabolite] = list(entries)
        else:
            mapping[metabolite] = None

    # Close connection
    database.close()

    return mapping


def run_auto_annotation(model, parent):
    """ Run the auto annotation using the MetaNetX database

    Parameters
    ----------
    model : GEMEditor.cobraClasses.Model
    parent : GEMEditor.main.MainWindow

    Returns
    -------

    """

    connection = get_database_connection()

    if connection is None:
        # Database not found
        response = QMessageBox().question(parent, "Database not found!",
                                          "The database necessary for this action has not been found. "
                                          "Would you like to download the files and setup the database now?")
        if response == QDialogButtonBox.No:
            return False
        elif response == QDialogButtonBox.Yes and create_database_de_novo(parent):
            connection = get_database_connection()
            if connection is None:
                return False
        else:
            return False

    # Select which parts to update
    cursor = connection.cursor()
    cursor.execute("SELECT name, id FROM resources WHERE type=?;", ("reaction",))
    reaction_resources = dict(tuple(x) for x in cursor.fetchall())
    cursor.execute("SELECT name, id FROM resources WHERE type=?;", ("metabolite",))
    metabolite_resources = dict(tuple(x) for x in cursor.fetchall())
    cursor.execute("SELECT id, miriam_collection FROM resources WHERE type=?;", ("metabolite",))
    resource_miriam_map = dict(tuple(x) for x in cursor.fetchall())
    miriam_resource_map = dict((v, k) for k, v in resource_miriam_map.items())

    # Get settings
    dialog = AnnotationSettingsDialog(metabolite_resources, reaction_resources)
    if not dialog.exec_():
        # Cancelled by user
        return
    else:
        settings = dialog.get_settings()

    # Make sure anything has been selected for update
    if not any(settings.values()):
        return

    # Setup progress
    progress = QProgressDialog(parent)
    progress.setMinimumDuration(0.5)
    progress.setWindowTitle("Updating annotations..")
    progress.setLabelText("Updating metabolites..")
    progress.setRange(0, len(model.metabolites))
    QApplication.processEvents()

    # Keep track of updated metabolites in order to update corresponding reactions as well
    updated_metabolites = []

    for row, metabolite in enumerate(model.QtMetaboliteTable.get_items()):
        if progress.wasCanceled():
            break
        progress.setValue(row)
        QApplication.processEvents()

        # Map metabolite to database via an existing annotation
        metabolite_db_id = None
        for annotation in metabolite.annotation:
            cursor.execute("SELECT metabolite_id FROM metabolite_ids WHERE resource_id=? AND identifier=?;",
                           (miriam_resource_map[annotation.collection], annotation.identifier))
            result = cursor.fetchone()
            if result:
                metabolite_db_id = result[0]
                break

        # Metabolite has not been mapped by annotation
        if metabolite_db_id is None:
            # Try mapping database entry by attributes
            name_hits, formula_hits = set(), set()
            if metabolite.name:
                cursor.execute("SELECT metabolite_id FROM metabolite_names WHERE name=? COLLATE NOCASE;",
                               (metabolite.name,))
                name_hits.update([x[0] for x in cursor.fetchall()])

            # Unique hit based on the name
            if len(name_hits) == 1:
                metabolite_db_id = name_hits.pop()

            # No unique name, try to narrow down based on formula
            elif len(name_hits) > 1 and metabolite.formula:
                cursor.execute("SELECT id FROM metabolites WHERE formula=?", (metabolite.formula,))
                formula_hits.update([x[0] for x in cursor.fetchall()])
                intersection = name_hits.intersection(formula_hits)
                if len(intersection) == 1:
                    metabolite_db_id = intersection.pop()
                else:
                    logging.warning("Multiple entries for metabolite!")

        # Unique metabolite id found
        if metabolite_db_id is None:
            continue

        # Get annotation entries
        annotation_entries = get_annotation_entries(cursor, metabolite_db_id, "Metabolite")
        if not annotation_entries:
            continue

        annotations = set()
        selected_resources = set(settings["metabolite_resources"])
        for entry in annotation_entries:
            resource_id, identifier = entry
            if resource_id in selected_resources and resource_miriam_map[resource_id]:
                annotations.add(Annotation(collection=resource_miriam_map[resource_id],
                                           identifier=identifier))
        # Update annotations
        metabolite.annotation.update(annotations)

        # Update charge formula
        if settings["formula"] or settings["charge"]:
            cursor.execute("SELECT formula, charge FROM metabolites WHERE id=?", (metabolite_db_id,))
            formula, charge = cursor.fetchone()

            if settings["formula"] and formula and re.match(formula_validator, formula):
                metabolite.formula = formula
            if settings["charge"] and charge not in (None, ""):
                metabolite.charge = charge
            updated_metabolites.append((row, metabolite))

    # Keep track of reactions that need to be updated
    update_reactions = set()

    # Update metabolite table entries
    progress.setLabelText("Updating metabolite table..")
    progress.setRange(0, len(updated_metabolites))
    model.QtMetaboliteTable.blockSignals(True)

    for i, row_met_tuple in enumerate(updated_metabolites):
        progress.setValue(i)
        QApplication.processEvents()
        row, metabolite = row_met_tuple
        update_reactions.update(metabolite.reactions)
        model.QtMetaboliteTable.update_row_from_item(metabolite, row)
    model.QtMetaboliteTable.blockSignals(False)
    model.QtMetaboliteTable.all_data_changed()

    # Map reactions to row
    reaction_row_map = dict((reaction, i) for i, reaction in enumerate(model.QtReactionTable.get_items()))

    # Set progress dialog
    progress.setLabelText("Updating reaction table..")
    progress.setRange(0, len(update_reactions))

    # Update reactions
    model.QtReactionTable.blockSignals(True)
    for i, reaction in enumerate(update_reactions):
        progress.setValue(i)
        QApplication.processEvents()
        reaction.update_balancing_status()
        model.QtReactionTable.update_row_from_item(reaction, reaction_row_map[reaction])
    model.QtReactionTable.blockSignals(False)
    model.QtReactionTable.all_data_changed()

    progress.close()


def run_check_consistency(model, parent):
    """ Check that all annotations point to the same database item

    Parameters
    ----------
    model : GEMEditor.cobraClasses.Model
    database : QtSql.QSqlDatabase
    progress : QProgressDialog

    Returns
    -------

    """
    errors = []

    # Check if database could be opened without errors
    connection = get_database_connection()
    if not connection:
        QMessageBox().critical(None, "Database error", "The database has not been found. Please set it up first!")
        return

    # Update progress dialog
    progress = QProgressDialog(parent)
    progress.setWindowTitle("Checking annotations..")
    progress.setLabelText("Checking metabolites..")
    progress.setMinimumDuration(0)
    QApplication.processEvents()

    # Setup cursor
    cursor = connection.cursor()

    # Map miriam collections to database resource ids
    cursor.execute("SELECT id, miriam_collection FROM resources;")
    resource_map = dict((result[1], result[0]) for result in cursor.fetchall())

    progress.setRange(0, len(model.metabolites))
    for i, metabolite in enumerate(model.metabolites):
        progress.setValue(i)
        QApplication.processEvents()

        mapped_items = defaultdict(set)
        for annotation in metabolite.annotation:
            cursor.execute("SELECT metabolite_id FROM metabolite_ids WHERE resource_id=? AND identifier=?;", (resource_map[annotation.collection],
                                                                                                              annotation.identifier))
            results = cursor.fetchall()

            # Add mapping to database item
            for entry in results:
                mapped_items[entry[0]].add(annotation)

            # Keep track of unmapped annotations
            if not results:
                mapped_items[None].add(annotation)

        # Skip the evaluation if there are no annotations
        if not metabolite.annotation:
            continue

        # Check if there is any database item to which all annotations that are found
        # in the database point. If that is the case set mapping_ok to True
        mapping_ok = False

        # Check for None in order to avoid changing the dictionary during iteration
        if None not in mapped_items:
            mapping_ok = any(x == metabolite.annotation for x in mapped_items.values())
        else:
            for x in mapped_items.values():
                # Test if one mapped metabolite together with the items without annotation
                # explains all items
                if x.union(mapped_items[None]) == metabolite.annotation:
                    mapping_ok = True
                    break

        # If no common database item is found for all annotations that are within the database
        # add the error information to errors
        if not mapping_ok:
            errors.append("There is an error with the annotation in {}".format(metabolite.id))

    # Clean up
    cursor.close()
    connection.close()
    progress.close()

    return errors


def find_metabolite_name(resource_map, name_query, annotation_query, metabolite):
    """ Find the metabolite id in the database and load annotations

    Parameters
    ----------
    resource_map : dict - Mapping resource ids to miriam collectioins
    database : QtSql.QSqlDatabase
    metabolite_id : GEMEditor.cobraClasses.Metabolite

    Returns
    -------
    annotation: set
    """

    name_query.bindValue(":name", metabolite.name)
    name_query.exec_()

    metabolite_ids = set()
    while name_query.next():
        metabolite_ids.add(name_query.value(0))

    annotations = set()
    if not metabolite_ids:
        print("No id found for {}".format(metabolite.id))
        return annotations

    for metabolite_id in metabolite_ids:
        annotation_query.bindValue(":id", metabolite_id)
        annotation_query.exec_()

        while annotation_query.next():
            collection = resource_map[annotation_query.value(0)]
            identifier = annotation_query.value(1)
            annotations.add(Annotation(collection, identifier))

    return annotations


if __name__ == '__main__':
    app = QApplication([])
    con = sqlite3.connect(database_path)
    cursor = con.cursor()
    result = get_model_object_from_id(cursor, 5, Metabolite)
    print(result.name, result.id, result.charge)
