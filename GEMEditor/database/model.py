import logging
import re
import json
from collections import defaultdict
from PyQt5.QtWidgets import QMessageBox, QApplication, QProgressDialog
from PyQt5 import QtSql
from GEMEditor.database.create import get_database_connection
from GEMEditor.database.base import DatabaseWrapper
from GEMEditor.database.match import ManualMatchDialog
from GEMEditor.database.query import AnnotationSettingsDialog
from GEMEditor import formula_validator
from GEMEditor.base.functions import unpack
from cobra import Metabolite


LOGGER = logging.getLogger(__name__)


def map_by_annotation(database, item):
    """ Map model item by annotation

    Parameters
    ----------
    database:   DatabaseWrapper
    item:       GEMEditor.model.classes.cobra.Metabolite or
                GEMEditor.model.classes.cobra.Reaction

    Returns
    -------
    entries
    """

    entries = set()
    for annotation in item.annotation:
        ids = database.get_ids_from_annotation(annotation.identifier,
                                               annotation.collection)
        entries.update(ids)
    return entries


def get_reactions_with_same_signature(database, entries, signature, ignored_ids):
    """ Get reactions from database that match signature

    Parameters
    ----------
    database: DatabaseWrapper
    entries: set, Containing the reaction ids to check for same signature
    signature: set, Containing metabolite entry ids of the metabolites in the reaction
    ignored_ids: set, Containing the metabolite entry ids to be ignored e.g. proton

    Returns
    -------
    set
    """
    matches = set()

    for reaction_id in entries:
        participants = database.get_reaction_participants_from_id(reaction_id)

        reaction_signature = set([row["metabolite_id"] for row in participants if
                                  row["metabolite_id"] not in ignored_ids])

        if reaction_signature == signature:
            matches.add(reaction_id)

    return matches


def check_ambiguous_mappings(model, parent):
    """ Allow user to manually map ambiguously mapped metabolites

    Parameters
    ----------
    model: GEMEditor.model.classes.cobra.Model
    parent: QWidget or None

    Returns
    -------
    None
    """

    # Get unique mapping for multiple entries
    # Note: check for cobra Metabolite to avoid circular dependency
    ambiguous_matches = dict((k, v) for k, v in model.database_mapping.items()
                             if isinstance(v, list) and isinstance(k, Metabolite))

    # Manual match ambiguous items
    if ambiguous_matches:
        LOGGER.debug("There are {0!s} ambiguously mapped metabolites".format(len(ambiguous_matches)))

        dialog = ManualMatchDialog(parent, unmatched_items=ambiguous_matches)
        dialog.exec_()

        # Add manually matched entries
        model.database_mapping.update(dialog.manual_mapped)


def update_metabolite_database_mapping(database, model, progress):
    """ Map all metabolites to database entries

    Parameters
    ----------
    database: DatabaseWrapper
    model: GEMEditor.model.classes.cobra.Model
    progress: QProgressDialog

    Returns
    -------
    dict
    """

    LOGGER.debug("Updating metabolite to database mapping..")

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
        if entries:
            model.database_mapping[metabolite] = unpack(entries, list)
        else:
            model.database_mapping[metabolite] = None

        LOGGER.debug("Metabolite {0!s} mapped to {1!s}".format(metabolite,
                                                               model.database_mapping[metabolite]))


def update_reaction_database_mapping(database, model, progress):
    """  Map reactions to the corresponding entry in the database

    1)  Use annotations to map to database
    2)  Refine annotation mapping or do initial mapping
        by stoichiometry

    Parameters
    ----------
    model: GEMEditor.model.classes.cobra.Model
    progress: QProgressDialog
    parent

    Returns
    -------

    """

    LOGGER.debug("Updating reaction to database mapping..")

    mapping = model.database_mapping

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
        if progress.wasCanceled():
            return
        elif reaction.boundary:
            LOGGER.debug("Skip boundary reaction {0!s}".format(reaction.id))
            continue
        elif reaction in mapping:
            LOGGER.debug("Skip already mapped reaction {0!s}".format(reaction.id))
            continue
        else:
            LOGGER.debug("Mapping reaction reaction {0!s}".format(reaction.id))
            progress.setValue(i)
            QApplication.processEvents()

        # First try to map by annotation
        entries_by_annotation = map_by_annotation(database, reaction)

        # Directly map if unique
        if len(entries_by_annotation) == 1:
            mapping[reaction] = entries_by_annotation.pop()
            LOGGER.debug("Mapped to {0!s} by annotation".format(mapping[reaction]))
            continue

        # Check if all metabolites are mapped
        all_mapped = all(m in mapping and isinstance(mapping[m], int) for m in reaction.metabolites)

        if not all_mapped:
            if entries_by_annotation:
                mapping[reaction] = unpack(entries_by_annotation, list)
                LOGGER.debug("Mapped to {0!s} by annotation".format(mapping[reaction]))
            else:
                LOGGER.debug("No match found by annotation and stoichiometry")
            continue

        # Store expected metabolite ids
        metabolite_mapping = set(mapping[m] for m in reaction.metabolites)

        # Remove proton entries
        clean_signature = metabolite_mapping - proton_entries

        # Get reaction database entries that match the signature
        common_ids = database.get_reaction_id_from_participant_ids(clean_signature)
        entries_by_signature = get_reactions_with_same_signature(database, common_ids,
                                                                 clean_signature, proton_entries)

        # Find entries that match metabolites and annotations
        overlap = entries_by_signature.intersection(entries_by_annotation)

        if overlap:
            mapping[reaction] = unpack(overlap, list)
            LOGGER.debug("Mapped to {0!s} by annotation and stoichiometry".format(mapping[reaction]))
        elif entries_by_signature or entries_by_annotation:
            combination = entries_by_annotation.union(entries_by_signature)
            mapping[reaction] = unpack(combination, list)
            if entries_by_signature:
                LOGGER.debug("Mapped to {0!s} by stoichiometry".format(entries_by_signature))
            if entries_by_annotation:
                LOGGER.debug("Mapped to {0!s} by annotation".format(entries_by_annotation))
        else:
            LOGGER.debug("No match by stoichiometry or annotations.")


def run_auto_annotation(database, model, progress, parent):
    """ Run the auto annotation using the MetaNetX database

    Parameters
    ----------
    model : GEMEditor.model.classes.cobra.Model
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
        update_metabolite_database_mapping(database, model, progress)
        update_reaction_database_mapping(database, model, progress)

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
    model : GEMEditor.model.classes.cobra.Model
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
    model: GEMEditor.model.classes.cobra.Model
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
    model: GEMEditor.model.classes.cobra.Model
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


def run_database_mapping(database, model, progress):
    # Update metabolites
    update_metabolite_database_mapping(database, model, progress)
    check_ambiguous_mappings(model, None)
    update_reaction_database_mapping(database, model, progress)


def load_mapping(model, path):
    """ Load database mapping from file

    Parameters
    ----------
    model: GEMEditor.model.classes.cobra.Model

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
    model: GEMEditor.model.classes.cobra.Model
    path: str

    Returns
    -------
    None
    """

    if not all((model, model.database_mapping, path)):
        return

    # Substitute database items for their id
    substituted = dict((key.id, value) for key, value in
                       model.database_mapping.items() if isinstance(value, int))

    with open(path, "w") as open_file:
        open_file.write(json.dumps(substituted))
