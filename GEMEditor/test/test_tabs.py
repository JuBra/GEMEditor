import pytest
import PyQt5
from GEMEditor.tabs import *
from cobra.core.solution import LegacySolution
from GEMEditor.cobraClasses import Model, Reaction, Metabolite, Gene
from GEMEditor.data_classes import ModelTest, ReactionSetting, Outcome, Reference
from GEMEditor.dialogs.mock import MockModelTestDialog
from PyQt5 import QtCore, QtTest
from PyQt5.QtWidgets import QApplication, QErrorMessage
from unittest.mock import Mock


# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


@pytest.fixture()
def monkeypatch_proxymodel_setfilterfixedstring(monkeypatch):
    monkeypatch.setattr("PyQt5.QtCore.QSortFilterProxyModel.setFilterFixedString", Mock())


class TestStandardTab:

    @pytest.fixture()
    def monkeypatch_button_slots(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.tabs.StandardTab.addItemSlot", Mock())
        monkeypatch.setattr("GEMEditor.tabs.StandardTab.editItemSlot", Mock())
        monkeypatch.setattr("GEMEditor.tabs.StandardTab.deleteItemSlot", Mock())

    @pytest.mark.usefixtures("monkeypatch_proxymodel_setfilterfixedstring")
    def test_typing_search_field_changes_filterstring(self):
        """ Check that the filter string entered into the search input is set
        to the filtersortproxy model """
        tab = StandardTab()
        QtTest.QTest.keyClicks(tab.searchInput, "Test")
        tab.proxyModel.setFilterFixedString.assert_called_with("Test")

    @pytest.mark.usefixtures("monkeypatch_button_slots")
    def test_add_button_triggering(self):
        tab = StandardTab()
        assert tab.addItemSlot.called is False
        QtTest.QTest.mouseClick(tab.addItemButton, QtCore.Qt.LeftButton)
        assert tab.addItemSlot.called is True

    @pytest.mark.usefixtures("monkeypatch_button_slots")
    def test_edit_button_triggering(self):
        tab = StandardTab()
        assert tab.editItemSlot.called is False
        QtTest.QTest.mouseClick(tab.editItemButton, QtCore.Qt.LeftButton)
        assert tab.editItemSlot.called is True

    @pytest.mark.usefixtures("monkeypatch_button_slots")
    def test_del_button_triggering(self):
        tab = StandardTab()
        assert tab.deleteItemSlot.called is False
        QtTest.QTest.mouseClick(tab.deleteItemButton, QtCore.Qt.LeftButton)
        assert tab.deleteItemSlot.called is True

    def test_setup(self):
        tab = StandardTab()
        assert tab.filterComboBox.isHidden() is True
        assert tab.label_filter.isHidden() is True
        assert tab.line.isHidden() is True


class TestReactionTab:

    @pytest.fixture()
    def patch_button_slots(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.tabs.ReactionTab.addItemSlot", Mock())
        monkeypatch.setattr("GEMEditor.tabs.ReactionTab.editItemSlot", Mock())
        monkeypatch.setattr("GEMEditor.tabs.ReactionTab.deleteItemSlot", Mock())

    @pytest.fixture()
    def patched_remove_reactions(self, monkeypatch):
        mock = Mock()
        monkeypatch.setattr("GEMEditor.cobraClasses.Model.remove_reactions", mock)
        return mock

    @pytest.fixture()
    def patch_edit_dialog_true(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.dialogs.reaction.ReactionInputDialog.exec_", Mock(return_value=True))

    @pytest.fixture()
    def patch_edit_dialog_false(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.dialogs.reaction.ReactionInputDialog.exec_", Mock(return_value=False))

    def test_setup(self):
        tab = ReactionTab()

        # Check that the reaction filter part is not hidden
        assert tab.filterComboBox.isHidden() is False
        assert tab.label_filter.isHidden() is False
        assert tab.line.isHidden() is False

    @pytest.mark.usefixtures("patch_button_slots")
    def test_add_button_triggering(self):
        tab = ReactionTab()
        assert tab.addItemSlot.called is False
        QtTest.QTest.mouseClick(tab.addItemButton, QtCore.Qt.LeftButton)
        assert tab.addItemSlot.called is True

    @pytest.mark.usefixtures("patch_button_slots")
    def test_edit_button_triggering(self):
        tab = ReactionTab()
        assert tab.editItemSlot.called is False
        QtTest.QTest.mouseClick(tab.editItemButton, QtCore.Qt.LeftButton)
        assert tab.editItemSlot.called is True

    @pytest.mark.usefixtures("patch_button_slots")
    def test_del_button_triggering(self):
        tab = ReactionTab()
        assert tab.deleteItemSlot.called is False
        QtTest.QTest.mouseClick(tab.deleteItemButton, QtCore.Qt.LeftButton)
        assert tab.deleteItemSlot.called is True

    @pytest.mark.usefixtures("monkeypatch_proxymodel_setfilterfixedstring")
    def test_typing_search_field_changes_filterstring(self):
        """ Check that the filter string entered into the search input is set
        to the filtersortproxy model """
        tab = ReactionTab()
        QtTest.QTest.keyClicks(tab.searchInput, "Test")
        tab.proxyModel.setFilterFixedString.assert_called_with("Test")

    @pytest.mark.parametrize("user_response", [True, False])
    def test_user_asked_upon_deletion(self, user_response, patched_remove_reactions):
        tab = ReactionTab()
        tab.set_model(Model())
        tab.confirmDeletion = Mock(return_value=user_response)
        tab.dataView.delete_selected_rows = Mock()
        assert tab.confirmDeletion.called is False
        assert patched_remove_reactions.called is False
        assert tab.dataView.delete_selected_rows.called is False
        tab.deleteItemSlot()
        assert tab.confirmDeletion.called is True
        assert patched_remove_reactions.called is user_response
        assert tab.dataView.delete_selected_rows.called is user_response

    @pytest.mark.parametrize("user_response", [True, False])
    def test_deletion(self, user_response):
        tab = ReactionTab()
        model = Model()
        reaction1 = Reaction("r1")
        reaction2 = Reaction("r2")
        reaction3 = Reaction("r3")
        model.add_reactions([reaction1, reaction2, reaction3])
        model.setup_reaction_table()
        assert len(model.reactions) == model.QtReactionTable.rowCount() == 3
        tab.set_model(model)
        tab.confirmDeletion = Mock(return_value=user_response)

        item = tab.dataTable.item(1, 0)
        selected_reaction = item.link
        source_index = tab.dataTable.indexFromItem(item)
        view_index = tab.proxyModel.mapFromSource(source_index)
        tab.dataView.selectRow(view_index.row())

        assert tab.confirmDeletion.called is False
        tab.deleteItemSlot()
        assert tab.confirmDeletion.called is True
        assert (selected_reaction in model.reactions) is not user_response
        assert tab.dataTable.findItems(selected_reaction.id) is not user_response
        if user_response:
            assert len(model.reactions) == model.QtReactionTable.rowCount() == 2

    @pytest.mark.usefixtures("patch_edit_dialog_true")
    def test_add_item_dialog_accept(self):
        tab = ReactionTab()
        model = Model()
        model.add_reaction = Mock()
        model.QtReactionTable.update_row_from_item = Mock()
        tab.set_model(model)

        assert model.add_reaction.called is False
        assert model.QtReactionTable.update_row_from_item.called is False
        tab.addItemSlot()
        assert model.add_reaction.called is True
        assert model.QtReactionTable.update_row_from_item.called is True

    @pytest.mark.usefixtures("patch_edit_dialog_false")
    def test_add_item_dialog_reject(self):
        tab = ReactionTab()
        model = Model()
        model.add_reaction = Mock()
        model.QtReactionTable.update_row_from_item = Mock()
        tab.set_model(model)

        assert model.add_reaction.called is False
        assert model.QtReactionTable.update_row_from_item.called is False
        tab.addItemSlot()
        assert model.add_reaction.called is False
        assert model.QtReactionTable.update_row_from_item.called is False

    @pytest.mark.usefixtures("patch_edit_dialog_true")
    def test_modify_item_accept(self):
        tab = ReactionTab()
        model = Model()
        model.QtReactionTable.update_row_from_link = Mock()
        reaction = Reaction(id="old_id")
        model.add_reactions([reaction])
        model.setup_reaction_table()
        tab.set_model(model)

        tab.dataView.selectRow(0)
        assert model.QtReactionTable.update_row_from_link.called is False
        tab.editItemSlot()
        assert model.QtReactionTable.update_row_from_link.called is True

    @pytest.mark.usefixtures("patch_edit_dialog_false")
    def test_modify_item_reject(self):
        tab = ReactionTab()
        model = Model()
        model.QtReactionTable.update_row_from_link = Mock()
        reaction = Reaction(id="old_id")
        model.add_reactions([reaction])
        model.setup_reaction_table()
        tab.set_model(model)

        tab.dataView.selectRow(0)
        assert model.QtReactionTable.update_row_from_link.called is False
        tab.editItemSlot()
        assert model.QtReactionTable.update_row_from_link.called is False


class TestMetaboliteTab:

    @pytest.fixture()
    def patch_button_slots(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.tabs.MetaboliteTab.addItemSlot", Mock())
        monkeypatch.setattr("GEMEditor.tabs.MetaboliteTab.editItemSlot", Mock())
        monkeypatch.setattr("GEMEditor.tabs.MetaboliteTab.deleteItemSlot", Mock())

    @pytest.fixture()
    def patch_edit_dialog_true(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.dialogs.metabolite.MetaboliteEditDialog.exec_", Mock(return_value=True))

    @pytest.fixture()
    def patch_edit_dialog_false(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.dialogs.metabolite.MetaboliteEditDialog.exec_", Mock(return_value=False))

    def test_setup(self):
        tab = MetaboliteTab()

        # Check that the filter part is not hidden
        assert tab.filterComboBox.isHidden() is False
        assert tab.label_filter.isHidden() is False
        assert tab.line.isHidden() is False

    @pytest.mark.usefixtures("patch_button_slots")
    def test_add_button_triggering(self):
        tab = MetaboliteTab()
        assert tab.addItemSlot.called is False
        QtTest.QTest.mouseClick(tab.addItemButton, QtCore.Qt.LeftButton)
        assert tab.addItemSlot.called is True

    @pytest.mark.usefixtures("patch_button_slots")
    def test_edit_button_triggering(self):
        tab = MetaboliteTab()
        assert tab.editItemSlot.called is False
        QtTest.QTest.mouseClick(tab.editItemButton, QtCore.Qt.LeftButton)
        assert tab.editItemSlot.called is True

    @pytest.mark.usefixtures("patch_button_slots")
    def test_del_button_triggering(self):
        tab = MetaboliteTab()
        assert tab.deleteItemSlot.called is False
        QtTest.QTest.mouseClick(tab.deleteItemButton, QtCore.Qt.LeftButton)
        assert tab.deleteItemSlot.called is True

    @pytest.mark.usefixtures("monkeypatch_proxymodel_setfilterfixedstring")
    def test_typing_search_field_changes_filterstring(self):
        """ Check that the filter string entered into the search input is set
        to the filtersortproxy model """
        tab = MetaboliteTab()
        QtTest.QTest.keyClicks(tab.searchInput, "Test")
        tab.proxyModel.setFilterFixedString.assert_called_with("Test")

    @pytest.mark.parametrize("user_response", [True, False])
    def test_user_asked_upon_deletion(self, user_response):
        tab = MetaboliteTab()
        tab.set_model(Model())
        tab.confirmDeletion = Mock(return_value=user_response)
        tab.dataView.delete_selected_rows = Mock()
        assert tab.confirmDeletion.called is False
        assert tab.dataView.delete_selected_rows.called is False
        tab.deleteItemSlot()
        assert tab.confirmDeletion.called is True
        assert tab.dataView.delete_selected_rows.called is user_response

    @pytest.mark.parametrize("user_response", [True, False])
    def test_deletion(self, user_response):
        tab = MetaboliteTab()
        model = Model()
        metabolite1 = Metabolite("m1")
        metabolite2 = Metabolite("m2")
        metabolite3 = Metabolite("m3")
        model.add_metabolites([metabolite1, metabolite2, metabolite3])
        model.setup_metabolite_table()
        assert len(model.metabolites) == model.QtMetaboliteTable.rowCount() == 3
        tab.set_model(model)
        tab.confirmDeletion = Mock(return_value=user_response)

        item = tab.dataTable.item(1, 0)
        selected_metabolite = item.link
        source_index = tab.dataTable.indexFromItem(item)
        view_index = tab.proxyModel.mapFromSource(source_index)
        tab.dataView.selectRow(view_index.row())

        assert tab.confirmDeletion.called is False
        tab.deleteItemSlot()
        assert tab.confirmDeletion.called is True
        assert (selected_metabolite in model.metabolites) is not user_response
        assert tab.dataTable.findItems(selected_metabolite.id) is not user_response
        if user_response:
            assert len(model.metabolites) == model.QtMetaboliteTable.rowCount() == 2

    @pytest.mark.usefixtures("patch_edit_dialog_true")
    def test_add_item_dialog_accept(self):
        tab = MetaboliteTab()
        model = Model()
        model.add_metabolites = Mock()
        model.QtMetaboliteTable.update_row_from_item = Mock()
        tab.set_model(model)

        assert model.add_metabolites.called is False
        assert model.QtMetaboliteTable.update_row_from_item.called is False
        tab.addItemSlot()
        assert model.add_metabolites.called is True
        assert model.QtMetaboliteTable.update_row_from_item.called is True

    @pytest.mark.usefixtures("patch_edit_dialog_false")
    def test_add_item_dialog_reject(self):
        tab = MetaboliteTab()
        model = Model()
        model.add_metabolites = Mock()
        model.QtMetaboliteTable.update_row_from_item = Mock()
        tab.set_model(model)

        assert model.add_metabolites.called is False
        assert model.QtMetaboliteTable.update_row_from_item.called is False
        tab.addItemSlot()
        assert model.add_metabolites.called is False
        assert model.QtMetaboliteTable.update_row_from_item.called is False

    @pytest.mark.usefixtures("patch_edit_dialog_true")
    def test_edit_item_dialog_accept(self):
        tab = MetaboliteTab()
        model = Model()
        metabolite1 = Metabolite("m1")
        model.add_metabolites([metabolite1])
        model.setup_metabolite_table()
        model.QtMetaboliteTable.update_row_from_link = Mock()
        tab.set_model(model)
        tab.dataView.selectRow(0)
        assert model.QtMetaboliteTable.update_row_from_link.called is False
        tab.editItemSlot()
        assert model.QtMetaboliteTable.update_row_from_link.called is True

    @pytest.mark.usefixtures("patch_edit_dialog_false")
    def test_edit_item_dialog_reject(self):
        tab = MetaboliteTab()
        model = Model()
        metabolite1 = Metabolite("m1")
        model.add_metabolites([metabolite1])
        model.setup_metabolite_table()
        model.QtMetaboliteTable.update_row_from_link = Mock()
        tab.set_model(model)
        tab.dataView.selectRow(0)
        assert model.QtMetaboliteTable.update_row_from_link.called is False
        tab.editItemSlot()
        assert model.QtMetaboliteTable.update_row_from_link.called is False

    def test_set_bulk_charge(self):
        # Todo: Implement test
        assert True


class TestGeneTab:

    @pytest.fixture()
    def patch_button_slots(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.tabs.GeneTab.addItemSlot", Mock())
        monkeypatch.setattr("GEMEditor.tabs.GeneTab.editItemSlot", Mock())
        monkeypatch.setattr("GEMEditor.tabs.GeneTab.deleteItemSlot", Mock())

    @pytest.fixture()
    def patch_edit_dialog_true(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.dialogs.gene.GeneEditDialog.exec_", Mock(return_value=True))

    @pytest.fixture()
    def patch_edit_dialog_false(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.dialogs.gene.GeneEditDialog.exec_", Mock(return_value=False))

    def test_setup(self):
        tab = GeneTab()

        # Check that the filter part is not hidden
        assert tab.filterComboBox.isHidden() is False
        assert tab.label_filter.isHidden() is False
        assert tab.line.isHidden() is False

    @pytest.mark.usefixtures("patch_button_slots")
    def test_add_button_triggering(self):
        tab = GeneTab()
        assert tab.addItemSlot.called is False
        QtTest.QTest.mouseClick(tab.addItemButton, QtCore.Qt.LeftButton)
        assert tab.addItemSlot.called is True

    @pytest.mark.usefixtures("patch_button_slots")
    def test_edit_button_triggering(self):
        tab = GeneTab()
        assert tab.editItemSlot.called is False
        QtTest.QTest.mouseClick(tab.editItemButton, QtCore.Qt.LeftButton)
        assert tab.editItemSlot.called is True

    @pytest.mark.usefixtures("patch_button_slots")
    def test_del_button_triggering(self):
        tab = GeneTab()
        assert tab.deleteItemSlot.called is False
        QtTest.QTest.mouseClick(tab.deleteItemButton, QtCore.Qt.LeftButton)
        assert tab.deleteItemSlot.called is True

    @pytest.mark.usefixtures("monkeypatch_proxymodel_setfilterfixedstring")
    def test_typing_search_field_changes_filterstring(self):
        """ Check that the filter string entered into the search input is set
        to the filtersortproxy model """
        tab = GeneTab()
        QtTest.QTest.keyClicks(tab.searchInput, "Test")
        tab.proxyModel.setFilterFixedString.assert_called_with("Test")

    @pytest.mark.parametrize("user_response", [True, False])
    def test_user_asked_upon_deletion(self, user_response):
        tab = GeneTab()
        tab.set_model(Model())
        tab.confirmDeletion = Mock(return_value=user_response)
        tab.dataView.delete_selected_rows = Mock()
        assert tab.confirmDeletion.called is False
        assert tab.dataView.delete_selected_rows.called is False
        tab.deleteItemSlot()
        assert tab.confirmDeletion.called is True
        assert tab.dataView.delete_selected_rows.called is user_response

    @pytest.mark.parametrize("user_response", [True, False])
    def test_deletion(self, user_response):
        tab = GeneTab()
        model = Model()
        gene1 = Gene("r1")
        gene2 = Gene("r2")
        gene3 = Gene("r3")
        model.add_gene(gene1)
        model.add_gene(gene2)
        model.add_gene(gene3)
        model.setup_gene_table()
        assert len(model.genes) == model.QtGeneTable.rowCount() == 3
        tab.set_model(model)
        tab.confirmDeletion = Mock(return_value=user_response)

        item = tab.dataTable.item(1, 0)
        selected_gene = item.link
        source_index = tab.dataTable.indexFromItem(item)
        view_index = tab.proxyModel.mapFromSource(source_index)
        tab.dataView.selectRow(view_index.row())

        assert tab.confirmDeletion.called is False
        tab.deleteItemSlot()
        assert tab.confirmDeletion.called is True
        assert (selected_gene in model.genes) is not user_response
        assert tab.dataTable.findItems(selected_gene.id) is not user_response
        if user_response:
            assert len(model.genes) == model.QtGeneTable.rowCount() == 2

    @pytest.mark.usefixtures("patch_edit_dialog_true")
    def test_add_item_dialog_accept(self):
        tab = GeneTab()
        model = Model()
        model.genes.append = Mock()
        model.QtGeneTable.update_row_from_item = Mock()
        tab.set_model(model)

        assert model.genes.append.called is False
        assert model.QtGeneTable.update_row_from_item.called is False
        tab.addItemSlot()
        assert model.genes.append.called is True
        assert model.QtGeneTable.update_row_from_item.called is True

    @pytest.mark.usefixtures("patch_edit_dialog_false")
    def test_add_item_dialog_reject(self):
        tab = GeneTab()
        model = Model()
        model.genes.append = Mock()
        model.QtGeneTable.update_row_from_item = Mock()
        tab.set_model(model)

        assert model.genes.append.called is False
        assert model.QtGeneTable.update_row_from_item.called is False
        tab.addItemSlot()
        assert model.genes.append.called is False
        assert model.QtGeneTable.update_row_from_item.called is False

    @pytest.mark.usefixtures("patch_edit_dialog_true")
    def test_edit_item_dialog_accept(self):
        tab = GeneTab()
        model = Model()
        gene1 = Gene("r1")
        model.add_gene(gene1)
        model.setup_gene_table()
        model.QtGeneTable.update_row_from_link = Mock()
        tab.set_model(model)
        tab.dataView.selectRow(0)
        assert model.QtGeneTable.update_row_from_link.called is False
        tab.editItemSlot()
        assert model.QtGeneTable.update_row_from_link.called is True

    @pytest.mark.usefixtures("patch_edit_dialog_false")
    def test_edit_item_dialog_reject(self):
        tab = GeneTab()
        model = Model()
        gene1 = Gene("r1")
        model.add_gene(gene1)
        model.setup_gene_table()
        model.QtGeneTable.update_row_from_link = Mock()
        tab.set_model(model)
        tab.dataView.selectRow(0)
        assert model.QtGeneTable.update_row_from_link.called is False
        tab.editItemSlot()
        assert model.QtGeneTable.update_row_from_link.called is False

    def test_set_genome(self):
        # Todo: implement test
        assert True

    def test_showContextMenu(self):
        # Todo: implement test
        assert True


# Todo: Clean up tests - Remove mock dialog
# class TestModelTestsTab:
#
#     @pytest.fixture()
#     def patch_button_slots(self, monkeypatch):
#         monkeypatch.setattr("GEMEditor.tabs.ModelTestsTab.addItemSlot", Mock())
#         monkeypatch.setattr("GEMEditor.tabs.ModelTestsTab.editItemSlot", Mock())
#         monkeypatch.setattr("GEMEditor.tabs.ModelTestsTab.deleteItemSlot", Mock())
#
#     @pytest.fixture()
#     def patch_edit_dialog_true(self, monkeypatch):
#         monkeypatch.setattr("GEMEditor.dialogs.modeltest.EditModelTestDialog.exec_", Mock(return_value=True))
#
#     @pytest.fixture()
#     def patch_edit_dialog_false(self, monkeypatch):
#         monkeypatch.setattr("GEMEditor.dialogs.modeltest.EditModelTestDialog.exec_", Mock(return_value=False))
#
#     @pytest.fixture()
#     def patch_solvers_none(self, monkeypatch):
#         monkeypatch.setattr("cobra.solvers", Mock(solver_dict={}))
#         monkeypatch.setattr("PyQt5.QtWidgets.QErrorMessage", Mock())
#
#     @pytest.fixture()
#     def patch_solvers_gurobi(self, monkeypatch):
#         monkeypatch.setattr("cobra.solvers", Mock(solver_dict={"gurobi": None}))
#         monkeypatch.setattr("PyQt5.QtWidgets.QErrorMessage", Mock())
#
#     @pytest.fixture()
#     def patch_getitem_accept_gurobi(self, monkeypatch):
#         monkeypatch.setattr("PyQt5.QtWidgets.QInputDialog.getItem", Mock(return_value=("gurobi", True)))
#         monkeypatch.setattr("PyQt5.QtWidgets.QErrorMessage", Mock())
#
#     @pytest.fixture()
#     def patch_getitm_reject(self, monkeypatch):
#         monkeypatch.setattr("PyQt5.QtWidgets.QInputDialog.getItem", Mock(return_value=(None, False)))
#         monkeypatch.setattr("PyQt5.QtWidgets.QErrorMessage", Mock())
#
#     @pytest.fixture()
#     def patch_run_test_infeasible(self, monkeypatch):
#         monkeypatch.setattr("GEMEditor.tabs.run_test", Mock(return_value=(False, LegacySolution(f=None,
#                                                                                           status="infeasible"))))
#
#     @pytest.fixture()
#     def patch_run_test_passed(self, monkeypatch):
#         monkeypatch.setattr("GEMEditor.tabs.run_test", Mock(return_value=(True, LegacySolution(f=None,
#                                                                                          status="optimal"))))
#
#     @pytest.fixture()
#     def patch_run_test_failed(self, monkeypatch):
#         monkeypatch.setattr("GEMEditor.tabs.run_test", Mock(return_value=(False, LegacySolution(f=None,
#                                                                                           status="optimal"))))
#
#     @pytest.fixture(autouse=True)
#     def setup_items(self):
#         self.tab = ModelTestsTab()
#         self.model = Model()
#         self.model.setup_tables()
#         self.test_description = "Test_name"
#         self.test_case = ModelTest(description=self.test_description)
#         self.reaction1 = Reaction(id="r1")
#         self.setting = ReactionSetting(reaction=self.reaction1, upper_bound=1000., lower_bound=0., objective_coefficient=0.)
#         self.reaction2 = Reaction(id="r2")
#         self.outcome = Outcome(reaction=self.reaction2, value=0., operator="greater than")
#         self.test_case.add_outcome(self.outcome)
#         self.test_case.add_setting(self.setting)
#
#         self.tab.set_model(self.model)
#
#         self.mock_return_test_case = MockModelTestDialog(return_value=1)
#
#     @pytest.fixture()
#     def setup_new_test(self):
#         self.new_description = "test test"
#         self.new_test_case = ModelTest(description=self.new_description)
#         self.new_outcome = Outcome(self.reaction1, value=555., operator="less than")
#         self.new_setting = ReactionSetting(self.reaction2, upper_bound=888., lower_bound=444., objective_coefficient=0.599)
#         self.new_test_case.add_outcome(self.new_outcome)
#         self.new_test_case.add_setting(self.new_setting)
#
#     def test_setup_items(self):
#         assert self.model.QtTestsTable is not None
#         assert self.model.QtTestsTable.rowCount() == 0
#
#         assert self.tab.model is self.model
#
#     def test_setup(self):
#         tab = ModelTestsTab()
#
#         # Check that the filter part is not hidden
#         assert tab.filterComboBox.isHidden() is True
#         assert tab.label_filter.isHidden() is True
#         assert tab.line.isHidden() is True
#
#     def test_add_test_case(self):
#
#         mock_dialog = MockModelTestDialog(example_item=self.test_case)
#         self.tab.addItemSlot(dialog=mock_dialog)
#
#         assert self.model.QtTestsTable.rowCount() == 1
#         assert self.model.QtTestsTable.item(0, 0).link is not self.test_case
#         assert self.tab.dataTable.rowCount() == 1
#         assert self.tab.dataTable.item(0, 0).link is not self.test_case
#         assert self.tab.dataTable.item(0, 0).link is self.model.QtTestsTable.item(0, 0).link
#
#         new_testcase = self.tab.dataTable.item(0, 0).link
#         assert new_testcase.outcomes == self.test_case.outcomes
#         assert new_testcase.all_settings() == self.test_case.all_settings()
#         assert new_testcase.description == self.test_case.description
#
#     @pytest.mark.usefixtures("setup_new_test")
#     def test_modify_test_case(self):
#
#         self.tab.dataTable.update_row_from_item(self.test_case)
#         assert self.tab.dataTable.rowCount() == 1
#
#         self.tab.dataView.selectRow(0)
#         mock_dialog = MockModelTestDialog(example_item=self.new_test_case)
#         self.tab.editItemSlot(dialog=mock_dialog)
#
#         assert self.tab.dataTable.item(0, 0).link is self.test_case
#         assert self.tab.dataTable.item(0, 0).text() == self.new_description
#         assert self.test_case.description == self.new_description
#         assert self.test_case.settings == self.new_test_case.settings
#         assert self.test_case.outcomes == self.new_test_case.outcomes
#
#     @pytest.mark.usefixtures("patch_button_slots")
#     def test_add_button_triggering(self):
#         tab = ModelTestsTab()
#         assert tab.addItemSlot.called is False
#         QtTest.QTest.mouseClick(tab.addItemButton, QtCore.Qt.LeftButton)
#         assert tab.addItemSlot.called is True
#
#     @pytest.mark.usefixtures("patch_button_slots")
#     def test_edit_button_triggering(self):
#         tab = ModelTestsTab()
#         assert tab.editItemSlot.called is False
#         QtTest.QTest.mouseClick(tab.editItemButton, QtCore.Qt.LeftButton)
#         assert tab.editItemSlot.called is True
#
#     @pytest.mark.usefixtures("patch_button_slots")
#     def test_del_button_triggering(self):
#         tab = ModelTestsTab()
#         assert tab.deleteItemSlot.called is False
#         QtTest.QTest.mouseClick(tab.deleteItemButton, QtCore.Qt.LeftButton)
#         assert tab.deleteItemSlot.called is True
#
#     @pytest.mark.usefixtures("monkeypatch_proxymodel_setfilterfixedstring")
#     def test_typing_search_field_changes_filterstring(self):
#         """ Check that the filter string entered into the search input is set
#         to the filtersortproxy model """
#         tab = ModelTestsTab()
#         QtTest.QTest.keyClicks(tab.searchInput, "Test")
#         tab.proxyModel.setFilterFixedString.assert_called_with("Test")
#
#     @pytest.mark.parametrize("user_response", [True, False])
#     def test_user_asked_upon_deletion(self, user_response):
#         tab = ModelTestsTab()
#         tab.set_model(Model())
#         tab.confirmDeletion = Mock(return_value=user_response)
#         tab.dataView.delete_selected_rows = Mock()
#         assert tab.confirmDeletion.called is False
#         assert tab.dataView.delete_selected_rows.called is False
#         tab.deleteItemSlot()
#         assert tab.confirmDeletion.called is True
#         assert tab.dataView.delete_selected_rows.called is user_response
#
#     @pytest.mark.parametrize("user_response", [True, False])
#     def test_deletion(self, user_response):
#         tab = ModelTestsTab()
#         model = Model()
#         test1 = ModelTest(description="t1")
#         test2 = ModelTest(description="t2")
#         test3 = ModelTest(description="t3")
#         model.add_test(test1)
#         model.add_test(test2)
#         model.add_test(test3)
#         model.setup_tests_table()
#         assert len(model.tests) == model.QtTestsTable.rowCount() == 3
#         tab.set_model(model)
#         tab.confirmDeletion = Mock(return_value=user_response)
#
#         item = tab.dataTable.item(1, 0)
#         selected_test = item.link
#         source_index = tab.dataTable.indexFromItem(item)
#         view_index = tab.proxyModel.mapFromSource(source_index)
#         tab.dataView.selectRow(view_index.row())
#
#         assert tab.confirmDeletion.called is False
#         tab.deleteItemSlot()
#         assert tab.confirmDeletion.called is True
#         assert (selected_test in model.tests) is not user_response
#         assert tab.dataTable.findItems(selected_test.description) is not user_response
#         if user_response:
#             assert model.QtTestsTable.rowCount() == 2
#
#     @pytest.mark.usefixtures("patch_edit_dialog_true")
#     def test_add_item_dialog_accept(self):
#         tab = ModelTestsTab()
#         model = Model()
#         model.add_test = Mock()
#         model.QtTestsTable.update_row_from_item = Mock()
#         tab.set_model(model)
#
#         assert model.add_test.called is False
#         assert model.QtTestsTable.update_row_from_item.called is False
#         tab.addItemSlot()
#         assert model.add_test.called is True
#         assert model.QtTestsTable.update_row_from_item.called is True
#
#     @pytest.mark.usefixtures("patch_edit_dialog_false")
#     def test_add_item_dialog_reject(self):
#         tab = ModelTestsTab()
#         model = Model()
#         model.add_test = Mock()
#         model.QtTestsTable.update_row_from_item = Mock()
#         tab.set_model(model)
#
#         assert model.add_test.called is False
#         assert model.QtTestsTable.update_row_from_item.called is False
#         tab.addItemSlot()
#         assert model.add_test.called is False
#         assert model.QtTestsTable.update_row_from_item.called is False
#
#     @pytest.mark.usefixtures("patch_edit_dialog_true")
#     def test_edit_item_dialog_accept(self):
#         tab = ModelTestsTab()
#         model = Model()
#         test = ModelTest()
#         model.add_test(test)
#         model.setup_tests_table()
#         model.QtTestsTable.update_row_from_link = Mock()
#         tab.set_model(model)
#         tab.dataView.selectRow(0)
#         assert model.QtTestsTable.update_row_from_link.called is False
#         tab.editItemSlot()
#         assert model.QtTestsTable.update_row_from_link.called is True
#
#     @pytest.mark.usefixtures("patch_edit_dialog_false")
#     def test_edit_item_dialog_reject(self):
#         tab = ModelTestsTab()
#         model = Model()
#         test = ModelTest()
#         model.add_test(test)
#         model.setup_tests_table()
#         model.QtTestsTable.update_row_from_link = Mock()
#         tab.set_model(model)
#         tab.dataView.selectRow(0)
#         assert model.QtTestsTable.update_row_from_link.called is False
#         tab.editItemSlot()
#         assert model.QtTestsTable.update_row_from_link.called is False
#
#     @pytest.mark.usefixtures("patch_solvers_none")
#     def test_run_tests_no_solvers(self):
#         tab = ModelTestsTab()
#         assert PyQt5.QtWidgets.QErrorMessage.called is False
#         tab.run_tests()
#         assert PyQt5.QtWidgets.QErrorMessage.called is True
#
#     @pytest.mark.usefixtures("patch_solvers_gurobi", "patch_getitm_reject")
#     def test_run_tests_gurobi_reject(self):
#         tab = ModelTestsTab()
#         tab.set_model(self.model)
#         tab.dataTable.rowCount = Mock()
#         assert PyQt5.QtWidgets.QErrorMessage.called is False
#         tab.dataTable.rowCount.called is False
#         tab.run_tests()
#         assert PyQt5.QtWidgets.QErrorMessage.called is False
#         tab.dataTable.rowCount.called is False
#
#     @pytest.mark.usefixtures("patch_solvers_gurobi", "patch_getitem_accept_gurobi")
#     def test_run_tests_gurobi_accept(self):
#         tab = ModelTestsTab()
#         tab.set_model(self.model)
#         tab.dataTable.rowCount = Mock(return_value=0)
#         assert PyQt5.QtWidgets.QErrorMessage.called is False
#         tab.dataTable.rowCount.called is False
#         tab.run_tests()
#         assert PyQt5.QtWidgets.QErrorMessage.called is False
#         tab.dataTable.rowCount.called is True
#
#     @pytest.mark.usefixtures("patch_run_test_infeasible", "patch_solvers_gurobi", "patch_getitem_accept_gurobi")
#     def test_test_infeasible(self):
#         tab = ModelTestsTab()
#         model = Model()
#         model.setup_tests_table()
#         tab.set_model(model)
#         tab.dataTable.update_row_from_item(ModelTest())
#         assert tab.dataTable.rowCount() == 1
#         assert tab.dataTable.item(0, 1).text() == ""
#         tab.run_tests()
#         assert tab.dataTable.item(0, 1).text() == "infeasible"
#
#     @pytest.mark.usefixtures("patch_run_test_failed", "patch_solvers_gurobi", "patch_getitem_accept_gurobi")
#     def test_test_failed(self):
#         tab = ModelTestsTab()
#         model = Model()
#         model.setup_tests_table()
#         tab.set_model(model)
#         tab.dataTable.update_row_from_item(ModelTest())
#         assert tab.dataTable.rowCount() == 1
#         assert tab.dataTable.item(0, 1).text() == ""
#         tab.run_tests()
#         assert tab.dataTable.item(0, 1).text() == "Failed"
#
#     @pytest.mark.usefixtures("patch_run_test_passed", "patch_solvers_gurobi", "patch_getitem_accept_gurobi")
#     def test_test_passed(self):
#         tab = ModelTestsTab()
#         model = Model()
#         model.setup_tests_table()
#         tab.set_model(model)
#         tab.dataTable.update_row_from_item(ModelTest())
#         assert tab.dataTable.rowCount() == 1
#         assert tab.dataTable.item(0, 1).text() == ""
#         tab.run_tests()
#         assert tab.dataTable.item(0, 1).text() == "Passed"


class TestReferenceTab:

    @pytest.fixture()
    def patch_button_slots(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.tabs.ReferenceTab.addItemSlot", Mock())
        monkeypatch.setattr("GEMEditor.tabs.ReferenceTab.editItemSlot", Mock())
        monkeypatch.setattr("GEMEditor.tabs.ReferenceTab.deleteItemSlot", Mock())

    @pytest.fixture()
    def patch_edit_dialog_true(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.dialogs.reference.ReferenceEditDialog.exec_", Mock(return_value=True))

    @pytest.fixture()
    def patch_edit_dialog_false(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.dialogs.reference.ReferenceEditDialog.exec_", Mock(return_value=False))

    def test_setup(self):
        tab = ReferenceTab()

        # Check that the filter part is not hidden
        assert tab.filterComboBox.isHidden() is True
        assert tab.label_filter.isHidden() is True
        assert tab.line.isHidden() is True

    @pytest.mark.usefixtures("patch_button_slots")
    def test_add_button_triggering(self):
        tab = ReferenceTab()
        assert tab.addItemSlot.called is False
        QtTest.QTest.mouseClick(tab.addItemButton, QtCore.Qt.LeftButton)
        assert tab.addItemSlot.called is True

    @pytest.mark.usefixtures("patch_button_slots")
    def test_edit_button_triggering(self):
        tab = ReferenceTab()
        assert tab.editItemSlot.called is False
        QtTest.QTest.mouseClick(tab.editItemButton, QtCore.Qt.LeftButton)
        assert tab.editItemSlot.called is True

    @pytest.mark.usefixtures("patch_button_slots")
    def test_del_button_triggering(self):
        tab = ReferenceTab()
        assert tab.deleteItemSlot.called is False
        QtTest.QTest.mouseClick(tab.deleteItemButton, QtCore.Qt.LeftButton)
        assert tab.deleteItemSlot.called is True

    @pytest.mark.usefixtures("monkeypatch_proxymodel_setfilterfixedstring")
    def test_typing_search_field_changes_filterstring(self):
        """ Check that the filter string entered into the search input is set
        to the filtersortproxy model """
        tab = ReferenceTab()
        QtTest.QTest.keyClicks(tab.searchInput, "Test")
        tab.proxyModel.setFilterFixedString.assert_called_with("Test")

    @pytest.mark.parametrize("user_response", [True, False])
    def test_user_asked_upon_deletion(self, user_response):
        tab = ReferenceTab()
        tab.set_model(Model())
        tab.confirmDeletion = Mock(return_value=user_response)
        tab.dataView.delete_selected_rows = Mock()
        assert tab.confirmDeletion.called is False
        assert tab.dataView.delete_selected_rows.called is False
        tab.deleteItemSlot()
        assert tab.confirmDeletion.called is True
        assert tab.dataView.delete_selected_rows.called is user_response

    @pytest.mark.parametrize("user_response", [True, False])
    def test_deletion(self, user_response):
        tab = ReferenceTab()
        model = Model()
        reference1 = Reference("r1")
        reference2 = Reference("r2")
        reference3 = Reference("r3")
        model.add_reference(reference1)
        model.add_reference(reference2)
        model.add_reference(reference3)
        model.setup_reference_table()
        assert len(model.references) == model.QtReferenceTable.rowCount() == 3
        tab.set_model(model)
        tab.confirmDeletion = Mock(return_value=user_response)

        item = tab.dataTable.item(1, 0)
        selected_reference = item.link
        source_index = tab.dataTable.indexFromItem(item)
        view_index = tab.proxyModel.mapFromSource(source_index)
        tab.dataView.selectRow(view_index.row())

        assert tab.confirmDeletion.called is False
        tab.deleteItemSlot()
        assert tab.confirmDeletion.called is True
        assert (selected_reference.id in model.references) is not user_response
        if user_response:
            assert len(model.references) == model.QtReferenceTable.rowCount() == 2

    @pytest.mark.usefixtures("patch_edit_dialog_true")
    def test_add_item_dialog_accept(self):
        tab = ReferenceTab()
        model = Model()
        model.add_reference = Mock()
        model.QtReferenceTable.update_row_from_item = Mock()
        tab.set_model(model)

        assert model.add_reference.called is False
        assert model.QtReferenceTable.update_row_from_item.called is False
        tab.addItemSlot()
        assert model.add_reference.called is True
        assert model.QtReferenceTable.update_row_from_item.called is True

    @pytest.mark.usefixtures("patch_edit_dialog_false")
    def test_add_item_dialog_reject(self):
        tab = ReferenceTab()
        model = Model()
        model.add_reference = Mock()
        model.QtReferenceTable.update_row_from_item = Mock()
        tab.set_model(model)

        assert model.add_reference.called is False
        assert model.QtReferenceTable.update_row_from_item.called is False
        tab.addItemSlot()
        assert model.add_reference.called is False
        assert model.QtReferenceTable.update_row_from_item.called is False

    @pytest.mark.usefixtures("patch_edit_dialog_true")
    def test_edit_item_dialog_accept(self):
        tab = ReferenceTab()
        model = Model()
        reference = Reference()
        model.add_reference(reference)
        model.setup_reference_table()
        model.QtReferenceTable.update_row_from_link = Mock()
        tab.set_model(model)
        tab.dataView.selectRow(0)
        assert model.QtReferenceTable.update_row_from_link.called is False
        tab.editItemSlot()
        assert model.QtReferenceTable.update_row_from_link.called is True

    @pytest.mark.usefixtures("patch_edit_dialog_false")
    def test_edit_item_dialog_reject(self):
        tab = ReferenceTab()
        model = Model()
        reference = Reference()
        model.add_reference(reference)
        model.setup_reference_table()
        model.QtReferenceTable.update_row_from_item = Mock()
        tab.set_model(model)
        tab.dataView.selectRow(0)
        assert model.QtReferenceTable.update_row_from_item.called is False
        tab.editItemSlot()
        assert model.QtReferenceTable.update_row_from_item.called is False
