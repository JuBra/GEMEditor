import logging
import re
import json
from collections import defaultdict
from PyQt5.QtWidgets import QMessageBox, QApplication, QProgressDialog, QFileDialog
from PyQt5 import QtSql
from GEMEditor.database.create import get_database_connection
from GEMEditor.database.base import DatabaseWrapper
from GEMEditor.database.match import ManualMatchDialog
from GEMEditor.database.query import AnnotationSettingsDialog
from GEMEditor import formula_validator
from cobra import Metabolite


LOGGER = logging.getLogger(__name__)


def update_metabolite_database_mapping(model, progress, parent=None):
    """ Map all metabolites to database entries

    Parameters
    ----------
    model: GEMEditor.cobraClasses.Model
    progress: QProgressDialog
    parent: PyQt5.QtWidgets.QWidget

    Returns
    -------
    dict
    """

    LOGGER.debug("Updating metabolite to database mapping..")

    # Setup database connection
    database = DatabaseWrapper()

    # Update progress dialog
    progress.setLabelText("Mapping metabolites to database..")
    progress.setRange(0, len(model.metabolites))

    # Run the annotation
    for i, metabolite in enumerate(model.metabolites):
        if progress.wasCanceled() or metabolite in model.database_mapping:
            LOGGER.debug("Metabolite {0!s} skipped - Already mapped or progress cancelled.".format(metabolite))
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

        LOGGER.debug("Metabolite {0!s} mapped to {1!s}".format(metabolite,
                                                               model.database_mapping[metabolite]))

    # Close
    database.close()

    # Get unique mapping for multiple entries
    # Note: check for cobra Metabolite to avoid circular dependency
    ambiguous_matches = dict((k, v) for k, v in model.database_mapping.items()
                             if isinstance(v, list) and isinstance(k, Metabolite))

    # Manual match ambiguous items
    if not progress.wasCanceled() and ambiguous_matches:
        LOGGER.debug("There are ambiguously mapped metabolites")

        dialog = ManualMatchDialog(parent, unmatched_items=ambiguous_matches)
        dialog.exec_()

        # Add manually matched entries
        model.database_mapping.update(dialog.manual_mapped)


