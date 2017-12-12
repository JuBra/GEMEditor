import cobra
import logging
from collections import OrderedDict
from GEMEditor.analysis.model_test import run_tests
from GEMEditor.base.classes import Settings, ProgressDialog
from GEMEditor.base.functions import generate_copy_id
from GEMEditor.base.dialogs import DataFrameDialog
from GEMEditor.main.model.ui import Ui_StandardTab, Ui_AnalysisTab, Ui_SolutionTableWidget, Ui_model_stats_tab
from GEMEditor.model.classes.cobra import Gene, Reaction, Metabolite, find_duplicate_metabolite
from GEMEditor.model.classes.modeltest import ModelTest
from GEMEditor.model.classes.reference import Reference
from GEMEditor.model.display.proxymodels import ReactionProxyFilter, MetaboliteProxyFilter, GeneProxyFilter, ReferenceProxyFilter
from GEMEditor.model.edit.gene import GeneEditDialog
from GEMEditor.model.edit.metabolite import MetaboliteEditDialog
from GEMEditor.model.edit.modeltest import EditModelTestDialog
from GEMEditor.model.edit.reaction import ReactionInputDialog, SetFluxValueDialog
from GEMEditor.model.edit.reference import ReferenceEditDialog
from GEMEditor.solution.base import status_objective_from_solution, set_objective_to_label, set_status_to_label
from GEMEditor.solution.display import SolutionDialog, factory_solution
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QSortFilterProxyModel, QSize
from PyQt5.QtWidgets import QWidget, QMessageBox, QApplication, QAction, QMenu, QInputDialog, QProgressDialog, \
    QStatusBar, QListWidgetItem
from cobra.flux_analysis import pfba, flux_variability_analysis, loopless_solution, single_gene_deletion, \
    single_reaction_deletion


LOGGER = logging.getLogger(__name__)


class StandardTab(QWidget, Ui_StandardTab):

    # Signal that should be emitted when there is a change to the model stats
    # i.e. addition/deletion of items to the model.
    modelChanged = QtCore.pyqtSignal()

    # The data_type represented in the table
    # Used in:  - Context menu
    #           - Buttons
    data_type = None

    def __init__(self, ProxyModel=None):
        QWidget.__init__(self)
        self.setupUi(self)
        self.model = None

        if ProxyModel is None:
            self.proxyModel = QSortFilterProxyModel(self)
            # Hide filter label and combobox
            self.label_filter.setVisible(False)
            self.filterComboBox.setVisible(False)
            self.line.setVisible(False)
        else:
            self.proxyModel = ProxyModel(self)
            # Show filter label and combobox
            self.label_filter.setVisible(True)
            self.filterComboBox.setVisible(True)
            self.line.setVisible(True)

            self.filterComboBox.addItems(ProxyModel.options)
            self.filterComboBox.currentIndexChanged.connect(self.proxyModel.set_custom_filter)

        self.proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxyModel.setFilterKeyColumn(-1)
        self.proxyModel.setDynamicSortFilter(True)
        self.dataView.setModel(self.proxyModel)
        self.proxyModel.sort(0)

        self.addItemButton.setText("Add {}".format(self.data_type))
        self.editItemButton.setText(self.tr("Edit {}".format(self.data_type)))
        self.deleteItemButton.setText(self.tr("Delete {}".format(self.data_type)))

        self.searchInput.textChanged.connect(self.proxyModel.setFilterFixedString)

    def confirmDeletion(self):
        row_indices = self.dataView.get_selected_rows()
        if row_indices:
            display_names = [self.dataTable.get_row_display_name(row) for row in row_indices]
            if len(display_names) > 20:
                question_text = self.tr("Do you really want to delete {0!s} {1!s}s\nThis can not be undone!".format(len(display_names), self.data_type))
            else:
                question_text = self.tr("Do you really want to delete the {0!s}s {1!s}?\nThis can not be undone!".format(self.data_type, ", ".join(display_names)))
            status = QMessageBox.question(self,
                                          self.tr("Delete {0!s}s?".format(self.data_type)),
                                          question_text,
                                          QMessageBox.Yes,
                                          QMessageBox.No)
            if status == QMessageBox.Yes:
                return True

        return False

    @QtCore.pyqtSlot()
    def addItemSlot(self):
        pass

    @QtCore.pyqtSlot()
    def editItemSlot(self):
        pass

    @QtCore.pyqtSlot()
    def deleteItemSlot(self):
        pass

    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Copy):
            self.copySelectionToClipboard()
        elif event.matches(QtGui.QKeySequence.Delete):
            self.deleteItemSlot()
        elif event.matches(QtGui.QKeySequence.Find):
            self.searchInput.selectAll()
            self.searchInput.setFocus(QtCore.Qt.ShortcutFocusReason)
        QWidget.keyPressEvent(self, event)

    def copySelectionToClipboard(self):
        selection = self.dataView.get_selected_indexes()
        if selection:
            selection_dict = {}
            for element in sorted(selection, key=lambda x: (x.row(), x.column())):
                element_text = self.dataTable.itemFromIndex(element).text()
                try:
                    selection_dict[element.row()].append(element_text)
                except KeyError:
                    selection_dict[element.row()] = [element_text]
            text = "\n".join(["\t".join(selection_dict[key]) for key in selection_dict.keys()])
            clipboard = QApplication.clipboard()
            clipboard.setText(text)

    def add_standard_menu_actions(self, menu):
        """ Return a standard context menu consisting of the add, edit and delete functions """

        add_action = QAction(self.tr("Add {}".format(self.data_type)), menu)
        add_action.triggered.connect(self.addItemSlot)
        menu.addAction(add_action)

        # Show edit and deletion option only if an item is selected
        if self.dataView.selectedIndexes():
            # Edit action
            edit_action = QAction(self.tr("Edit {}".format(self.data_type)), menu)
            edit_action.triggered.connect(self.editItemSlot)
            menu.addAction(edit_action)

            # Delete action
            delete_action = QAction(self.tr("Delete {}".format(self.data_type)), menu)
            delete_action.triggered.connect(self.deleteItemSlot)
            menu.addAction(delete_action)
        return menu

    @QtCore.pyqtSlot(QtCore.QPoint)
    def showContextMenu(self, pos):
        menu = QMenu()
        self.add_standard_menu_actions(menu)
        menu.exec_(self.dataView.viewport().mapToGlobal(pos))

    def set_model(self, model):
        self.clear_widget()
        self.model = model
        self.set_datatable()

    def set_datatable(self):
        raise NotImplementedError

    def clear_widget(self):
        self.searchInput.clear()

    def update_row(self, row):
        """ Update datatable row from the linked object """
        self.dataTable.update_row_from_item(self.dataTable.item(row).link, row)


