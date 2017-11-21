import pytest
from unittest.mock import Mock
from GEMEditor.base.tables import LinkedItem
from GEMEditor.model.classes.cobra import Metabolite, Model, Reaction, Gene, GeneGroup
from GEMEditor.model.display.reaction import StoichiometryDisplayWidget, GenesDisplayWidget, \
    ReactionAttributesDisplayWidget
from GEMEditor.model.display.test.fixture import MockSlot
from PyQt5 import QtGui, QtCore, QtTest
from PyQt5.QtWidgets import QWidget, QApplication

# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestStoichiometryDisplayWidget:

    @pytest.fixture(autouse=True)
    def setup_items(self):

        self.parent = QWidget()
        self.widget = StoichiometryDisplayWidget(self.parent)
        self.test_met_id = "test_id"
        self.test_react_id = "test_id2"
        self.test_stoich = -1.5
        self.metabolite = Metabolite(id=self.test_met_id)
        self.reaction = Reaction(id=self.test_react_id)
        self.reaction.add_metabolites({self.metabolite: self.test_stoich})
        self.model = Model("test")

    def test_setup(self):
        assert self.widget.dataTable.rowCount() == 0
        assert self.widget.add_button.isEnabled() is True
        assert self.widget.edit_button is None
        assert self.widget.delete_button.isEnabled() is False

        assert self.metabolite.id == self.test_met_id
        assert self.reaction.id == self.test_react_id
        assert self.reaction.metabolites == {self.metabolite: self.test_stoich}

    def test_setting_reaction(self):
        self.widget.set_item(self.reaction, self.model)

        assert self.widget.dataTable.rowCount() == 1
        assert self.widget.dataTable.item(0, 0).text() == self.test_met_id
        assert self.widget.dataTable.item(0, 0).link is self.metabolite
        assert self.widget.dataTable.item(0, 1).data(2) == self.test_stoich
        assert self.widget.dataTable.item(0, 1).link is self.metabolite

    def test_changed(self):
        self.widget.set_item(self.reaction, self.model)

        receiver = MockSlot()
        self.widget.changed.connect(receiver.slot)

        assert self.widget.content_changed is False
        self.widget.dataTable.item(0, 1).setData(12., 2)
        assert self.widget.dataTable.item(0, 1).data(2) == 12.
        assert self.widget.content_changed is True

        assert receiver.called is True
        assert receiver.last_caller is self.widget

    def test_changed2(self):
        self.widget.set_item(self.reaction, self.model)
        new_metabolite = Metabolite("test_2")
        new_stoich = 0.

        receiver = MockSlot()
        self.widget.changed.connect(receiver.slot)
        self.widget.dataTable.update_row_from_item((new_metabolite, new_stoich))

        assert self.widget.content_changed is True
        assert self.widget.dataTable.item(1, 0).text() == new_metabolite.id
        assert self.widget.dataTable.item(1, 0).link is new_metabolite
        assert self.widget.dataTable.item(1, 1).data(2) == new_stoich
        assert self.widget.dataTable.item(1, 1).link is new_metabolite

        assert receiver.called is True
        assert receiver.last_caller is self.widget

    def test_activation_of_delete(self):
        self.widget.set_item(self.reaction, self.model)

        assert self.widget.delete_button.isEnabled() is False
        self.widget.dataView.selectRow(0)
        assert self.widget.delete_button.isEnabled() is True

        self.widget.dataView.clearSelection()
        assert self.widget.delete_button.isEnabled() is False

    def test_balancing_status(self):
        self.widget.set_item(self.reaction, self.model)

        assert self.widget.statusLabel.toolTip() == self.widget.msg_boundary

    def test_balancing_status2(self):
        charge = 0
        formula = "H2O"

        met1 = Metabolite("test1", charge=charge, formula=formula)
        met2 = Metabolite("test2", charge=charge, formula=formula)
        stoichiometry = 1
        reaction = Reaction("test")
        reaction.add_metabolites({met1: stoichiometry,
                                  met2: -stoichiometry})
        self.widget.set_item(reaction, self.model)

        assert self.widget.statusLabel.toolTip() == self.widget.msg_standard.format(status="balanced",
                                                                                    charge="OK",
                                                                                    elements="OK")

    def test_balancing_status3(self):
        charge = 0.
        formula = "H2O"

        met1 = Metabolite("test1", charge=charge, formula=formula)
        met2 = Metabolite("test2", charge=charge+1, formula=formula)
        stoichiometry = 1
        reaction = Reaction("test")
        reaction.add_metabolites({met1: stoichiometry,
                                  met2: -stoichiometry})
        self.widget.set_item(reaction, self.model)

        assert self.widget.statusLabel.toolTip() == self.widget.msg_standard.format(status="unbalanced",
                                                                                    charge="-1.0",
                                                                                    elements="OK")

    def test_get_stoichiometry(self):
        self.widget.set_item(self.reaction, self.model)

        assert self.widget.get_stoichiometry() == self.reaction.metabolites

    def test_get_stoichiometry2(self):
        self.widget.set_item(Reaction(), self.model)

        assert self.widget.get_stoichiometry() == {}

    def test_save_state(self):
        self.widget.set_item(self.reaction, self.model)

        new_stoich = -20.
        self.widget.dataTable.item(0, 1).setData(new_stoich, 2)
        self.widget.save_state()

        assert self.reaction.metabolites == {self.metabolite: new_stoich}


