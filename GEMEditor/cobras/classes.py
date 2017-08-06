# from PyQt5.QtCore import QObject
# from cobra.core import Metabolite as cobraMetabolite
# from cobra.core import Gene as cobraGene
# from cobra.core import Reaction as cobraReaction
# from cobra.core import Model as cobraModel
# from GEMEditor.base.classes import BaseModelItem
# from collections import defaultdict
#
#
# class CleaningDict(defaultdict):
#
#     def __init__(self):
#         super(CleaningDict, self).__init__(set)
#
#     def remove_reaction(self, key, reaction):
#         self[key].discard(reaction)
#         if not self[key]:
#             del self[key]
#
#
# class WindowManager(QObject):
#
#     def __init__(self):
#         super(WindowManager, self).__init__()
#         self.windows = set()
#
#     def add(self, dialog):
#         self.windows.add(dialog)
#         dialog.finished.connect(self.delete_window)
#
#     def remove(self, dialog):
#         self.windows.discard(dialog)
#
#     def remove_all(self):
#         for window in self.windows.copy():
#             window.close()
#
#     @QtCore.pyqtSlot()
#     def delete_window(self):
#         sender = self.sender()
#         self.windows.discard(sender)
#
#
# class Model(QObject, cobraModel):
#
#     modelChanged = QtCore.pyqtSignal()
#
#     def __init__(self, *args, **kwargs):
#         super(Model, self).__init__(*args, **kwargs)
#         BaseEvidenceElement.__init__(self)
#
#         self.QtReactionTable = ReactionTable(self)
#         self.QtMetaboliteTable = MetaboliteTable(self)
#         self.QtGeneTable = GeneTable(self)
#         self.QtReferenceTable = ReferenceTable(self)
#         self.QtTestsTable = ModelTestTable(self)
#         self.gem_subsystems = CleaningDict()
#         self.references = {}
#         self.all_evidences = WeakValueDictionary()
#         self.tests = []
#         self.dialogs = WindowManager()
#         self.setup_tables()
#         self.setup_connections()
#
#     def setup_connections(self):
#         # Connect the changes in the reaction table to the modelChanged signal
#         self.QtReactionTable.rowsInserted.connect(self.modelChanged.emit)
#         self.QtReactionTable.rowsRemoved.connect(self.modelChanged.emit)
#         self.QtReactionTable.dataChanged.connect(self.modelChanged.emit)
#
#         # Connect the changes in the metabolite table to the modelChanged signal
#         self.QtMetaboliteTable.rowsInserted.connect(self.modelChanged.emit)
#         self.QtMetaboliteTable.rowsRemoved.connect(self.modelChanged.emit)
#         self.QtMetaboliteTable.dataChanged.connect(self.modelChanged.emit)
#
#         # Connect the changes in the gene table to the modelChanged signal
#         self.QtGeneTable.rowsInserted.connect(self.modelChanged.emit)
#         self.QtGeneTable.rowsRemoved.connect(self.modelChanged.emit)
#         self.QtGeneTable.dataChanged.connect(self.modelChanged.emit)
#
#         # Connect the changes in the reference table to the modelChanged signal
#         self.QtReferenceTable.rowsInserted.connect(self.modelChanged.emit)
#         self.QtReferenceTable.rowsRemoved.connect(self.modelChanged.emit)
#         self.QtReferenceTable.dataChanged.connect(self.modelChanged.emit)
#
#         # Connect the changes in the reference table to the modelChanged signal
#         self.QtTestsTable.rowsInserted.connect(self.modelChanged.emit)
#         self.QtTestsTable.rowsRemoved.connect(self.modelChanged.emit)
#         self.QtTestsTable.dataChanged.connect(self.modelChanged.emit)
#
#     def setup_tables(self):
#         self.setup_reaction_table()
#         self.setup_metabolite_table()
#         self.setup_gene_table()
#         self.setup_tests_table()
#         self.setup_reference_table()
#
#     def setup_reaction_table(self):
#         self.QtReactionTable.populate_table(self.reactions)
#
#     def setup_metabolite_table(self):
#         self.QtMetaboliteTable.populate_table(self.metabolites)
#
#     def setup_gene_table(self):
#         self.QtGeneTable.populate_table(self.genes)
#
#     def setup_tests_table(self):
#         self.QtTestsTable.populate_table(self.tests)
#
#     def setup_reference_table(self):
#         self.QtReferenceTable.populate_table(self.references.values())
#
#     def add_reference(self, reference):
#         self.references[reference.id] = reference
#
#     def add_gene(self, gene):
#         self.genes.append(gene)
#
#     def add_test(self, test):
#         self.tests.append(test)
#
#     def add_evidence(self, evidence):
#         self.all_evidences[evidence.internal_id] = evidence
#
#     def add_reactions(self, reaction_list):
#         """Will add a cobra.Reaction object to the model, if
#         reaction.id is not in self.reactions.
#
#         reaction_list: A list of :class:`~cobra.core.Reaction` objects
#
#         """
#         # Only add the reaction if one with the same ID is not already
#         # present in the model.
#
#         # This function really should not used for single reactions
#         if not hasattr(reaction_list, "__len__"):
#             reaction_list = [reaction_list]
#             warn("Use add_reaction for single reactions")
#
#         # Add reactions. Also take care of genes and metabolites in the loop
#         for reaction in reaction_list:
#             reaction._model = self  # the reaction now points to the model
#             self.subsystems[reaction.subsystem].add(reaction)
#
#             for metabolite in list(reaction._metabolites.keys()):
#                 # if the metabolite is not in the model, add it
#                 # should we be adding a copy instead.
#                 if not self.metabolites.has_id(metabolite.id):
#                     self.metabolites.append(metabolite)
#                     metabolite._model = self
#                 else:
#                     stoichiometry = reaction._metabolites.pop(metabolite)
#                     model_metabolite = self.metabolites.get_by_id(
#                         metabolite.id)
#                     reaction._metabolites[model_metabolite] = stoichiometry
#                     model_metabolite._reaction.add(reaction)
#
#             for gene in reaction.genes:
#                 if not self.genes.has_id(gene.id):
#                     self.genes.append(gene)
#                     gene._model = self
#                 else:
#                     if gene is not self.genes.get_by_id(gene.id):
#                         raise ValueError("There is already a gene with id {} in the model".format(gene.id))
#
#         self.reactions += reaction_list
#
#     def copy_metabolite(self, metabolite, compartment):
#         new_metabolite = Metabolite(id=generate_copy_id(metabolite.id, self.metabolites),
#                                     formula=metabolite.formula,
#                                     name=metabolite.name,
#                                     charge=metabolite.charge,
#                                     compartment=compartment)
#         new_metabolite.annotation = metabolite.annotation.copy()
#         self.add_metabolites([new_metabolite])
#         self.QtMetaboliteTable.update_row_from_item(new_metabolite)
#         return new_metabolite
#
#     def optimize(self, *args, refresh_dialogs=False, **kwargs):
#         solution = super(Model, self).optimize(*args, **kwargs)
#         if refresh_dialogs:
#             self.update_dialogs(solution)
#
#         return solution
#
#     def update_dialogs(self, solution):
#         for dialog in self.dialogs.windows:
#             try:
#                 dialog.set_reaction_data(solution.x_dict)
#             except AttributeError:
#                 pass
#
#     def add_metabolites(self, metabolite_list):
#         if not hasattr(metabolite_list, '__iter__'):
#             metabolite_list = [metabolite_list]
#
#         for metabolite in metabolite_list:
#             if metabolite.compartment not in self.compartments:
#                 self.compartments[metabolite.compartment] = Compartment(metabolite.compartment)
#
#         super(Model, self).add_metabolites(metabolite_list)
#
#     def remove_test(self, test):
#         """ Remove the test from the model"""
#
#         try:
#             index = self.tests.index(test)
#         except ValueError:
#             return
#         else:
#             self.tests.pop(index)
#             self.QtTestsTable.removeRow(index)
#
#     def add_gene_to_subsystem(self, reaction, subsystem):
#         self.gem_subsystems[subsystem].add(reaction)
#
#     def remove_gene_from_subsystem(self, reaction, subsystem):
#         self.gem_subsystems.remove_reaction(subsystem, reaction)
#
#     def close(self):
#         self.dialogs.remove_all()
#
#
# class Reaction(BaseModelItem, cobraReaction):
#
#     def __init__(self, id="", name='', subsystem='', lower_bound=0., upper_bound=1000.):
#         super(Reaction, self).__init__()
#
#         # Cobra attributes
#         self.id = id or ""
#         self.name = name or ""
#         self.subsystem = subsystem or ""
#         self.lower_bound = lower_bound or 0.
#         self.upper_bound = 1000. if upper_bound is None else upper_bound
#
#         # GEMEditor specific attributes
#         self.elements_balanced = None
#         self.charge_balanced = None
#         self.balanced = None
#         self.gem_subsystems = set()
#
#     @property
#     def enabled(self):
#         status = set(child.functional for child in self._children)
#         if True in status:
#             return True
#         elif False in status:
#             return False
#         else:
#             return True
#
#     @property
#     def _genes(self):
#         return self.genes
#
#     @_genes.setter
#     def _genes(self, value):
#         if value != set():
#             raise ValueError("_genes should not be set!")
#         pass
#
#     @property
#     def gene_reaction_rule(self):
#         if self._children:
#             return self._children[0].gem_reaction_rule
#         else:
#             return ""
#
#     @gene_reaction_rule.setter
#     def gene_reaction_rule(self, new_rule):
#         self._gene_reaction_rule = new_rule.strip()
#         try:
#             _, gene_names = parse_gpr(self._gene_reaction_rule)
#         except (SyntaxError, TypeError) as e:
#             warn("malformed gene_reaction_rule '%s' for %s" %
#                  (new_rule, repr(self)))
#             tmp_str = and_or_search.sub('', self._gene_reaction_rule)
#             gene_names = set((gpr_clean.sub(' ', tmp_str).split(' ')))
#         if '' in gene_names:
#             gene_names.remove('')
#         old_genes = self._genes
#         if self._model is None:
#             self._genes = {Gene(i) for i in gene_names}
#         else:
#             model_genes = self._model.genes
#             self._genes = set()
#             for id in gene_names:
#                 if model_genes.has_id(id):
#                     self._genes.add(model_genes.get_by_id(id))
#                 else:
#                     new_gene = Gene(id)
#                     new_gene._model = self._model
#                     self._genes.add(new_gene)
#                     model_genes.append(new_gene)
#
#         # Make the genes aware that it is involved in this reaction
#         for g in self._genes:
#             g._reaction.add(self)
#
#         # make the old genes aware they are no longer involved in this reaction
#         for g in old_genes:
#             if g not in self._genes:  # if an old gene is not a new gene
#                 try:
#                     g._reaction.remove(self)
#                 except:
#                     warn("could not remove old gene %s from reaction %s" %
#                          (g.id, self.id))
#
#     @subsystem.setter
#     def subsystem(self, value):
#         if self.model is not None:
#             self.model.subsystems.remove_reaction(self._subsystem, self)
#             self.model.subsystems[value].add(self)
#         self._subsystem = value
#
#     def update_balancing_status(self):
#         self.charge_balanced, self.elements_balanced, self.balanced = reaction_balance(self._metabolites)
#
#     def remove_from_model(self):
#         if self._model:
#             items = self._model.QtReactionTable.findItems(self.id)
#             for x in items:
#                 if x.link is self:
#                     index = self._model.QtReactionTable.indexFromItem(x)
#                     self._model.QtReactionTable.removeRow(index.row())
#             super(Reaction, self).remove_from_model()
#
#     def add_metabolites(self, *args, **kwargs):
#         super(Reaction, self).add_metabolites(*args, **kwargs)
#         self.update_balancing_status()
#
#     def add_subsystem(self, subsystem):
#         """ Add subsystem to the list"""
#         self.gem_subsystems.add(subsystem)
#         if self.model is not None:
#             self.model.add_reaction_to_subsystem(self, subsystem)
#
#     def remove_subsystem(self, subsystem):
#         """ Remove the subsystem from the list"""
#         self.gem_subsystems.discard(subsystem)
#         if self.model is not None:
#             self.model.remove_reaction_from_subsystem(self, subsystem)
#
#
# class Metabolite(BaseModelItem, cobraMetabolite):
#
#     def __init__(self, id="", formula="", name="", charge=0, compartment=""):
#         super(Metabolite, self).__init__()
#
#         self.id = id or ""
#         self.name = name or ""
#         self.formula = formula or ""
#         self.compartment = compartment or ""
#         self.charge = charge or 0
#
#
# class Gene(BaseModelItem, cobraGene):
#
#     def __init__(self, id="", name="", genome=""):
#         super(Gene, self).__init__()
#
#         self.id = id or ""
#         self.name = name or ""
#         self.genome = genome or ""
#
#
# class Compartment(BaseModelItem):
#     def __init__(self, id=None, name=None):
#         super(Compartment, self).__init__()
#         self.id = id
#         self.name = name
#
#     def get_values(self):
#         return self.id, self.name
#
#     def __eq__(self, other):
#         if isinstance(other, tuple):
#             return other == self.get_values()
#         elif isinstance(other, Compartment):
#             return other.get_values() == self.get_values()
#         else:
#             return NotImplemented
#
#     def __repr__(self):
#         return str(self.id)
#
#
#
# from cobra.core import Model as cobraModel
# from weakref import WeakValueDictionary
# from PyQt5 import QtGui, QtCore
# from collections import defaultdict
# from GEMEditor.widgets.tables import ReactionTable, MetaboliteTable, GeneTable, ReferenceTable, ModelTestTable, LinkedItem
# from GEMEditor.data_classes import ReactionSetting
# from GEMEditor.evidence.base import BaseEvidenceElement
# from warnings import warn
# from six import string_types, iteritems
# from difflib import SequenceMatcher
# import uuid
#
#
#
#
# def iterate_tree(standard_item, data_item):
#     for n, element in enumerate(data_item._children):
#         if isinstance(element, Gene):
#             gene_item = LinkedItem(element.id, element)
#             gene_item.setEditable(False)
#             standard_item.setChild(n, gene_item)
#         elif isinstance(element, GeneGroup):
#             new_item = LinkedItem(str(element.type).upper(), element)
#             new_item.setEditable(False)
#             iterate_tree(new_item, element)
#             standard_item.setChild(n, new_item)
#
#
# def check_charge_balance(metabolites):
#     """ Check charge balance of the reaction """
#     # Check that charge is set for all metabolites
#     if not all(x.charge is not None for x in metabolites.keys()):
#         return None
#     else:
#         return sum([metabolite.charge * coefficient for metabolite, coefficient in iteritems(metabolites)])
#
#
# def check_element_balance(metabolites):
#     """ Check that the reaction is elementally balanced """
#     # Check that a formula is set for all metabolites
#     if not all(x.formula for x in metabolites.keys()):
#         return None
#     else:
#         metabolite_elements = defaultdict(int)
#         for metabolite, coefficient in iteritems(metabolites):
#             for element, amount in iteritems(metabolite.elements):
#                 metabolite_elements[element] += coefficient * amount
#         return {k: v for k, v in iteritems(metabolite_elements) if v != 0}
#
#
# def reaction_string(stoichiometry, use_metabolite_names=True):
#     """Generate the reaction string """
#
#     attrib = "id"
#     if use_metabolite_names:
#         attrib = "name"
#
#     educts = [(str(abs(value)), getattr(key, attrib)) for key, value in iteritems(stoichiometry) if value < 0.]
#     products = [(str(abs(value)), getattr(key, attrib)) for key, value in iteritems(stoichiometry) if value > 0.]
#
#     return " + ".join([" ".join(x) for x in educts])+" --> "+" + ".join([" ".join(x) for x in products])
#
#
# def unbalanced_metabolites_to_string(in_dict):
#     substrings = ['{0}: {1:.1f}'.format(*x) for x in in_dict.items()]
#     return "<br>".join(substrings)
#
#
# def reaction_balance(metabolites):
#     """ Check the balancing status of the stoichiometry
#
#     Parameters
#     ----------
#     metabolites : dict - Dictionary of metabolites with stoichiometric coefficnets
#
#     Returns
#     -------
#     charge_str : str or bool
#     element_str : str or bool
#     balanced : str or bool
#     """
#     element_result = check_element_balance(metabolites)
#     charge_result = check_charge_balance(metabolites)
#
#     if charge_result is None:
#         charge_str = "Unknown"
#     elif charge_result == 0:
#         charge_str = "OK"
#     else:
#         charge_str = str(charge_result)
#
#     if element_result is None:
#         element_str = "Unknown"
#     elif element_result == {}:
#         element_str = "OK"
#     else:
#         element_str = unbalanced_metabolites_to_string(element_result)
#
#     if len(metabolites) < 2:
#         balanced = None
#     elif element_str == "OK" and charge_str == "OK":
#         balanced = True
#     elif element_str not in ("OK", "Unknown") or charge_str not in ("OK", "Unknown"):
#         balanced = False
#     else:
#         balanced = "Unknown"
#
#     return charge_str, element_str, balanced
#
#
# def remove_genes(model, genes):
#     """ Remove reactions from the model
#
#     Parameters
#     ----------
#     model : GEMEditor.cobraClasses.Model
#     genes : list of Genes
#
#     Returns
#     -------
#
#     """
#     for gene in genes:
#
#         # Delete all linked evidences
#         gene.remove_all_evidences()
#
#         # Remove all parents
#         for parent in gene._parents.copy():
#             gene.remove_parent(parent, all=True)
#
#         model.genes.remove(gene)
#
#     # Remove all test cases that link to gene
#     for testcase in model.tests.copy():
#         if any(x.gene in genes for x in testcase.gene_settings):
#             model.remove_test(testcase)
#
#
# def generate_copy_id(source_id, collection, suffix="_copy"):
#     base_id = str(source_id) + suffix
#     new_id = base_id
#     n = 0
#     # Make sure there is no metabolite with the same id
#     while new_id in collection:
#         n += 1
#         new_id = base_id + str(n)
#     return new_id
#
#
# def find_duplicate_metabolite(metabolite, collection, same_compartment=True, cutoff=0.):
#     duplicates = []
#     for entry in collection:
#         similarity = 0
#         if entry.charge != metabolite.charge:
#             continue
#         elif same_compartment and entry.compartment != metabolite.compartment:
#             continue
#
#         if entry.formula and metabolite.formula:
#             if entry.formula != metabolite.formula:
#                 continue
#             else:
#                 similarity += 1
#
#         similarity += len(metabolite.annotation.intersection(entry.annotation)) * 2
#         similarity += SequenceMatcher(a=metabolite.name, b=entry.name).quick_ratio()
#         if similarity > cutoff:
#             duplicates.append((entry, similarity))
#
#     return sorted(duplicates, key=lambda tup: tup[1], reverse=True)
#
#
# def prune_gene_tree(input_element, parent=None):
#     """ Simplify gene tree
#
#     Parameters
#     ----------
#     input_element
#
#     Returns
#     -------
#
#     """
#
#     # Remove gene groups with 0 or one children, or nested or groups
#     if len(input_element._children) <= 1 and isinstance(input_element, GeneGroup) or \
#         (isinstance(input_element, GeneGroup) and input_element.type == "or" and
#              isinstance(parent, GeneGroup) and parent.type == "or"):
#         for child in input_element._children.copy():
#             input_element.remove_child(child)
#             parent.add_child(child)
#             prune_gene_tree(child, parent)
#         parent.remove_child(input_element)
#     # Try to prune all downstream branches
#     else:
#         for child in input_element._children:
#             prune_gene_tree(child, input_element)
#
#