class ReactionTab(StandardTab):

    data_type = "Reaction"

    def __init__(self):
        StandardTab.__init__(self, ProxyModel=ReactionProxyFilter)
        self.dataTable = None

    @QtCore.pyqtSlot()
    def deleteItemSlot(self):
        if self.confirmDeletion():
            reactions = self.dataView.get_selected_items()
            self.model.gem_remove_reactions(reactions)

    @QtCore.pyqtSlot()
    def editItemSlot(self):
        selected_index = self.dataView.get_selected_indexes(get_first_only=True)
        if selected_index:
            row_index = selected_index[0].row()
            col_index = selected_index[0].column()
            edit_reaction = self.dataTable.item_from_row(row_index)

            dialog = ReactionInputDialog(edit_reaction, self.model, parent=self)

            # Todo: Move this to the dialog
            if col_index == 0:
                dialog.attributeWidget.idLineEdit.setFocus()
            elif col_index == 1:
                dialog.attributeWidget.nameLineEdit.setFocus()
            elif col_index == 2:
                dialog.metaboliteTab.setFocus()
            elif col_index == 3:
                dialog.attributeWidget.subsystemLineEdit.setFocus()
            elif col_index == 4:
                dialog.attributeWidget.lowerBoundInput.setFocus()
            elif col_index == 5:
                dialog.attributeWidget.upperBoundInput.setFocus()
            elif col_index == 6:
                dialog.attributeWidget.objectiveCoefficientInput.setFocus()

            status = dialog.exec_()
            if status:
                self.dataTable.update_row_from_link(row_index)
                self.dataView.clearSelection()

    @QtCore.pyqtSlot()
    def addItemSlot(self):
        new_reaction = Reaction()
        dialog = ReactionInputDialog(new_reaction, self.model, parent=self)
        status = dialog.exec_()
        if status:
            self.model.add_reaction(new_reaction)
            self.dataTable.update_row_from_item(new_reaction)

    @QtCore.pyqtSlot(QtCore.QPoint)
    def showContextMenu(self, pos):
        menu = QMenu()
        self.add_standard_menu_actions(menu)
        columns = self.dataView.get_selected_columns()
        menu.addSeparator()
        if len(columns) == 1:
            if columns[0] == 3:
                set_subsystem_action = QAction(self.tr("Set Subsystem"), menu)
                set_subsystem_action.triggered.connect(self.set_subsystem)
                menu.addAction(set_subsystem_action)
            elif columns[0] == 4 or columns[0] == 5:
                set_bound_action = QAction(self.tr("Set Bound"), menu)
                set_bound_action.triggered.connect(self.set_flux_bound)
                menu.addAction(set_bound_action)
        if len(columns) > 0:
            set_flux_value_action = QAction(self.tr("Set Flux Value".format(self.data_type)), menu)
            set_flux_value_action.triggered.connect(self.set_flux_value)
            menu.addAction(set_flux_value_action)
        if columns:
            copy_reaction_action = QAction(self.tr("Copy reaction"), menu)
            copy_reaction_action.triggered.connect(self.copy_reaction)
            menu.addAction(copy_reaction_action)

            move_reaction_action = QAction(self.tr("Move reaction"), menu)
            move_reaction_action.triggered.connect(self.move_reaction)
            menu.addAction(move_reaction_action)

        menu.exec_(self.dataView.viewport().mapToGlobal(pos))

    @QtCore.pyqtSlot()
    def set_subsystem(self):
        rows = self.dataView.get_selected_rows()
        subsystem, status = QInputDialog().getText(self, "Set subsystem", "Set subsystem:")
        if status:
            for r in rows:
                item = self.dataTable.item(r, 3)
                item.link.subsystem = subsystem
                item.setText(subsystem)

    @QtCore.pyqtSlot()
    def set_flux_value(self, dialog=None):
        rows = self.dataView.get_selected_rows()
        if dialog is None:
            dialog = SetFluxValueDialog(self)
        if dialog.exec_():
            value, deviation = dialog.user_input
            values = ((1 + (deviation / 100)) * value, (1 - (deviation / 100)) * value)
            upper, lower = max(values), min(values)
            for r in rows:
                item1 = self.dataTable.item(r, 4)
                item2 = self.dataTable.item(r, 5)
                item1.link.lower_bound = lower
                item1.setData(lower, 2)
                item2.link.upper_bound = upper
                item2.setData(upper, 2)

    @QtCore.pyqtSlot()
    def set_flux_bound(self):
        rows = self.dataView.get_selected_rows()
        col = self.dataView.get_selected_columns()[0]
        if col == 4:
            max_value = min([self.dataTable.item(r).link.upper_bound for r in rows])
            min_value = -999999.
        elif col == 5:
            min_value = max([self.dataTable.item(r).link.lower_bound for r in rows])
            max_value = 999999
        else:
            raise ValueError("The selected column for set_flux_bound needs to be 4, or 5!")

        value, status = QInputDialog().getDouble(self, "Set Bound", "New bound value:", 0, min_value, max_value)
        if status:
            self.dataTable.blockSignals(True)
            for row in rows:
                item = self.dataTable.item(row)
                if col == 4:
                    item.link.lower_bound = value
                elif col == 5:
                    item.link.upper_bound = value
                self.dataTable.item(row, 2).setText(item.link.reaction)
                self.dataTable.item(row, col).setData(value, 2)
            self.dataTable.blockSignals(False)
            self.dataTable.all_data_changed()

    @QtCore.pyqtSlot()
    def copy_reaction(self, move=False):
        """ Copy or move reactions between compartmsntes
        
        Parameters
        ----------
        move : bool

        Returns
        -------

        """

        # Get selected items
        rows = self.dataView.get_selected_rows()
        reactions = [self.dataTable.item_from_row(i) for i in rows]

        # Only continue if rows are selected
        if not rows:
            return

        # Collect compartments of metabolites in the selected reactions
        compartments = set()
        for reaction in reactions:
            compartments.update([metabolite.compartment for metabolite in reaction.metabolites])

        # Get compartment mapping from user
        compartment_mapping = dict()
        for compartment in compartments:
            value, status = QInputDialog().getItem(self, "Choose target compartment", 'Choose target for compartment "{}":'.format(compartment), list(self.model.gem_compartments.keys()), 0, False)
            if not status:
                return
            else:
                compartment_mapping[compartment] = value

        progress = QProgressDialog("{} reactions".format("Moving" if move else "Copying"),
                                         "Cancel", 0, len(reactions), self)

        # Copy reactions using matching metabolite from other compartment
        for n, reaction in enumerate(reactions):

            # Check user input and update progress dialog
            if progress.wasCanceled():
                progress.close()
                return
            else:
                progress.setValue(n)
                QApplication.processEvents()

            metabolites = dict()
            # Collect corresponding metabolites in target compartment
            for key, value in reaction.metabolites.items():
                target_compartment = compartment_mapping[key.compartment]

                putative_target_metabolits = find_duplicate_metabolite(key,
                                                                       [x for x in self.model.metabolites if x.compartment == target_compartment],
                                                                       same_compartment=False)

                corresponding_metabolite = None
                if putative_target_metabolits:
                    best_hit, score = putative_target_metabolits[0]
                    if best_hit.compartment == target_compartment and score >= 2.:
                        corresponding_metabolite = best_hit

                if not corresponding_metabolite:
                    corresponding_metabolite = self.model.copy_metabolite(key, target_compartment)

                metabolites[corresponding_metabolite] = value

            # Create new reaction if the move flag is false
            if not move:
                new_reaction = Reaction(id=generate_copy_id(reaction.id, self.model.reactions),
                                        name=reaction.name,
                                        subsystem=reaction.subsystem,
                                        lower_bound=reaction.lower_bound,
                                        upper_bound=reaction.upper_bound,
                                        comment=reaction.comment)
                new_reaction.annotation = reaction.annotation.copy()
                new_reaction.add_metabolites(metabolites)
                self.model.add_reactions([new_reaction])

                # Set objective coefficient after adding reaction to model
                new_reaction.objective_coefficient = reaction.objective_coefficient
                self.model.QtReactionTable.update_row_from_item(new_reaction)

            # Update existing reactions with new metabolites if moving
            else:
                reaction.clear_metabolites()
                reaction.add_metabolites(metabolites)
                self.model.QtReactionTable.update_row_from_link(rows[n])

        progress.close()

    @QtCore.pyqtSlot()
    def move_reaction(self):
        self.copy_reaction(move=True)

    def set_datatable(self):
        if self.model is not None:
            self.dataTable = self.model.QtReactionTable
            self.proxyModel.setSourceModel(self.dataTable)
            header_state = Settings().value("ReactionTableViewState")
            if header_state is not None:
                self.dataView.horizontalHeader().restoreState(header_state)


