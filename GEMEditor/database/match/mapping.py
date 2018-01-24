import logging
from PyQt5 import QtCore
from GEMEditor.database.base import DatabaseWrapper
from GEMEditor.base import ProgressSignals, unpack


LOGGER = logging.getLogger(__name__)


class Mapper(QtCore.QRunnable):
    """ Base class for runnables mapping
    model items to the MetaNetX database
    """

    mapping_updated = QtCore.pyqtSignal(dict)

    def __init__(self, items, existing_mapping):
        super(Mapper, self).__init__()
        self.progress = ProgressSignals()

        self._items = items
        self._existing_mapping = existing_mapping
        self._new_mapping = dict()


class MetaboliteMapper(Mapper):

    def __init__(self, items, existing_mapping):
        super(MetaboliteMapper, self).__init__(items, existing_mapping)

    def run(self):
        LOGGER.debug("Running metabolite mapping.")

        with DatabaseWrapper() as database:

            for metabolite in self._items:
                # Check cancellation
                if self.progress.was_canceled:
                    break
                else:
                    self.progress.increment()

                if metabolite in self._existing_mapping:
                    LOGGER.debug("Metabolite {0!s} was already mapped.".format(metabolite))
                    continue

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
                    self._new_mapping[metabolite] = unpack(entries, list)
                else:
                    self._new_mapping[metabolite] = None

                LOGGER.debug("Metabolite {0!s} mapped to {1!s}".format(metabolite, self._new_mapping[metabolite]))

            else:
                self.mapping_updated.emit(self._new_mapping)


class ReactionMapper(Mapper):

    def __init__(self, items, existing_mapping):
        super(ReactionMapper, self).__init__(items, existing_mapping)

    def run(self):
        LOGGER.debug("Running reaction mapping.")

        with DatabaseWrapper() as database:

            # Ignore protons when matching reactions
            proton_entries = set()
            for mnx_id in ("MNXM01", "MNXM1"):
                ids = database.get_ids_from_annotation(identifier=mnx_id,
                                                       collection="metanetx.chemical")
                proton_entries.update(ids)

            # Match reactions
            for reaction in self._items:

                if self.progress.was_canceled:
                    break
                elif reaction.boundary:
                    LOGGER.debug("Boundary reaction {0!s} skipped".format(reaction.id))
                    continue
                elif reaction in self._existing_mapping:
                    LOGGER.debug("Reaction {0!s} was already mapped.".format(reaction.id))
                    continue
                else:
                    self.progress.increment()

                # Map by annotation
                entries = map_by_annotation(database, reaction)

                # Directly map if unique
                if not entries:
                    # No match found
                    pass
                elif len(entries) > 1 and all_metabolites_mapped(self._existing_mapping, reaction):
                    # Can potentially be narrowed down by connectivity
                    pass
                else:
                    self._new_mapping[reaction] = unpack(entries, list)
                    LOGGER.debug("Reaction {0!s} mapped by annotation".format(reaction))
                    continue

                # Store expected metabolite ids
                metabolite_mapping = set(self._existing_mapping[m] for m in reaction.metabolites)

                # Remove proton entries
                signature = metabolite_mapping - proton_entries

                # Get reaction database entries that match the signature
                reaction_ids = database.get_reaction_id_from_participant_ids(signature)
                entries_by_signature = filter_same_signature(database, reaction_ids,
                                                             signature, proton_entries)

                # Find entries that match metabolites and annotations
                overlap = entries_by_signature.intersection(entries)

                if overlap:
                    self._new_mapping[reaction] = unpack(overlap, list)
                    LOGGER.debug("Reaction {0!s} mapped by annotation and stoichiometry".format(reaction))
                elif entries or entries_by_signature:
                    combination = entries.union(entries_by_signature)
                    self._new_mapping[reaction] = unpack(combination, list)
                    LOGGER.debug("Reaction {0!s} mapped by annotation or stoichiometry".format(reaction))
                else:
                    LOGGER.debug("No match found for reaction {0!s}".format(reaction))
            else:
                self.mapping_updated.emit(self._new_mapping)


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


def all_metabolites_mapped(mapping, reaction):
    return all(m in mapping and isinstance(mapping[m], int)
               for m in reaction.metabolites)


def filter_same_signature(database, entries, signature, ignored_ids):
    """ Get reactions from database that match signature

    Parameters
    ----------
    database: DatabaseWrapper
    entries: set,
        Containing the reaction ids to check for same signature
    signature: set,
        Containing metabolite entry ids of the metabolites in the reaction
    ignored_ids: set,
        Containing the metabolite entry ids to be ignored e.g. proton

    Returns
    -------
    matches: set
    """
    matches = set()

    for reaction_id in entries:
        participants = database.get_reaction_participants_from_id(reaction_id)

        reaction_signature = set([row["metabolite_id"] for row in participants if
                                  row["metabolite_id"] not in ignored_ids])

        if reaction_signature == signature:
            matches.add(reaction_id)

    return matches
