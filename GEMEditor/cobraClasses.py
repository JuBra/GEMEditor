import logging
from cobra.core import Reaction as cobraReaction
from cobra.core import Gene as cobraGene
from cobra.core import Metabolite as cobraMetabolite
from cobra.core import Model as cobraModel
from weakref import WeakValueDictionary
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from GEMEditor.base.functions import generate_copy_id
from GEMEditor.base.classes import WindowManager
from GEMEditor.widgets.tables import ReactionTable, MetaboliteTable, GeneTable, ReferenceTable, ModelTestTable, LinkedItem, CompartmentTable
from GEMEditor.data_classes import ReactionSetting, CleaningDict, Compartment
from GEMEditor.base_classes import EvidenceLink
from GEMEditor.base.functions import reaction_balance
from six import string_types
from difflib import SequenceMatcher
import uuid


LOGGER = logging.getLogger(__name__)


class BaseTreeElement:

    def __init__(self):
        self._children = []
        self._parents = []
        super(BaseTreeElement, self).__init__()

    def _add_child(self, child):
        self._children.append(child)

    def _remove_child(self, child, all=False):
        if all:
            self._children[:] = [x for x in self._children if x is not child]
        else:
            self._children.remove(child)

    def _add_parent(self, parent):
        self._parents.append(parent)

    def _remove_parent(self, parent, all=False):
        if all:
            self._parents[:] = [x for x in self._parents if x is not parent]
        else:
            self._parents.remove(parent)

    def add_child(self, child):
        self._add_child(child)
        child._add_parent(self)

    def remove_child(self, child, all=False):
        self._remove_child(child, all=all)
        child._remove_parent(self, all=all)

    def add_parent(self, parent):
        self._add_parent(parent)
        parent._add_child(self)

    def remove_parent(self, parent, all=False):
        self._remove_parent(parent, all=all)
        parent._remove_child(self, all=all)

    @property
    def genes(self):
        gene_set = set()
        for x in self._children:
            gene_set.update(x.genes)
        return gene_set

    @property
    def reactions(self):
        reaction_set = set()
        for x in self._parents:
            reaction_set.update(x.reactions)
        return reaction_set

    def delete_children(self, parent=None):
        for x in self._children:
            x.delete_children(self)
        self._children[:] = []
        if parent is not None:
            self._parents[:] = [x for x in self._parents if x is not parent]

    def prepare_deletion(self):
        """ Prepare the deletion of the object from the model.

        Unlink all parents and children"""

        # Delete all parents
        for parent in set(self._parents):
            self.remove_parent(parent, all=True)

        # Delete all child elements
        self.delete_children()

        try:
            super(BaseTreeElement, self).prepare_deletion()
        except AttributeError:
            pass