class MetaboliteTab(StandardTab):

    data_type = "Metabolite"

    def __init__(self):
        StandardTab.__init__(self, ProxyModel=MetaboliteProxyFilter)
        self.dataTable = None

    @QtCore.pyqtSlot()
    def addItemSlot(self):
        MetaboliteEditDialog(self, Metabolite(), self.model).exec_()

    @QtCore.pyqtSlot()
    def editItemSlot(self):
        selected_item = self.dataView.get_selected_indexes(get_first_only=True)
        if selected_item:
            row_index = selected_item[0].row()
            col_index = selected_item[0].column()
            edit_metabolite = self.dataTable.item_from_row(row_index)
            dialog = MetaboliteEditDialog(self, edit_metabolite, self.model)
            if col_index == 0:
                dialog.attributeWidget.iDLineEdit.setFocus()
            elif col_index == 1:
                dialog.attributeWidget.nameLineEdit.setFocus()
            elif col_index == 2:
                dialog.attributeWidget.formulaLineEdit.setFocus()
            elif col_index == 3:
                dialog.attributeWidget.chargeSpinBox.setFocus()
            elif col_index == 4:
                dialog.attributeWidget.compartmentComboBox.setFocus()

            status = dialog.exec_()
            if status:
                self.dataView.clearSelection()

    @QtCore.pyqtSlot()
    def deleteItemSlot(self):
        if self.confirmDeletion():
            metabolites = self.dataView.get_selected_items()
            self.model.gem_remove_metabolites(metabolites)

    def set_datatable(self):
        if self.model is not None:
            self.dataTable = self.model.QtMetaboliteTable
            self.proxyModel.setSourceModel(self.dataTable)
            self.dataTable.set_header()
            header_state = Settings().value("MetaboliteTableViewState")
            if header_state is not None:
                self.dataView.horizontalHeader().restoreState(header_state)

    @QtCore.pyqtSlot()
    def set_charge(self):
        rows = self.dataView.get_selected_rows()
        value, status = QInputDialog().getInt(self, "Set Bound", "New bound value:", 0)
        if status:
            # Set dialog manually in order to prevent dialog popup before user input
            progress = QProgressDialog(self)
            progress.setWindowModality(QtCore.Qt.WindowModal)

            # Keep track of all reactions that need to be updated
            update_reactions = set()
            self.model.QtReactionTable.blockSignals(True)
            self.model.QtMetaboliteTable.blockSignals(True)

            # Update metabolites
            progress.setRange(0, len(rows))
            progress.setLabelText("Changing metabolite..")
            for i, row in enumerate(rows):
                progress.setValue(i)
                QApplication.processEvents()
                metabolite = self.model.QtMetaboliteTable.item(row).link
                if metabolite.charge != value:
                    metabolite.charge = value
                    update_reactions.update(metabolite.reactions)
                    self.model.QtMetaboliteTable.item(row, 3).setData(value, 2)

            # Update reaction table
            progress.setRange(0, len(update_reactions))
            progress.setLabelText("Updating reactions..")
            for i, reaction in enumerate(update_reactions):
                progress.setValue(i)
                QApplication.processEvents()
                reaction.update_balancing_status()
                self.model.QtReactionTable.update_row_from_id(reaction.id)

            # Make views update
            self.model.QtReactionTable.blockSignals(False)
            self.model.QtReactionTable.all_data_changed()
            self.model.QtMetaboliteTable.blockSignals(False)
            self.model.QtMetaboliteTable.all_data_changed()

    @QtCore.pyqtSlot(QtCore.QPoint)
    def showContextMenu(self, pos):
        menu = QMenu()
        self.add_standard_menu_actions(menu)
        columns = self.dataView.get_selected_columns()
        if len(columns) == 1:
            if columns[0] == 3:
                menu.addSeparator()
                set_charge_action = QAction(self.tr("Set Charge"), menu)
                set_charge_action.triggered.connect(self.set_charge)
                menu.addAction(set_charge_action)
        menu.addSeparator()
        copy_action = QAction(self.tr("Copy metabolites"), menu)
        copy_action.triggered.connect(self.copy_metabolites)
        menu.addAction(copy_action)

        menu.exec_(self.dataView.viewport().mapToGlobal(pos))

    @QtCore.pyqtSlot()
    def copy_metabolites(self):
        if self.model:
            compartment, status = QInputDialog.getItem(self, "Choose target", "Compartment:",
                                                             list({metabolite.compartment for metabolite in self.model.metabolites}),
                                                             0,
                                                             False)
            if status:
                metabolites = [self.dataTable.item_from_row(row) for row in self.dataView.get_selected_rows()]
                for metabolite in metabolites:
                    self.model.copy_metabolite(metabolite, compartment)