class TestGeneDisplayWidget:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.parent = QWidget()
        self.widget = GenesDisplayWidget(self.parent)
        self.reaction = Reaction("test_id")
        self.model = Model("test model")

    @pytest.fixture()
    def patch_menu_exec(self, monkeypatch):
        monkeypatch.setattr("PyQt5.QtWidgets.QMenu.exec_", Mock())

    @pytest.fixture()
    def patch_gene_selection_cancelled(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.model.selection.gene.GeneSelectionDialog.exec_", Mock(return_value=False))

    @pytest.fixture()
    def patch_gene_selection_accepted(self, monkeypatch):
        gene = Gene("test")
        monkeypatch.setattr("GEMEditor.model.selection.gene.GeneSelectionDialog.exec_", Mock(return_value=True))
        monkeypatch.setattr("GEMEditor.model.selection.gene.GeneSelectionDialog.selected_items", Mock(return_value=[gene]))
        return gene

    @pytest.fixture()
    def patch_iterate_tree(self, monkeypatch):
        mock = Mock()
        monkeypatch.setattr("GEMEditor.model.display.reaction.iterate_tree", mock)
        return mock

    def test_setup(self):
        assert self.widget.geneTable.rowCount() == 0
        assert self.widget.cached_actions == []
        assert self.widget.reaction is None
        assert self.widget.model is None

    def test_set_item(self):
        reaction = Reaction()
        model = Model()
        self.widget.populate_gene_tree = Mock()
        self.widget.clear_information = Mock()
        self.widget.set_item(reaction, model)

        assert self.widget.model is model
        assert self.widget.reaction is reaction
        assert self.widget.populate_gene_tree.called is True
        assert self.widget.clear_information.called is True

    def test_clear_information(self):
        self.widget.cached_actions.append(None)
        self.widget.geneTable.appendRow(QtGui.QStandardItem("Test"))

        assert self.widget.cached_actions != []
        assert self.widget.geneTable.rowCount() == 1
        self.widget.clear_information()
        assert self.widget.cached_actions == []
        assert self.widget.geneTable.rowCount() == 0

    def test_content_changed(self):
        assert self.widget.content_changed is False
        self.widget.cached_actions.append(None)
        assert self.widget.content_changed is True

    def test_save_state(self):
        self.widget.execute_cache = Mock()
        self.widget.save_state()
        assert self.widget.execute_cache.called is True

    def test_get_selected_item_none_selected(self):
        reaction = Reaction()
        model = Model()
        self.widget.set_item(reaction, model)
        assert self.widget.geneTable.rowCount() == 0
        table_item, linked_item = self.widget.get_selected_item()
        assert table_item is self.widget.geneTable
        assert linked_item is reaction

    @pytest.mark.usefixtures("patch_menu_exec")
    def test_context_menu_no_selection(self):
        reaction = Reaction()
        model = Model()
        self.widget.set_item(reaction, model)
        assert self.widget.geneTable.rowCount() == 0
        assert self.widget.get_selected_item()[1] is reaction
        menu = self.widget.show_gene_contextmenu(QtCore.QPoint())
        assert len(menu.actions()) == 2
        assert self.widget.add_gene_action in menu.actions()
        assert self.widget.add_genegroup_action in menu.actions()

    @pytest.mark.usefixtures("patch_menu_exec")
    def test_context_menu_gene(self):
        reaction = Reaction()
        model = Model()
        gene = Gene()
        self.widget.set_item(reaction, model)
        self.widget.geneTable.appendRow(LinkedItem("test", gene))
        assert self.widget.geneTable.rowCount() == 1
        index = self.widget.geneTable.item(0, 0).index()
        self.widget.geneView.setCurrentIndex(index)
        assert self.widget.get_selected_item()[1] is gene
        menu = self.widget.show_gene_contextmenu(QtCore.QPoint())
        assert self.widget.delete_action in menu.actions()

    @pytest.mark.usefixtures("patch_menu_exec")
    def test_context_menu_genegroup(self):
        reaction = Reaction()
        model = Model()
        genegroup = GeneGroup()
        self.widget.set_item(reaction, model)
        self.widget.geneTable.appendRow(LinkedItem("test", genegroup))
        assert self.widget.geneTable.rowCount() == 1
        index = self.widget.geneTable.item(0, 0).index()
        self.widget.geneView.setCurrentIndex(index)
        assert self.widget.get_selected_item()[1] is genegroup
        menu = self.widget.show_gene_contextmenu(QtCore.QPoint())
        assert self.widget.delete_genegroup_action in menu.actions()
        assert self.widget.add_gene_action in menu.actions()
        assert self.widget.add_genegroup_action in menu.actions()

    def test_add_gene(self):
        receiver = MockSlot()
        self.widget.changed.connect(receiver.slot)
        self.widget.set_item(self.reaction, self.model)

        # Check prior state
        assert len(self.widget.cached_actions) == 0
        assert self.widget.geneTable.rowCount() == 0
        assert len(self.reaction._children) == 0

        # Action
        new_gene_id = "test id"
        new_gene = Gene(new_gene_id)
        self.widget.add_gene(new_gene)

        # Check emission of the changed signal
        assert receiver.called is True
        assert receiver.last_caller is self.widget

        # Check cached actions
        assert len(self.widget.cached_actions) == 1
        action = self.widget.cached_actions[0]
        assert action[0] is self.reaction
        assert action[1] == "addition"
        assert action[2] is new_gene

        # Check the table item
        assert self.widget.geneTable.rowCount() == 1
        assert self.widget.geneTable.item(0, 0).text() == new_gene_id
        assert self.widget.geneTable.item(0, 0).link is new_gene

        # Check that no children has been added
        assert len(self.reaction._children) == 0

    def test_add_genegroup(self):
        receiver = MockSlot()
        self.widget.changed.connect(receiver.slot)
        self.widget.set_item(self.reaction, self.model)

        # Check prior state
        assert len(self.widget.cached_actions) == 0
        assert self.widget.geneTable.rowCount() == 0
        assert len(self.reaction._children) == 0

        # Action
        self.widget.add_genegroup()

        # Check emission of the changed signal
        assert receiver.called is True
        assert receiver.last_caller is self.widget

        # Check cached actions
        assert len(self.widget.cached_actions) == 1
        action = self.widget.cached_actions[0]
        assert action[0] is self.reaction
        assert action[1] == "addition"
        assert isinstance(action[2], GeneGroup)

        # Check the table item
        assert self.widget.geneTable.rowCount() == 1
        assert isinstance(self.widget.geneTable.item(0, 0).link, GeneGroup)

        # Check that no children has been added
        assert len(self.reaction._children) == 0

    def test_gene_deletion(self):
        receiver = MockSlot()
        gene = Gene("Test id")
        self.widget.changed.connect(receiver.slot)
        self.reaction.add_child(gene)
        self.widget.set_item(self.reaction, self.model)

        # Check prior state
        assert len(self.widget.cached_actions) == 0
        assert self.widget.geneTable.rowCount() == 1
        assert gene in self.reaction._children

        # Action
        self.widget.geneView.setCurrentIndex(self.widget.geneTable.item(0).index())
        self.widget.delete_item()

        # Check emission of the changed signal
        assert receiver.called is True
        assert receiver.last_caller is self.widget

        # Check cached actions
        assert len(self.widget.cached_actions) == 1
        action = self.widget.cached_actions[0]
        assert action[0] is self.reaction
        assert action[1] == "deletion"
        assert action[2] is gene

        # Check the table item
        assert self.widget.geneTable.rowCount() == 0

        # Check that child is still present
        assert gene in self.reaction._children

    def test_execute_cache(self):

        action = (None, "addition", None)
        self.widget.cached_actions.append(action)
        self.widget.execute_action = Mock()
        self.widget.clear_information = Mock()

        # Action
        self.widget.execute_cache()
        self.widget.execute_action.assert_called_with(action)
        assert self.widget.clear_information.called is True

    def test_execute_action_addition(self):

        action = "addition"

        # Add Gene
        target = Mock()
        gene = Gene()
        self.widget.execute_action((target, action, gene))
        target.add_child.assert_called_once_with(gene)

        # Add GeneGroup
        target = Mock()
        gene_group = GeneGroup()
        self.widget.execute_action((target, action, gene_group))
        target.add_child.assert_called_once_with(gene_group)

    def test_execute_action_deletion(self):
        action = "deletion"

        # Delete Gene
        target = Mock()
        gene = Gene()
        self.widget.execute_action((target, action, gene))
        target.remove_child.assert_called_once_with(gene)

        # Delete GeneGroup
        target = Mock()
        gene_group = GeneGroup()
        gene_group.delete_children = Mock()
        self.widget.execute_action((target, action, gene_group))
        target.remove_child.assert_called_once_with(gene_group)
        assert gene_group.delete_children.called is False

        # Check that children are deleted if genegroup has only one parent
        target = Mock()
        gene_group = GeneGroup()
        gene_group.add_parent(self.reaction)
        gene_group.delete_children = Mock()
        self.widget.execute_action((target, action, gene_group))
        target.remove_child.assert_called_once_with(gene_group)
        assert gene_group.delete_children.called is True

    @pytest.mark.usefixtures("patch_gene_selection_cancelled")
    def test_add_item_cancelled(self):
        # Setup
        self.widget.add_gene = Mock()
        self.widget.set_item(self.reaction, self.model)

        #Action
        self.widget.add_item()

        # Check that add gene has not been called
        assert self.widget.add_gene.called is False

    def test_add_item_accepted(self, patch_gene_selection_accepted):
        # Setup
        self.widget.add_gene = Mock()
        self.widget.set_item(self.reaction, self.model)

        # Action
        self.widget.add_item()

        # Check that add gene was called with the selected gene from
        # the gene selection dialog
        self.widget.add_gene.assert_called_once_with(patch_gene_selection_accepted)

    def test_populate_gene_tree_empty_reaction(self, patch_iterate_tree):
        # Setup
        self.widget.set_item(self.reaction, self.model)

        # Test conditions
        assert len(self.widget.reaction._children) == 0

        # Action
        self.widget.populate_gene_tree()

        # Test outcome
        assert patch_iterate_tree.called is False

    def test_populate_gene_tree_nonempty_reaction(self, patch_iterate_tree):
        # Setup
        self.reaction.add_child(Gene("test"))
        self.widget.set_item(self.reaction, self.model)

        # Test condition
        assert len(self.widget.reaction._children) == 1

        # Action
        self.widget.populate_gene_tree()

        # Test outcome
        patch_iterate_tree.assert_called_with(self.widget.geneTable.invisibleRootItem(), self.reaction)


class TestReactionAttributesDisplayWidget:

    def test_setting_reaction(self):
        widget = ReactionAttributesDisplayWidget()
        reaction = Reaction(id="id", name="name", subsystem="subsystem",
                            lower_bound=-1000., upper_bound=1000.)
        model = Model()
        model.add_reactions((reaction,))
        reaction.objective_coefficient = 1.

        assert widget.idLineEdit.text() == ""
        assert widget.nameLineEdit.text() == ""
        assert widget.subsystemLineEdit.text() == ""
        assert widget.lowerBoundInput.value() == 0.
        assert widget.upperBoundInput.value() == 0.
        assert widget.objectiveCoefficientInput.value() == 0.
        assert widget.content_changed is False
        assert widget.valid_inputs() is False

        widget.set_item(reaction, model)
        assert widget.idLineEdit.text() == reaction.id
        assert widget.nameLineEdit.text() == reaction.name
        assert widget.subsystemLineEdit.text() == reaction.subsystem
        assert widget.lowerBoundInput.value() == reaction.lower_bound
        assert widget.upperBoundInput.value() == reaction.upper_bound
        assert widget.objectiveCoefficientInput.value() == reaction.objective_coefficient
        assert widget.content_changed is False
        assert widget.valid_inputs() is True

    def test_changed_triggered_by_idchange(self):
        widget = ReactionAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.idLineEdit, "A")
        assert mock.test.called is True

    def test_changed_triggered_by_name_change(self):
        widget = ReactionAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.nameLineEdit, "A")
        assert mock.test.called is True

    def test_changed_triggered_by_subsystem_change(self):
        widget = ReactionAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.subsystemLineEdit, "A")
        assert mock.test.called is True

    def test_changed_triggered_by_lower_bound_change(self):
        widget = ReactionAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.lowerBoundInput, "3")
        assert mock.test.called is True

    def test_changed_triggered_by_upper_bound_change(self):
        widget = ReactionAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.upperBoundInput, "3")
        assert mock.test.called is True

    def test_changed_triggered_by_objective_coefficient_change(self):
        widget = ReactionAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.objectiveCoefficientInput, "3")
        assert mock.test.called is True

    def test_setting_id(self):
        widget = ReactionAttributesDisplayWidget()
        model = Model()
        reaction = Reaction()
        widget.set_item(reaction, model)

        assert widget.content_changed is False
        assert widget.valid_inputs() is False
        QtTest.QTest.keyClicks(widget.idLineEdit, "Test")
        assert widget.content_changed is True
        assert widget.valid_inputs() is True

    def test_setting_name(self):
        widget = ReactionAttributesDisplayWidget()
        model = Model()
        reaction = Reaction(id="test")
        widget.set_item(reaction, model)

        assert widget.content_changed is False
        assert widget.valid_inputs() is True
        QtTest.QTest.keyClicks(widget.nameLineEdit, "Test")
        assert widget.content_changed is True
        assert widget.valid_inputs() is True

    def test_setting_subsystem(self):
        widget = ReactionAttributesDisplayWidget()
        model = Model()
        reaction = Reaction(id="id")
        widget.set_item(reaction, model)

        assert widget.content_changed is False
        assert widget.valid_inputs() is True
        QtTest.QTest.keyClicks(widget.subsystemLineEdit, "Test")
        assert widget.content_changed is True
        assert widget.valid_inputs() is True

    def test_setting_lower_bound(self):
        widget = ReactionAttributesDisplayWidget()
        model = Model()
        reaction = Reaction(id="test")
        widget.set_item(reaction, model)
        current_max = widget.lowerBoundInput.maximum()
        current_min = widget.lowerBoundInput.minimum()
        current_max_upper = widget.upperBoundInput.maximum()

        widget.lowerBoundInput.clear()
        QtTest.QTest.keyClicks(widget.lowerBoundInput, "-2000")
        assert widget.lowerBoundInput.value() == -200.
        assert widget.upperBoundInput.minimum() == -200.
        assert widget.lowerBoundInput.maximum() == current_max
        assert widget.lowerBoundInput.minimum() == current_min
        assert widget.upperBoundInput.maximum() == current_max_upper

    def test_setting_upper_bound(self):
        widget = ReactionAttributesDisplayWidget()
        model = Model()
        reaction = Reaction(id="test")
        widget.set_item(reaction, model)
        # Clear input first as spinbox is already at max
        current_max = widget.upperBoundInput.maximum()
        current_min = widget.upperBoundInput.minimum()
        current_min_lower = widget.lowerBoundInput.minimum()

        widget.upperBoundInput.clear()
        QtTest.QTest.keyClicks(widget.upperBoundInput, "500")
        assert widget.upperBoundInput.value() == 500
        assert widget.lowerBoundInput.maximum() == 500.
        assert widget.upperBoundInput.maximum() == current_max
        assert widget.upperBoundInput.minimum() == current_min
        assert widget.lowerBoundInput.minimum() == current_min_lower

    def test_setting_objective_value(self):
        widget = ReactionAttributesDisplayWidget()
        model = Model()
        reaction = Reaction(id="test")
        model.add_reactions((reaction,))
        widget.set_item(reaction, model)

        new_value = 1.
        assert reaction.objective_coefficient != new_value
        widget.objectiveCoefficientInput.clear()
        QtTest.QTest.keyClicks(widget.objectiveCoefficientInput, str(new_value))
        assert widget.objectiveCoefficientInput.value() == new_value
        assert widget.content_changed is True
        assert widget.valid_inputs() is True

    def test_reaction_enormous_bounds(self):
        widget = ReactionAttributesDisplayWidget()
        model = Model()
        reaction = Reaction(id="test", lower_bound=-999999, upper_bound=999999)
        widget.set_item(reaction, model)

        assert widget.lowerBoundInput.value() == -999999
        assert widget.upperBoundInput.value() == 999999
        assert widget.lowerBoundInput.minimum() == -999999
        assert widget.upperBoundInput.maximum() == 999999

    def test_standard_reaction_bounds(self):
        """ Check that bounds are set to standard values when the upper and lower bound are smaller"""
        widget = ReactionAttributesDisplayWidget()
        model = Model()
        reaction = Reaction(lower_bound=-500, upper_bound=100)
        widget.set_item(reaction, model)

        assert widget.lowerBoundInput.value() == -500
        assert widget.lowerBoundInput.maximum() == 100.
        assert widget.lowerBoundInput.minimum() == -1000.

        assert widget.upperBoundInput.value() == 100
        assert widget.upperBoundInput.maximum() == 1000.
        assert widget.upperBoundInput.minimum() == -500.

    def test_saving_changes(self):
        widget = ReactionAttributesDisplayWidget()
        reaction = Reaction("r1")
        model = Model("id")
        model.add_reactions((reaction,))
        widget.set_item(reaction, model)

        new_id = "New id"
        new_name = "New name"
        new_subsytem = "New Subsystem"
        new_upper_bound = 200.5
        new_lower_bound = -300.5
        new_obj_coefficient = 20.4

        widget.idLineEdit.setText(new_id)
        widget.nameLineEdit.setText(new_name)
        widget.subsystemLineEdit.setText(new_subsytem)
        widget.upperBoundInput.setValue(new_upper_bound)
        widget.lowerBoundInput.setValue(new_lower_bound)
        widget.objectiveCoefficientInput.setValue(new_obj_coefficient)

        # Action
        widget.save_state()

        # Check that inputs are saved
        assert reaction.id == new_id
        assert reaction.name == new_name
        assert reaction.subsystem == new_subsytem
        assert reaction.lower_bound == new_lower_bound
        assert reaction.upper_bound == new_upper_bound
        assert reaction.objective_coefficient == new_obj_coefficient

    def test_valid_input(self):
        reaction = Reaction(id="test")
        model = Model()

        widget = ReactionAttributesDisplayWidget()

        widget.set_item(reaction, model)
        assert widget.valid_inputs() is True
        widget.idLineEdit.clear()
        assert widget.valid_inputs() is False