class Reaction(BaseTreeElement, EvidenceLink, cobraReaction):

    def __init__(self, id="", name='', subsystem='', lower_bound=0.,
                 upper_bound=1000., comment=""):
        # Setup variables before calling
        self._model = None
        self._subsystem = None
        super(Reaction, self).__init__()

        self.id = id or ""
        self.name = name or ""
        self.subsystem = subsystem or ""
        self.lower_bound = lower_bound or 0.
        self.upper_bound = 1000. if upper_bound is None else upper_bound
        self.comment = comment or ""
        self.elements_balanced = None
        self.charge_balanced = None
        self.balanced = None

        self._metabolites = {}
        self._gene_reaction_rule = ''

        self.annotation = set()
        self.variable_kind = 'continuous'

    @property
    def functional(self):
        status = set(child.functional for child in self._children)
        if True in status:
            return True
        elif False in status:
            return False
        else:
            return True

    @property
    def _genes(self):
        return self.genes

    @_genes.setter
    def _genes(self, value):
        if value != set():
            raise ValueError("_genes should not be set!")
        pass

    @property
    def gene_reaction_rule(self):
        if self._children:
            return self._children[0].gem_reaction_rule
        else:
            return ""

    @gene_reaction_rule.setter
    def gene_reaction_rule(self, new_rule):
        raise NotImplementedError("Setting gene reaction rule is not supported!")

    def _dissociate_gene(self, cobra_gene):
        """Dissociates a cobra.Gene object with a cobra.Reaction.

        cobra_gene : :class:`~cobra.core.Gene.Gene`

        """
        self.remove_child(cobra_gene)

    def add_annotation(self, Annotation):
        self.annotation.add(Annotation)

    def get_setting(self):
        return ReactionSetting(reaction=self,
                               upper_bound=self.upper_bound,
                               lower_bound=self.lower_bound,
                               objective_coefficient=self.objective_coefficient)

    @property
    def reactions(self):
        return set([self])

    def add_parent(self, parent):
        raise NotImplementedError

    def remove_parent(self, parent, **kwargs):
        raise NotImplementedError

    @property
    def subsystem(self):
        return self._subsystem

    @subsystem.setter
    def subsystem(self, value):
        if self.model is not None:
            self.model.subsystems.remove_reaction(self._subsystem, self)
            self.model.subsystems[value].add(self)
        self._subsystem = value

    def update_balancing_status(self):
        self.charge_balanced, self.elements_balanced, self.balanced = reaction_balance(self.metabolites)

    def remove_from_model(self):
        if self._model:
            items = self._model.QtReactionTable.findItems(self.id)
            for x in items:
                if x.link is self:
                    index = self._model.QtReactionTable.indexFromItem(x)
                    self._model.QtReactionTable.removeRow(index.row())
            super(Reaction, self).remove_from_model()

    def add_metabolites(self, *args, **kwargs):
        super(Reaction, self).add_metabolites(*args, **kwargs)
        self.update_balancing_status()

    def get_annotation_by_collection(self, *args):
        return set([x.identifier for x in self.annotation if x.collection in args])

    def prepare_deletion(self):
        """ Prepare reaction for deletion from model

        Remove reaction subsystem from model list
        """

        # Remove subsystem
        if self.model:
            self.model.subsystems.remove_reaction(self.subsystem, self)

        super(Reaction, self).prepare_deletion()


class Gene(BaseTreeElement, EvidenceLink, cobraGene):

    def __init__(self, id="", name="", genome=""):
        super(Gene, self).__init__()
        EvidenceLink.__init__(self)

        self.id = id or ""
        self.name = name or ""
        self.genome = genome or ""
        self.annotation = set()

    @property
    def _reaction(self):
        return self._parents

    @_reaction.setter
    def _reaction(self, reaction_set):
        self._reaction.extend(reaction_set)

    @property
    def genes(self):
        return set([self])

    def add_child(self, child):
        raise NotImplementedError

    def remove_child(self, child):
        raise NotImplementedError

    @property
    def gem_reaction_rule(self):
        return self.id


class GeneGroup(BaseTreeElement, EvidenceLink):

    def __init__(self, id=None, genes=None, type="and"):
        super(GeneGroup, self).__init__()
        EvidenceLink.__init__(self)

        self.id = id or str(uuid.uuid4())
        # Genes might appear more than once in the group
        self._reference = set()
        self.type = type

        # Check if genes is a list
        if not isinstance(genes, string_types):
            try:
                iter(genes)
            except TypeError:
                pass
            else:
                for gene in genes:
                    self.add_child(gene)

    @property
    def functional(self):
        if not self._children:
            return None
        elif self.type == "and":
            return all(child.functional for child in self._children)
        elif self.type == "or":
            return any(child.functional for child in self._children)
        else:
            raise ValueError("Unknown group type '{}'".format(self.type))

    @property
    def gem_reaction_rule(self):
        base = " {} ".format(self.type)
        substrings = []
        for x in self._children:
            child_gpr = x.gem_reaction_rule
            if ("and" in child_gpr or "or" in child_gpr) and not (child_gpr.startswith("(") and child_gpr.endswith(")")):
                substrings.append("({})".format(child_gpr))
            elif child_gpr:
                substrings.append(child_gpr)
        return base.join(substrings)

    def __contains__(self, item):
        return item in self._children