class GeneTab(StandardTab):

    data_type = "Gene"

    def __init__(self):
        StandardTab.__init__(self, ProxyModel=GeneProxyFilter)
        self.dataTable = None

    @QtCore.pyqtSlot()
    def addItemSlot(self):
        new_gene = Gene()
        dialog = GeneEditDialog(self, new_gene, self.model)
        status = dialog.exec_()
        if status:
            self.model.genes.append(new_gene)
            self.dataTable.update_row_from_item(new_gene)

    @QtCore.pyqtSlot()
    def editItemSlot(self):
        selected_item = self.dataView.get_selected_indexes(get_first_only=True)
        if selected_item:
            row_index = selected_item[0].row()
            col_index = selected_item[0].column()
            edit_gene = self.dataTable.item_from_row(row_index)
            dialog = GeneEditDialog(self, edit_gene, self.model)
            if col_index == 0:
                dialog.attributeWidget.iDLineEdit.setFocus()
            elif col_index == 1:
                dialog.attributeWidget.nameLineEdit.setFocus()
            elif col_index == 2:
                dialog.attributeWidget.genomeLineEdit.setFocus()
            status = dialog.exec_()
            if status:
                self.dataTable.update_row_from_link(row_index)
                self.dataView.clearSelection()

    @QtCore.pyqtSlot()
    def deleteItemSlot(self):
        if self.confirmDeletion():
            genes = self.dataView.get_selected_items()
            self.model.gem_remove_genes(genes)

    def set_datatable(self):
        """ Set the datatable for the proxy model """
        if self.model is not None:
            self.dataTable = self.model.QtGeneTable
            self.proxyModel.setSourceModel(self.dataTable)
            header_state = Settings().value("GenesTableViewState")
            if header_state is not None:
                self.dataView.horizontalHeader().restoreState(header_state)

    def set_genome(self):
        rows = self.dataView.get_selected_rows()
        genome, status = QInputDialog().getText(self, "Set Genome", "Set Genome:")
        if status:
            for r in rows:
                item = self.dataTable.item(r, 2)
                item.link.genome = genome
                item.setText(genome)

    @QtCore.pyqtSlot(QtCore.QPoint)
    def showContextMenu(self, pos):
        menu = QMenu()
        self.add_standard_menu_actions(menu)
        columns = self.dataView.get_selected_columns()
        menu.addSeparator()
        if len(columns) == 1 and columns[0] == 2:
            set_genome_action = QAction(self.tr("Set Genome"), menu)
            set_genome_action.triggered.connect(self.set_genome)
            menu.addAction(set_genome_action)

        menu.exec_(self.dataView.viewport().mapToGlobal(pos))
        return menu


