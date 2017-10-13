import logging
import re
from collections import defaultdict
from PyQt5.QtWidgets import QMessageBox, QApplication, QProgressDialog
from PyQt5 import QtSql
from GEMEditor.database.create import get_database_connection
from GEMEditor.database.base import DatabaseWrapper
from GEMEditor.database.match import ManualMatchDialog
from GEMEditor.database.query import AnnotationSettingsDialog
from GEMEditor import formula_validator


def update_metabolite_database_mapping(model, progress, parent=None):
    """ Map all metabolites to database entries

    Parameters
    ----------
    model: GEMEditor.cobraClasses.Model
    progress: QProgressDialog

    Returns
    -------
    dict
    """

    # Setup database connection
    database = DatabaseWrapper()

    # Update progress dialog
    progress.setLabelText("Mapping metabolites to database..")
    progress.setRange(0, len(model.metabolites))

    # Run the annotation
    for i, metabolite in enumerate(model.metabolites):
        if progress.wasCanceled() or metabolite in model.database_mapping:
            continue

        # Update progress if not cancelled
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
            model.database_mapping[metabolite] = entries.pop()
        elif len(entries) > 1:
            model.database_mapping[metabolite] = list(entries)
        else:
            model.database_mapping[metabolite] = None

    # Close
    database.close()

    # Get unique mapping for multiple entries
    ambiguous_matches = dict(item for item in model.database_mapping.items()
                             if isinstance(item[1], list))

    # Manual match ambiguous items
    if not progress.wasCanceled() and ambiguous_matches:
        dialog = ManualMatchDialog(parent, unmatched_items=ambiguous_matches)
        dialog.exec_()

        # Add manually matched entries
        model.database_mapping.update(dialog.manual_mapped)


def get_reaction_to_entry_mapping(metabolite_to_db_mapping, progress, parent=None):
    pass


def run_auto_annotation(model, progress, parent):
    """ Run the auto annotation using the MetaNetX database

    Parameters
    ----------
    model : GEMEditor.cobraClasses.Model
    progress: QProgressDialog
    parent : GEMEditor.main.MainWindow

    Returns
    -------
    list
    """

    # Check prerequisites
    if not model or progress.wasCanceled():
        return

    # Check that all metabolites have been mapped
    if any([m not in model.database_mapping for m in model.metabolites]):
        update_metabolite_database_mapping(model, progress, parent)

        # Return if user cancelled during mapping metabolites
        if progress.wasCanceled():
            return

    # Let the user which annotations to add and
    # which attributes to update from the database
    dialog = AnnotationSettingsDialog(parent)
    if not dialog.exec_():
        # Dialog cancelled by user
        return

    # Get user choice
    settings = dialog.get_settings()

    # Make sure anything has been selected for update
    if not any(settings.values()):
        return

    # Keep track of updated metabolites in order to update corresponding reactions as well
    updated_metabolites = {"annotations": set(),
                           "others": set()}

    # Update progress dialog
    progress.setLabelText("Updating metabolites..")
    progress.setRange(0, len(model.metabolites))

    # Run annotation
    database = DatabaseWrapper()

    for i, metabolite in enumerate(model.metabolites):
        if progress.wasCanceled():
            break
        else:
            progress.setValue(i)
        QApplication.processEvents()

        # Get database id from mapping
        entry_id = model.database_mapping[metabolite]
        if not isinstance(entry_id, int):
            # No entry found in database for metabolite
            continue

        # Update annotations from database
        annotations = set(database.get_annotations_from_id(entry_id,
                                                           "Metabolite"))
        if annotations - metabolite.annotation:
            # There are new annotations
            metabolite.annotation.update(annotations)
            updated_metabolites["annotations"].add(metabolite)

        entry_metabolite = database.get_metabolite_from_id(entry_id)

        # Update charge formula
        if settings["formula_charge"]:
            formula, charge = entry_metabolite.formula, entry_metabolite.charge

            if re.match(formula_validator, formula) and charge not in (None, ""):
                if formula != metabolite.formula or charge != metabolite.charge:
                    metabolite.formula = formula
                    metabolite.charge = charge
                    updated_metabolites["others"].add(metabolite)

        # Update name
        if settings["update_metabolite_name"] and entry_metabolite.name != metabolite.name:
            metabolite.name = entry_metabolite.name
            updated_metabolites["others"].add(metabolite)

    database.close()

    # Update tables
    model.gem_update_metabolites(updated_metabolites["others"], progress)

    return updated_metabolites["annotations"].union(updated_metabolites["others"])


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