class Model(QtCore.QObject, EvidenceLink, cobraModel):

    modelChanged = QtCore.pyqtSignal()

    def __init__(self, id_or_model=None, name=None):
        super(Model, self).__init__()
        self._id = id_or_model
        self.name = name

        self.QtReactionTable = ReactionTable(self)
        self.QtMetaboliteTable = MetaboliteTable(self)
        self.QtGeneTable = GeneTable(self)
        self.QtReferenceTable = ReferenceTable(self)
        self.QtTestsTable = ModelTestTable(self)
        self.QtCompartmentTable = CompartmentTable(self)
        self.subsystems = CleaningDict()
        self.references = {}
        self.all_evidences = WeakValueDictionary()
        self.tests = []
        self.dialogs = WindowManager()

        # Store the mapping between metabolites and database entries
        self.database_mapping = dict()

        # Keep track of compartment objects
        # to be able to link them in evidences
        self.gem_compartments = dict()

        # Keep track of maps for this model
        self.gem_maps = {}

        # Setup model
        self.setup_tables()
        self.setup_connections()

    def setup_connections(self):
        # Connect the changes in the reaction table to the modelChanged signal
        self.QtReactionTable.rowsInserted.connect(self.modelChanged.emit)
        self.QtReactionTable.rowsRemoved.connect(self.modelChanged.emit)
        self.QtReactionTable.dataChanged.connect(self.modelChanged.emit)

        # Connect the changes in the metabolite table to the modelChanged signal
        self.QtMetaboliteTable.rowsInserted.connect(self.modelChanged.emit)
        self.QtMetaboliteTable.rowsRemoved.connect(self.modelChanged.emit)
        self.QtMetaboliteTable.dataChanged.connect(self.modelChanged.emit)

        # Connect the changes in the gene table to the modelChanged signal
        self.QtGeneTable.rowsInserted.connect(self.modelChanged.emit)
        self.QtGeneTable.rowsRemoved.connect(self.modelChanged.emit)
        self.QtGeneTable.dataChanged.connect(self.modelChanged.emit)

        # Connect the changes in the reference table to the modelChanged signal
        self.QtReferenceTable.rowsInserted.connect(self.modelChanged.emit)
        self.QtReferenceTable.rowsRemoved.connect(self.modelChanged.emit)
        self.QtReferenceTable.dataChanged.connect(self.modelChanged.emit)

        # Connect the changes in the reference table to the modelChanged signal
        self.QtTestsTable.rowsInserted.connect(self.modelChanged.emit)
        self.QtTestsTable.rowsRemoved.connect(self.modelChanged.emit)
        self.QtTestsTable.dataChanged.connect(self.modelChanged.emit)

        # Connect the changes in the compartment table to modelChanged signal
        self.QtCompartmentTable.rowsInserted.connect(self.modelChanged.emit)
        self.QtCompartmentTable.rowsRemoved.connect(self.modelChanged.emit)
        self.QtCompartmentTable.dataChanged.connect(self.modelChanged.emit)

    def setup_tables(self):
        self.setup_reaction_table()
        self.setup_metabolite_table()
        self.setup_gene_table()
        self.setup_tests_table()
        self.setup_reference_table()
        self.setup_compartment_table()

    def setup_reaction_table(self):
        self.QtReactionTable.populate_table(self.reactions)

    def setup_metabolite_table(self):
        self.QtMetaboliteTable.populate_table(self.metabolites)

    def setup_gene_table(self):
        self.QtGeneTable.populate_table(self.genes)

    def setup_tests_table(self):
        self.QtTestsTable.populate_table(self.tests)

    def setup_reference_table(self):
        self.QtReferenceTable.populate_table(self.references.values())

    def setup_compartment_table(self):
        self.QtCompartmentTable.populate_table(self.gem_compartments.values())

    def add_reference(self, reference):
        self.references[reference.id] = reference

    def add_gene(self, gene):
        self.genes.append(gene)

    def add_test(self, test):
        self.tests.append(test)

    def add_evidence(self, evidence):
        self.all_evidences[evidence.internal_id] = evidence

    def copy_metabolite(self, metabolite, compartment):
        new_metabolite = Metabolite(id=generate_copy_id(metabolite.id, self.metabolites),
                                    formula=metabolite.formula,
                                    name=metabolite.name,
                                    charge=metabolite.charge,
                                    compartment=compartment)
        new_metabolite.annotation = metabolite.annotation.copy()
        self.add_metabolites([new_metabolite])
        self.QtMetaboliteTable.update_row_from_item(new_metabolite)
        return new_metabolite

    def optimize(self, *args, refresh_dialogs=False, **kwargs):
        solution = super(Model, self).optimize(*args, **kwargs)
        if refresh_dialogs:
            self.update_dialogs(solution)

        return solution

    def update_dialogs(self, solution):
        for dialog in self.dialogs.windows:
            try:
                dialog.set_reaction_data(solution)
            except AttributeError:
                pass

    def add_metabolites(self, metabolite_list):
        if not hasattr(metabolite_list, '__iter__'):
            metabolite_list = [metabolite_list]

        for metabolite in metabolite_list:
            if metabolite.compartment not in self.gem_compartments:
                self.gem_compartments[metabolite.compartment] = Compartment(metabolite.compartment)

        super(Model, self).add_metabolites(metabolite_list)

    def add_reactions(self, list_of_reactions):

        # Add reactions to model
        super(Model, self).add_reactions(list_of_reactions)

        # Add subsystems
        for reaction in list_of_reactions:
            self.subsystems[reaction.subsystem].add(reaction)

    def add_genes(self, genes):
        for gene in genes:
            self.genes.add(gene)
            gene._model = self

    def gem_update_metabolites(self, metabolites, progress=None):
        """ Update the metabolite entries in the QTable

        Parameters
        ----------
        metabolites: iterable
        progress: QProgressDialog

        Returns
        -------

        """
        if not metabolites:
            return

        if progress is not None:
            progress.setLabelText("Updating metabolite tables..")
            progress.setRange(0, len(self.metabolites))

        # Block updates for speed
        self.QtMetaboliteTable.blockSignals(True)

        # Get mapping of tables
        met_mapping = self.QtMetaboliteTable.get_item_to_row_mapping()

        reactions_to_update = set()

        for i, metabolite in enumerate(metabolites):

            # Update progress dialog
            if progress:
                progress.setValue(i)
                QApplication.processEvents()

            # Update metabolite
            self.QtMetaboliteTable.update_row_from_item(metabolite, met_mapping[metabolite])
            reactions_to_update.update(self.reactions)

        # Update table
        self.QtMetaboliteTable.blockSignals(False)
        self.QtMetaboliteTable.all_data_changed()

        # Run update reactions
        self.gem_update_reactions(reactions_to_update, progress)

    def gem_update_reactions(self, reactions, progress=None):
        """ Update the reaction entries in the QTable

        Parameters
        ----------
        reactions: iterable
        progress: QProgressDialog

        Returns
        -------

        """

        self.QtReactionTable.blockSignals(True)
        react_mapping = self.QtReactionTable.get_item_to_row_mapping()

        if progress:
            progress.setLabelText("Updating reaction tables..")
            progress.setRange(0, len(reactions))

        for i, reaction in enumerate(reactions):

            # Update progress dialog
            if progress:
                progress.setValue(i)
                QApplication.processEvents()

            # Update reaction
            reaction.update_balancing_status()
            self.QtReactionTable.update_row_from_item(reaction, react_mapping[reaction])

        self.QtReactionTable.blockSignals(False)
        self.QtReactionTable.all_data_changed()

    def gem_remove_metabolites(self, metabolites):
        """ Delete metabolites from the model

        Parameters
        ----------
        metabolites: list,
            Metabolites to be removed

        Returns
        -------

        """

        # Remove evidence links
        for m in metabolites:
            m.remove_all_evidences()

        # Remove metabolites from model
        self.remove_metabolites(metabolites)

        # Remove metabolites from table
        self._gem_remove_items_from_table(self.QtMetaboliteTable, metabolites)

    def gem_remove_reactions(self, reactions):
        """ Delete reactions from the model

        Parameters
        ----------
        reactions: list,
            Reactions to be removed

        Returns
        -------
        None
        """

        # Remove evidence links
        for r in reactions:
            r.remove_all_evidences()
            r.prepare_deletion()

        # Remove reactions from model
        self.remove_reactions(reactions, remove_orphans=False)

        # Remove reactions from table
        self._gem_remove_items_from_table(self.QtReactionTable, reactions)

        # Remove all test cases that link to reaction from model
        tests_to_remove = []
        for testcase in self.tests.copy():
            if any(x.reaction in reactions for x in testcase.reaction_settings):
                tests_to_remove.append(testcase)
            elif any(x.reaction in reactions for x in testcase.outcomes):
                tests_to_remove.append(testcase)

        self.gem_remove_tests(tests_to_remove)

    def gem_remove_genes(self, genes):
        """ Delete genes from model

        Parameters
        ----------
        genes: list,
            Genes to be removed from model

        Returns
        -------
        None
        """
        # Remove GEMEditor specific links
        for gene in genes:
            gene.remove_all_evidences()
            gene.prepare_deletion()

            # Remove gene from model
            self.genes.remove(gene)
            gene._model = None

        # Remove reactions from table
        self._gem_remove_items_from_table(self.QtGeneTable, genes)

        # Remove all test cases that link to gene from model
        tests_to_remove = []
        for testcase in self.tests.copy():
            if any(x.gene in genes for x in testcase.gene_settings):
                tests_to_remove.append(testcase)
        self.gem_remove_tests(tests_to_remove)

    def gem_remove_references(self, references):
        """ Remove reference items from model

        Parameters
        ----------
        references: list,
            References to be removed

        Returns
        -------
        None
        """
        for reference in references:
            reference.remove_all_links()
            del self.references[reference.id]

        # Remove reactions from table
        self._gem_remove_items_from_table(self.QtReferenceTable, references)

    def gem_remove_tests(self, testcases):
        """ Remove test cases from model

        Parameters
        ----------
        testcases: list,
            Test cases to be removed

        Returns
        -------
        None
        """
        for test in testcases:
            test.remove_all_references()

            # Todo: Change to more efficient data structure
            try:
                index = self.tests.index(test)
            except ValueError:
                return
            else:
                self.tests.pop(index)
                self.QtTestsTable.removeRow(index)

    @staticmethod
    def _gem_remove_items_from_table(table, items):
        mapping = table.get_item_to_row_mapping()
        table.delete_rows([mapping[i] for i in items])

    def close(self):
        self.dialogs.remove_all()