class ReferenceTab(StandardTab):

    data_type = "Reference"

    def __init__(self):
        StandardTab.__init__(self, ProxyModel=ReferenceProxyFilter)
        self.dataTable = None

    @QtCore.pyqtSlot()
    def addItemSlot(self):
        reference = Reference()
        dialog = ReferenceEditDialog(reference)
        status = dialog.exec_()
        if status:
            self.dataTable.update_row_from_item(reference)
            self.model.add_reference(reference)

    @QtCore.pyqtSlot()
    def deleteItemSlot(self):
        if self.confirmDeletion():
            references = self.dataView.get_selected_items()
            self.model.gem_remove_references(references)

    @QtCore.pyqtSlot()
    def editItemSlot(self):
        selected_index = self.dataView.get_selected_indexes(get_first_only=True)
        if selected_index:
            row = selected_index[0].row()
            col = selected_index[0].column()
            reference = self.dataTable.item_from_row(row)
            dialog = ReferenceEditDialog(reference)
            inputs = (dialog.authorTableView, dialog.titleInput, dialog.journalInput, dialog.yearInput,
                      dialog.pmidInput, dialog.pmcInput, dialog.doiInput, dialog.linkInput)
            inputs[col].setFocus()
            status = dialog.exec_()
            if status:
                # Update the tableview to show new values
                self.dataTable.update_row_from_link(row)
                self.dataView.clearSelection()

    def set_datatable(self):
        """ Set the datatable for the proxy model """
        if self.model is not None:
            self.dataTable = self.model.QtReferenceTable
            self.proxyModel.setSourceModel(self.dataTable)
            header_state = Settings().value("ReferenceTableViewState")
            if header_state is not None:
                self.dataView.horizontalHeader().restoreState(header_state)