def update_reaction_database_mapping(model, progress, parent=None):
    """

    Parameters
    ----------
    model: GEMEditor.cobraClasses.Model
    progress: QProgressDialog
    parent

    Returns
    -------

    """

    LOGGER.debug("Updating reaction to database mapping..")

    with DatabaseWrapper() as database:

        # Ignore protons when matching reactions
        proton_entries = set()
        for mnx_id in ("MNXM01", "MNXM1"):
            ids = database.get_ids_from_annotation(identifier=mnx_id,
                                                   collection="metanetx.chemical")
            proton_entries.update(ids)

        # Update progress
        progress.setLabelText("Mapping reactions..")
        progress.setRange(0, len(model.reactions))

        # Match reactions
        for i, reaction in enumerate(model.reactions):
            if reaction.boundary or reaction in model.database_mapping or progress.wasCanceled():
                LOGGER.debug("Reaction {0!s} skipped - Boundary, "
                             "already mapped or progress cancelled.".format(reaction))
                continue

            # Update progress
            progress.setValue(i)
            QApplication.processEvents()

            # First try to map by annotation
            ids_from_annotation = set()
            for annotation in reaction.annotation:
                ids = database.get_ids_from_annotation(annotation.identifier,
                                                       annotation.collection)
                ids_from_annotation.update(ids)

            # Store mapping and skip mapping by database signature
            if ids_from_annotation:
                model.database_mapping[reaction] = list(ids_from_annotation)
                LOGGER.debug("Reaction {0!s} mapped to {1!s} by annotation".format(reaction, model.database_mapping[reaction]))
                continue

            # Store expected metabolite ids
            entry_signature = set()

            if any(m not in model.database_mapping for m in reaction.metabolites):
                # All elements must be mapped to the database
                LOGGER.debug("Not all metabolites in reaction {0!s} have been mapped to database".format(reaction))
                continue
            elif any(not isinstance(model.database_mapping[m], int) for m in reaction.metabolites):
                # All elements must be uniquely mapped to the database
                LOGGER.debug("Not all metabolites in reaction {0!s} have been mapped to a unique database entry".format(reaction))
                continue
            else:
                entry_signature.update(model.database_mapping[m] for m in reaction.metabolites)

            # Remove proton entries
            clean_signature = entry_signature - proton_entries

            # Get reaction database entries that match the signature
            common_reaction_ids = database.get_reaction_id_from_participant_ids(clean_signature)

            if not common_reaction_ids:
                # No reaction found that matches the current reaction
                LOGGER.debug("No reaction found in database containing all metabolites in reaction {0!s}".format(reaction))
                continue
            else:
                putative_matches = []

                for reaction_id in common_reaction_ids:
                    participants = database.get_reaction_participants_from_id(reaction_id)

                    reaction_signature = set([row["metabolite_id"] for row in participants if
                                              row["metabolite_id"] not in proton_entries])

                    if reaction_signature == clean_signature:
                        putative_matches.append(reaction_id)

                if not putative_matches:
                    LOGGER.debug("No corresponding reaction found in database for reaction {0!s}".format(reaction))
                    continue
                elif len(putative_matches) == 1:
                    model.database_mapping[reaction] = putative_matches[0]
                    LOGGER.debug("Reaction {0!s} mapped to {1!s}".format(reaction, model.database_mapping[reaction]))
                else:
                    model.database_mapping[reaction] = putative_matches
                    LOGGER.debug("Reaction {0!s} mapped to {1!s}".format(reaction, model.database_mapping[reaction]))


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

    LOGGER.debug("Running auto annotation..")

    # Check prerequisites
    if not model or progress.wasCanceled():
        return

    # Check that all metabolites have been mapped
    if any([m not in model.database_mapping for m in model.metabolites]):
        LOGGER.debug("There are unmapped metabolites. Running mapping..")
        update_metabolite_database_mapping(model, progress, parent)
        update_reaction_database_mapping(model, progress)

        # Return if user cancelled during mapping metabolites
        if progress.wasCanceled():
            LOGGER.debug("Mapping process cancelled by user. Auto annotation aborted.")
            return

    # Let the user which annotations to add and
    # which attributes to update from the database
    dialog = AnnotationSettingsDialog(parent)
    if not dialog.exec_():
        # Dialog cancelled by user
        LOGGER.debug("Auto annotation cancelled at annotation selection.")
        return

    # Get user choice
    settings = dialog.get_settings()

    # Make sure anything has been selected for update
    if not any(settings.values()):
        LOGGER.debug("Nothing has been selected for automatic annotation.")
        return

    # Keep track of updated metabolites in order to update corresponding reactions as well
    updates = {}

    # Run update of metabolites
    metabolite_updates = update_metabolites_from_database(model, progress,
                                                          update_names=settings["update_metabolite_name"],
                                                          update_formula=settings["formula_charge"])
    updates.update(metabolite_updates)

    # Run update reactions
    reaction_updates = update_reactions_from_database(model, progress)
    updates.update(reaction_updates)

    # Update tables - Only needed for those items with changed attributes
    model.gem_update_metabolites(updates["metabolite_attributes"], progress)
    model.gem_update_reactions(updates["reaction_attributes"], progress)

    return updates


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