class Metabolite(EvidenceLink, cobraMetabolite):

    def __init__(self, id="", formula="", name="",
                 charge=0, compartment=""):
        super(Metabolite, self).__init__()

        self.id = id or ""
        self.name = name or ""
        self.formula = formula or ""
        self.compartment = compartment or ""
        self.charge = charge or 0

        # Override annotation
        # Todo: Change to gem specific attribute name
        self.annotation = set()

    def get_annotation_by_collection(self, *args):
        return set([x.identifier for x in self.annotation if x.collection in args])


def iterate_tree(standard_item, data_item):
    for n, element in enumerate(data_item._children):
        if isinstance(element, Gene):
            gene_item = LinkedItem(element.id, element)
            gene_item.setEditable(False)
            standard_item.setChild(n, gene_item)
        elif isinstance(element, GeneGroup):
            new_item = LinkedItem(str(element.type).upper(), element)
            new_item.setEditable(False)
            iterate_tree(new_item, element)
            standard_item.setChild(n, new_item)


def find_duplicate_metabolite(metabolite, collection, same_compartment=True, cutoff=0., ignore_charge=False):
    duplicates = []
    for entry in collection:
        similarity = 0
        if not ignore_charge and entry.charge != metabolite.charge:
            continue
        elif same_compartment and entry.compartment != metabolite.compartment:
            continue

        if entry.formula and metabolite.formula:
            if entry.formula != metabolite.formula:
                continue
            else:
                similarity += 1

        similarity += len(metabolite.annotation.intersection(entry.annotation)) * 2
        similarity += SequenceMatcher(a=metabolite.name, b=entry.name).quick_ratio()
        if similarity > cutoff:
            duplicates.append((entry, similarity))

    return sorted(duplicates, key=lambda tup: tup[1], reverse=True)


def prune_gene_tree(input_element, parent=None):
    """ Simplify gene tree

    Parameters
    ----------
    input_element

    Returns
    -------

    """

    # Remove gene groups with 0 or one children, or nested or groups
    if len(input_element._children) <= 1 and isinstance(input_element, GeneGroup) or \
        (isinstance(input_element, GeneGroup) and input_element.type == "or" and
             isinstance(parent, GeneGroup) and parent.type == "or"):
        for child in input_element._children.copy():
            input_element.remove_child(child)
            parent.add_child(child)
            prune_gene_tree(child, parent)
        parent.remove_child(input_element)
    # Try to prune all downstream branches
    else:
        for child in input_element._children:
            prune_gene_tree(child, input_element)