class ModelTestsTab(StandardTab):

    data_type = "Test"

    def __init__(self):
        StandardTab.__init__(self)
        self.dataTable = None
        self.statusBar = QStatusBar()
        self.horizontalLayout_2.insertWidget(0, self.statusBar)

    @QtCore.pyqtSlot()
    def addItemSlot(self, dialog=None):
        model_test = ModelTest()
        if dialog is None:
            dialog = EditModelTestDialog(self)
        dialog.set_test(model_test, self.model)
        status = dialog.exec_()
        if status:
            self.dataTable.update_row_from_item(model_test)
            self.model.add_test(model_test)

    @QtCore.pyqtSlot()
    def deleteItemSlot(self):
        if self.confirmDeletion():
            selected_tests = self.dataView.get_selected_items()
            self.model.gem_remove_tests(selected_tests)

    @QtCore.pyqtSlot()
    def editItemSlot(self, *args, dialog=None):
        selected_indices = self.dataView.get_selected_indexes()
        if selected_indices:
            # Display result if only an item from the second column was selected
            if len(selected_indices) == 1 and selected_indices[0].column() == 1:
                solution = self.dataTable.itemFromIndex(selected_indices[0]).link
                if solution:
                    solution_dialog = SolutionDialog(solution, self.model)
                    self.model.dialogs.add(solution_dialog)
                    solution_dialog.show()
                    return

            if dialog is None:
                dialog = EditModelTestDialog(self)
            row_index = selected_indices[0].row()
            solution = self.dataTable.item(row_index, 1).link
            dialog.set_test(self.dataTable.item_from_row(row_index), self.model, solution)
            status = dialog.exec_()
            if status:
                self.dataTable.update_row_from_link(row_index)
                self.dataView.clearSelection()

    def set_datatable(self):
        """ Set the datatable for the proxy model """
        if self.model is not None:
            self.dataTable = self.model.QtTestsTable
            self.proxyModel.setSourceModel(self.dataTable)
            header_state = Settings().value("TestsTableViewState")
            if header_state is not None:
                self.dataView.horizontalHeader().restoreState(header_state)

    @QtCore.pyqtSlot()
    def run_selected(self):
        selected_tests = self.dataView.get_selected_items()
        self.run_tests(selected_tests)

    @QtCore.pyqtSlot()
    def run_tests(self, selected=()):
        if not self.model.tests:
            return
        elif not selected:
            # Run all tests if no selection specified
            selected = self.model.tests

        with ProgressDialog(title="Running tests..") as progress:
            try:
                test_results = run_tests(selected, self.model, progress)
            except Exception as e:
                LOGGER.exception("Error running tests")
                QMessageBox().critical(None, "Error", "The following error occured "
                                                      "while running the tests:\n{}".format(str(e)))
                return

            mapping = self.dataTable.get_item_to_row_mapping()

            num_passed = 0
            self.dataTable.blockSignals(True)
            for testcase, result in test_results.items():
                row = mapping[testcase]
                status, solution = result
                if status:
                    num_passed += 1
                self.dataTable.set_status(row, solution, status)
            self.dataTable.blockSignals(False)
            self.dataTable.all_data_changed()

        if num_passed == 0:
            self.statusBar.setStyleSheet("color: red; font-weight: bold;")
        elif num_passed == len(test_results):
            self.statusBar.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.statusBar.setStyleSheet("color: orange; font-weight: bold;")
        self.statusBar.showMessage("{0!s} out of {1!s} tests passed!".format(num_passed, len(test_results)), 4000)

    @QtCore.pyqtSlot(QtCore.QPoint)
    def showContextMenu(self, pos):
        menu = QMenu()
        self.add_standard_menu_actions(menu)

        actions_to_add =[]
        if self.dataView.selectedIndexes():
            run_selected_action = QAction(self.tr("Run selected"), menu)
            run_selected_action.triggered.connect(self.run_selected)
            actions_to_add.append(run_selected_action)

        if self.dataTable.rowCount() > 0:
            run_all_action = QAction(self.tr("Run all"), menu)
            run_all_action.triggered.connect(self.run_tests)
            actions_to_add.append(run_all_action)

        if actions_to_add:
            menu.addSeparator()
            menu.addActions(actions_to_add)

        menu.exec_(self.dataView.viewport().mapToGlobal(pos))