def update_reactions_from_database(model, progress):
    """ Update the reaction annotations

    Use the mapping of the reactions to the database
    in order to retrieve missing annotations and
    update the names of the reactions

    Parameters
    ----------
    model: GEMEditor.cobraClasses.Model
    progress: QProgressDialog
    update_annotations: bool
    update_names: bool

    Returns
    -------
    dict
    """

    progress.setLabelText("Updating reactions..")
    progress.setRange(0, len(model.reactions))

    database = DatabaseWrapper()

    updates = {"reaction_annotations": set(),
               "reaction_attributes": set()}

    for i, reaction in enumerate(model.reactions):
        progress.setValue(i)
        QApplication.processEvents()

        # Check requirements
        if reaction not in model.database_mapping:
            continue  # Mapping not existent
        elif not isinstance(model.database_mapping[reaction], int):
            continue  # Mapping is non-unique
        else:
            entry_id = model.database_mapping[reaction]

        database_annotations = database.get_annotations_from_id(identifier=entry_id,
                                                                entry_type="reaction")

        new_annotations = set(database_annotations) - reaction.annotation
        if new_annotations:
            LOGGER.debug("New annotations for reaction {0!s} added: {1!s}".format(reaction,
                                                                                  ", ".join(str(x) for x in new_annotations)))
            reaction.annotation.update(database_annotations)
            updates["reaction_annotations"].add(reaction)

    return updates


def update_metabolites_from_database(model, progress, update_names=False, update_formula=False):
    """ Update the metabolite information from the database

    Parameters
    ----------
    model: GEMEditor.cobraClasses.Model
    progress: QProgressDialog
    update_names: bool
    update_formula: bool

    Returns
    -------
    dict
    """

    LOGGER.debug("Updating metabolites from database..")

    # Update progress dialog
    progress.setLabelText("Updating metabolites..")
    progress.setRange(0, len(model.metabolites))

    # Keep track of updates
    updates = {"metabolite_annotations": set(),
               "metabolite_attributes": set()}

    with DatabaseWrapper() as database:

        # Run annotation
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
                LOGGER.debug("Skipping metabolite {0!s} due to invalid mapping.".format(metabolite))
                continue

            # Update annotations from database
            annotations = set(database.get_annotations_from_id(entry_id,
                                                               "Metabolite"))
            if annotations - metabolite.annotation:
                # There are new annotations
                metabolite.annotation.update(annotations)
                updates["metabolite_annotations"].add(metabolite)

            entry_metabolite = database.get_metabolite_from_id(entry_id)

            # Update charge formula
            if update_formula:
                formula, charge = entry_metabolite.formula, entry_metabolite.charge

                if re.match(formula_validator, formula) and charge not in (None, ""):
                    if formula != metabolite.formula or charge != metabolite.charge:
                        metabolite.formula = formula
                        metabolite.charge = charge
                        updates["metabolite_attributes"].add(metabolite)

            # Update name
            if update_names and entry_metabolite.name != metabolite.name:
                metabolite.name = entry_metabolite.name
                updates["metabolite_attributes"].add(metabolite)

    return updates


def load_mapping(model, path):
    """ Load database mapping from file

    Parameters
    ----------
    model: GEMEditor.cobraClasses.Model

    Returns
    -------

    """

    # Abort if database mapping is wrong
    if not model or not path:
        return

    try:
        with open(path) as json_file:
            data = json.load(json_file)
        assert isinstance(data, dict)
    except Exception as e:
        QMessageBox().critical(None, "Error", "Error loading file. The file is not properly formatted!\n{}".format(str(e)))
    else:
        substituted = dict()
        for key, value in data.items():
            if key in model.metabolites:
                item = model.metabolites.get_by_id(key)
            elif key in model.reactions:
                item = model.reactions.get_by_id(key)
            else:
                continue

            substituted[item] = value

        model.database_mapping.update(substituted)
        QMessageBox().information(None, "Success", "Mapping loaded!")


def store_mapping(model, path):
    """ Dump the mapping to file

    Parameters
    ----------
    model: GEMEditor.cobraClasses.Model
    path: str

    Returns
    -------
    None
    """

    if not all((model, model.database_mapping, path)):
        return

    # Substitute database items for their id
    substituted = dict((key.id, value) for key, value in model.database_mapping.items())

    with open(path, "w") as open_file:
        open_file.write(json.dumps(substituted))
