import logging
import re
from collections import defaultdict
from PyQt5.QtWidgets import QMessageBox, QApplication, QProgressDialog, QDialogButtonBox
from PyQt5 import QtSql
from GEMEditor.database.create import create_database_de_novo, get_database_connection
from GEMEditor.database.base import DatabaseWrapper
from GEMEditor.database.match import ManualMatchDialog
from GEMEditor.database.query import AnnotationSettingsDialog
from GEMEditor.base.functions import invert_mapping, get_annotation_to_item_map, generate_copy_id
from GEMEditor import formula_validator


def get_metabolite_to_entry_mapping(model, progress, parent=None):
    """ Map all metabolites to database entries

    Parameters
    ----------
    model: GEMEditor.cobraClasses.Model
    progress: QProgressDialog

    Returns
    -------
    dict
    """

    # Resulting metabolite to database mapping
    mapping = dict()

    # Setup database connection
    database = DatabaseWrapper()

    # Update progress dialog
    progress.setLabelText("Mapping metabolites to database..")
    progress.setRange(0, len(model.metabolites))

    # Run the annotation
    for i, metabolite in enumerate(model.metabolites):
        if progress.wasCanceled():
            # Map all remaining items to None
            mapping[metabolite] = None
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
            mapping[metabolite] = entries.pop()
        elif len(entries) > 1:
            mapping[metabolite] = list(entries)
        else:
            mapping[metabolite] = None

    # Close
    database.close()

    # Get unique mapping for multiple entries
    ambiguous_matches = dict(item for item in mapping.items() if isinstance(item[1], list))

    # Manual match ambiguous items
    if not progress.wasCanceled() and ambiguous_matches:
        dialog = ManualMatchDialog(parent, unmatched_items=ambiguous_matches)
        dialog.exec_()

        # Add manually matched entries
        mapping.update(dialog.manual_mapped)

    return mapping


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

    """

    # Mapping metabolites to database entries
    metabolite_database_mapping = get_metabolite_to_entry_mapping(model, progress, parent)

    # Shortcut if process cancelled by user
    if progress.wasCanceled():
        return

    # Set mapping to model
    model.database_mapping = metabolite_database_mapping

    # Get possible resources
    database = DatabaseWrapper()
    metabolite_resources = database.get_miriam_collections()
    reaction_resources = database.get_miriam_collections(type="reaction")

    # Generate display name to miriam collection mapping
    metabolite_mapping = dict((row['name'], row['miriam_collection']) for row in metabolite_resources)
    reaction_mapping = dict((row['name'], row['miriam_collection']) for row in reaction_resources)

    # Let the user which annotations to add and which attributes to update from the database
    dialog = AnnotationSettingsDialog(metabolite_mapping, reaction_mapping, parent)
    if not dialog.exec_():
        # Cancelled by user
        database.close()
        return

    # Get user choice
    settings = dialog.get_settings()

    # Make sure anything has been selected for update
    if not any(settings.values()):
        database.close()
        return

    progress.setLabelText("Updating metabolites..")
    progress.setRange(0, len(model.metabolites))

    # Keep track of updated metabolites in order to update corresponding reactions as well
    updated_metabolites = []
    # Keep track of reactions that need to be updated
    update_reactions = set()

    for row, metabolite in enumerate(model.QtMetaboliteTable.get_items()):
        if progress.wasCanceled():
            break
        progress.setValue(row)
        QApplication.processEvents()

        entry = metabolite_database_mapping[metabolite]
        if entry is None:
            # No entry found in database for metabolite
            continue
        elif isinstance(entry, int):
            # Metabolite has been mapped to a database entry
            annotations = database.get_annotations_from_id(entry, "Metabolite")

            # Only add the annotations for the databases that have been selected by the user
            filtered_annotations = [x for x in annotations if x.collection in settings["metabolite_resources"]]
            metabolite.annotation.update(filtered_annotations)

        # Update charge formula
        if settings["formula"] or settings["charge"]:
            entry_metabolite = database.get_metabolite_from_id(entry)
            formula, charge = entry_metabolite.formula, entry_metabolite.charge

            if settings["formula"] and formula and re.match(formula_validator, formula):
                metabolite.formula = formula
            if settings["charge"] and charge not in (None, ""):
                metabolite.charge = charge

            updated_metabolites.append((row, metabolite))
            update_reactions.update(metabolite.reactions)

    # Update metabolite table entries
    progress.setLabelText("Updating metabolite table..")
    progress.setRange(0, len(updated_metabolites))
    model.QtMetaboliteTable.blockSignals(True)

    for i, row_met_tuple in enumerate(updated_metabolites):
        progress.setValue(i)
        QApplication.processEvents()
        row, metabolite = row_met_tuple
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

    database.close()


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