class AnalysesTab(QWidget, Ui_AnalysisTab):

    def __init__(self):
        super(AnalysesTab, self).__init__()
        self.setupUi(self)
        self.model = None

        self.analyses = OrderedDict([("Flux Balance Analysis", self.run_flux_balance_analysis),
                                     ("Parsimonious FBA", self.run_parsimonous),
                                     ("Loopless FBA", self.run_loopless),
                                     ("Flux Variability Analysis", self.run_flux_variability),
                                     ("Single Gene Deletion", self.run_single_gene_deletion),
                                     ("Single Reaction Deletion", self.run_single_reaction_deletion)])
        self.populate_analyses()

        self.solvers = list(cobra.solvers.solver_dict.keys())
        self.populate_solvers()

        self.button_run.setEnabled(False)
        self.combo_solver.setEnabled(False)

        # Connect signals
        self.button_run.clicked.connect(self.run_analysis)
        self.combo_analysis.currentIndexChanged.connect(self.toggle_button)
        self.combo_solver.currentIndexChanged.connect(self.toggle_button)
        self.combo_analysis.currentIndexChanged.connect(self.toggle_solver_selection)
        self.list_solutions.customContextMenuRequested.connect(self.show_context_menu)

    def populate_solvers(self):
        if self.solvers:
            self.combo_solver.addItems(self.solvers)
        else:
            self.combo_solver.clear()
            self.combo_solver.addItem("No solver found!")
            self.combo_solver.setEnabled(False)

    def populate_analyses(self):
        self.combo_analysis.addItems(self.analyses.keys())

    @QtCore.pyqtSlot()
    def toggle_button(self):
        self.button_run.setEnabled(self.combo_solver.currentIndex() != 0 and
                                   self.combo_analysis.currentIndex() != 0)

    @QtCore.pyqtSlot()
    def toggle_solver_selection(self):
        self.combo_solver.setEnabled(self.combo_analysis.currentIndex() != 0)

    @QtCore.pyqtSlot()
    def run_analysis(self):
        if not self.model.objective.expression:
            QMessageBox.warning(self, "Warning",
                                "The objective values of all reactions are 0.", QMessageBox.Ok)
        else:
            selected_analysis = self.combo_analysis.currentText()
            selected_solver = self.combo_solver.currentText()
            self.analyses[selected_analysis](selected_solver)

    def run_flux_balance_analysis(self, selected_solver):
        solution = self.model.optimize()
        solution.method = "fba"
        self.add_solution(solution)

    def run_loopless(self, selected_solver):
        solution = loopless_solution(self.model)
        solution.method = "fba"
        self.add_solution(solution)

    def run_parsimonous(self, selected_solver):
        solution = pfba(self.model)
        solution.method = "fba"
        self.add_solution(solution)

    def run_single_gene_deletion(self, selected_solver):
        solution = single_gene_deletion(self.model)
        solution.method = "single_gene_deletion"
        self.add_solution(solution)

    def run_single_reaction_deletion(self, selected_solver):
        solution = single_reaction_deletion(self.model)
        solution.method = "single_reaction_deletion"
        self.add_solution(solution)

    def run_flux_variability(self, selected_solver):
        solution = flux_variability_analysis(model=self.model, solver=selected_solver)
        solution.method = "fva"
        self.add_solution(solution)

    def open_solution(self, solution):
        dialog = factory_solution(solution.method, self.model, solution)
        self.model.dialogs.add(dialog)
        dialog.show()

    def open_map(self, solution):
        if solution.method != "fba":
            return
        if solution.status != "optimal":
            self.show_infeasible_message(solution)
            return

        for dialog in self.model.dialogs._windows:
            if hasattr(dialog, "set_reaction_data"):
                dialog.set_reaction_data(solution)

    def show_infeasible_message(self, solution):
        QMessageBox.critical(self,
                             self.tr("Error in solution"),
                             self.tr("The solution status is {0}!\n"
                                     "This might be caused by erroneous boundaries or model stoichiometry!".format(
                                     solution.status)), QMessageBox.Ok)
        return

    def set_model(self, model):
        self.model = model
        if model is None:
            self.clear_solutions()

    def clear_solutions(self):
        for r in reversed(range(self.list_solutions.count())):
            self.list_solutions.takeItem(r)

    def add_solution(self, solution, open_solution=True):
        if solution.method == "fba" and solution.status != "optimal":
            self.show_infeasible_message(solution)
            return
        elif self.list_solutions.isEnabled() is False:
            self.list_solutions.clear()
            self.list_solutions.setEnabled(True)
        solution_widget = QListWidgetItem()
        solution_widget.setSizeHint(QSize(solution_widget.sizeHint().width(), 50))
        self.list_solutions.insertItem(0, solution_widget)

        # Setup solution display widget
        display_widget = SolutionWidget(solution)
        display_widget.button_open_solution_table.clicked.connect(self.show_solution_as_table)
        display_widget.button_open_solution_map.clicked.connect(self.show_solution_on_map)
        self.list_solutions.setItemWidget(solution_widget, display_widget)

        if open_solution:
            self.open_solution(solution)

    @QtCore.pyqtSlot()
    def show_solution_on_map(self):
        try:
            solution = self.sender().parent().get_solution()
        except AttributeError:
            return
        else:
            self.open_map(solution)

    @QtCore.pyqtSlot()
    def show_solution_as_table(self):
        try:
            solution = self.sender().parent().get_solution()
        except AttributeError:
            return
        else:
            self.open_solution(solution)

    @QtCore.pyqtSlot()
    def remove_solution(self, item):
        row = self.list_solutions.row(item)
        self.list_solutions.takeItem(row)

    @QtCore.pyqtSlot(QtCore.QPoint)
    def show_context_menu(self, pos):
        item = self.list_solutions.itemAt(pos)
        if item is not None:
            menu = QMenu()
            remove_action = QAction("Remove")
            remove_action.triggered.connect(lambda: self.remove_solution(item))
            menu.addAction(remove_action)
            menu.exec_(self.list_solutions.viewport().mapToGlobal(pos))


class ModelInfoTab(QWidget, Ui_model_stats_tab):
    def __init__(self):
        super(ModelInfoTab, self).__init__()
        self.setupUi(self)

    def set_model(self, model, path):
        self.modelInfoWidget.set_model(model, path)
        self.modelAnnotationWidget.set_model(model)

    def set_path(self, path):
        self.modelInfoWidget.set_path(path)


class SolutionWidget(QWidget, Ui_SolutionTableWidget):
    """ Widget used to display a solution entry

    This widget is used to display the solutions
    in a list of the AnalysisTab. The entry shows
    the status of the solution as well as the
    objective value. Two buttons are displayed:

    1) Open solution dialog
    2) Plot solution in open map dialogs

    """

    def __init__(self, solution=None):
        super(SolutionWidget, self).__init__()
        self.setupUi(self)
        self.solution = solution

        # Add tooltips to buttons
        self.button_open_solution_map.setToolTip("Update open map dialogs with solution")
        self.button_open_solution_table.setToolTip("Open solution dialog")

        self.update_display()

    def update_display(self):
        status, objective = status_objective_from_solution(self.solution)
        set_status_to_label(self.label_status, status)
        set_objective_to_label(self.label_value, objective)
        if self.solution.method != "fba":
            self.button_open_solution_map.setEnabled(False)

    def get_solution(self):
        return self.solution

