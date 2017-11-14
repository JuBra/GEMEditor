from GEMEditor.widgets.model import *
from GEMEditor.widgets.tables import LinkedItem
from PyQt5 import QtCore, QtGui, QtTest
from GEMEditor.cobraClasses import Model, Metabolite, Reaction, Gene, GeneGroup
from GEMEditor.data_classes import *
from GEMEditor.evidence_class import Evidence
import gc
from unittest.mock import Mock
import pytest


# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


class MockSlot(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.called = False
        self.last_caller = None

    @QtCore.pyqtSlot()
    def slot(self):
        self.called = True
        self.last_caller = self.sender()


class TestModelDisplayWidget:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.parent = QWidget()
        self.widget = ModelDisplayWidget(self.parent)

        self.test_id = "Test_model"
        self.test_name = "Test name"
        self.model = Model(self.test_id,
                           name=self.test_name)

        self.comp1_abbrev = "c"
        self.comp1_name = "Cytoplasm"
        self.comp1 = Compartment(self.comp1_abbrev, self.comp1_name)
        self.model.gem_compartments[self.comp1_abbrev] = self.comp1

        self.gene = Gene(id="test_id", name="test_name")
        self.metabolite = Metabolite(id="test_id", compartment="c")
        self.reaction = Reaction(id="test_id")

        self.model.add_metabolites([self.metabolite])
        self.model.add_reactions([self.reaction])
        self.model.genes.append(self.gene)

    def test_setup(self):
        assert len(self.model.metabolites) == 1
        assert len(self.model.reactions) == 1
        assert len(self.model.genes) == 1
        assert self.model.id == self.test_id
        assert self.model.name == self.test_name
        assert self.model.gem_compartments[self.comp1_abbrev] == self.comp1

    def test_model_addition(self):
        path = "Test_path"
        self.widget.set_model(self.model, path=path)

        assert self.widget.label_model_id.text() == self.test_id
        assert self.widget.label_model_name.text() == self.test_name
        assert self.widget.label_number_genes.text() == str(len(self.model.genes))
        assert self.widget.label_number_reactions.text() == str(len(self.model.reactions))
        assert self.widget.label_number_metabolites.text() == str(len(self.model.metabolites))
        assert self.widget.label_model_path.text() == path

    def test_clear_information(self):
        path = "Test_path"
        self.widget.set_model(self.model, path=path)

        self.widget.clear_information()
        assert self.widget.label_model_name.text() == ""
        assert self.widget.label_model_id.text() == ""
        assert self.widget.label_number_reactions.text() == ""
        assert self.widget.label_number_metabolites.text() == ""
        assert self.widget.label_number_genes.text() == ""
        assert self.widget.label_model_path.text() == path

    def test_setting_empty_model(self):
        path = "Test_path"
        self.widget.set_model(self.model, path=path)

        self.widget.set_model(None)
        assert self.widget.label_model_name.text() == ""
        assert self.widget.label_model_id.text() == ""
        assert self.widget.label_number_reactions.text() == ""
        assert self.widget.label_number_metabolites.text() == ""
        assert self.widget.label_number_genes.text() == ""
        assert self.widget.label_model_path.text() == ""


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


class TestAnnotationDislayWidget:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.parent = QWidget()
        self.widget = AnnotationDisplayWidget(self.parent)
        self.empty_reaction = Reaction()

        self.annotated_reaction = Reaction()
        self.annotation = Annotation("chebi", "CHEBI:123454")
        self.annotated_reaction.annotation.add(self.annotation)
        self.model = Model()

    def test_setup(self):
        assert self.widget.dataTable.rowCount() == 0

    def test_setting_empty_reaction(self):

        receiver = MockSlot()
        self.widget.changed.connect(receiver.slot)
        assert receiver.called is False
        assert receiver.last_caller is None

        self.widget.set_item(self.empty_reaction, self.model)

        assert self.widget.dataTable.rowCount() == 0
        assert receiver.called is True

    def test_setting_reaction_with_annotation(self):
        receiver = MockSlot()
        self.widget.changed.connect(receiver.slot)

        self.widget.set_item(self.annotated_reaction, self.model)

        assert self.widget.dataTable.rowCount() == 1
        assert self.widget.dataTable.item(0, 0).text() == self.annotation.collection
        assert self.widget.dataTable.item(0, 1).text() == self.annotation.identifier

        assert receiver.called is True
        assert self.widget.content_changed is False

    def test_change_collection(self):
        receiver = MockSlot()

        self.widget.set_item(self.annotated_reaction, self.model)
        self.widget.changed.connect(receiver.slot)
        assert receiver.called is False
        assert receiver.last_caller is None

        self.widget.dataTable.item(0, 0).setText("kegg")
        assert receiver.called is True
        assert receiver.last_caller is self.widget

    def test_change_identifier(self):
        receiver = MockSlot()

        self.widget.set_item(self.annotated_reaction, self.model)
        self.widget.changed.connect(receiver.slot)
        assert receiver.called is False
        assert receiver.last_caller is None

        self.widget.dataTable.item(0, 1).setText("CHEBI:55555")
        assert receiver.called is True
        assert receiver.last_caller is self.widget

    def test_delete_annotation(self):
        receiver = MockSlot()

        self.widget.set_item(self.annotated_reaction, self.model)
        self.widget.changed.connect(receiver.slot)
        assert receiver.called is False
        assert receiver.last_caller is None

        self.widget.dataTable.setRowCount(0)
        assert receiver.called is True
        assert receiver.last_caller is self.widget

    def test_add_annotation(self):
        receiver = MockSlot()

        self.widget.set_item(self.annotated_reaction, self.model)
        self.widget.changed.connect(receiver.slot)
        assert receiver.called is False
        assert receiver.last_caller is None

        new_annotation = Annotation("kegg", "C91233")

        self.widget.dataTable.update_row_from_item(new_annotation)
        assert receiver.called is True
        assert receiver.last_caller is self.widget

    def test_get_annotation_empty(self):
        assert self.widget.get_annotation() == []

    def test_get_annotation(self):
        self.widget.set_item(self.annotated_reaction, self.model)
        assert self.widget.get_annotation() == [self.annotation]

    def test_save_state(self):
        self.widget.set_item(self.annotated_reaction, self.model)
        new_annotation = Annotation("kegg", "C91233")

        self.widget.dataTable.update_row_from_item(new_annotation)
        assert self.widget.dataTable.rowCount() == 2
        self.widget.save_state()
        assert self.annotated_reaction.annotation == set([self.annotation, new_annotation])


class TestCommentDisplayWidget:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.parent = QWidget()
        self.widget = CommentDisplayWidget(self.parent)
        self.reaction = Reaction()

    def test_setup(self):
        assert self.reaction.comment == ""
        assert self.widget.commentInput.toPlainText() == ""
        assert self.widget.content_changed is False

    def test_set_empty_item(self):
        self.widget.set_item(self.reaction)
        assert self.widget.commentInput.toPlainText() == ""
        assert self.widget.content_changed is False
        assert self.widget.display_item is self.reaction

    def test_set_item_with_comment(self):
        new_comment = "test_comment"
        self.reaction.comment = new_comment

        self.widget.set_item(self.reaction)
        assert self.widget.commentInput.toPlainText() == new_comment
        assert self.widget.content_changed is False

    def test_changing_comment(self):
        new_comment = "test_comment"
        self.widget.set_item(self.reaction)

        QtTest.QTest.keyClicks(self.widget.commentInput, new_comment)

        assert self.widget.content_changed is True
        assert self.widget.commentInput.toPlainText() == new_comment

    def test_changed_emission_upon_typing(self):
        self.widget.set_item(self.reaction)
        detector = MockSlot()
        self.widget.changed.connect(detector.slot)
        assert detector.called is False
        assert detector.last_caller is None

        QtTest.QTest.keyClicks(self.widget.commentInput, "Test")
        assert detector.called is True
        assert detector.last_caller is self.widget

    def test_saving_comment(self):
        new_comment = "test_comment"

        self.widget.set_item(self.reaction)
        assert self.widget.content_changed is False

        self.widget.commentInput.setText(new_comment)
        assert self.widget.content_changed is True

        self.widget.save_state()
        assert self.reaction.comment == new_comment


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
        monkeypatch.setattr("GEMEditor.dialogs.standard.GeneSelectionDialog.exec_", Mock(return_value=False))

    @pytest.fixture()
    def patch_gene_selection_accepted(self, monkeypatch):
        gene = Gene("test")
        monkeypatch.setattr("GEMEditor.dialogs.standard.GeneSelectionDialog.exec_", Mock(return_value=True))
        monkeypatch.setattr("GEMEditor.dialogs.standard.GeneSelectionDialog.selected_items", Mock(return_value=[gene]))
        return gene

    @pytest.fixture()
    def patch_iterate_tree(self, monkeypatch):
        mock = Mock()
        monkeypatch.setattr("GEMEditor.widgets.model.iterate_tree", mock)
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

    def test_add_item_cancelled(self, patch_gene_selection_accepted):
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


class TestEvidenceDisplayWidget:

    def test_setup(self):
        widget = EvidenceDisplayWidget()
        assert widget.dataTable.rowCount() == 0
        assert widget.item is None
        assert widget.model is None
        assert widget.dataView.model() is widget.dataTable
        assert widget.content_changed is False

    def test_set_item(self):
        widget = EvidenceDisplayWidget()
        evidence = Evidence()
        reaction = Reaction()
        model = Model()
        evidence.set_entity(reaction)
        widget.set_item(reaction, model)

        # Check that a copy of the evidence has been added to the table
        assert widget.dataTable.rowCount() == 1
        assert widget.dataTable.item(0).link is not evidence
        assert widget.dataTable.item(0).link.internal_id == evidence.internal_id

    @pytest.fixture()
    def patch_dialog_accepted(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.dialogs.evidence.EditEvidenceDialog.exec_", Mock(return_value=True))

    @pytest.mark.usefixtures("patch_dialog_accepted")
    def test_changed_triggered_addition(self):
        widget = EvidenceDisplayWidget()
        reaction = Reaction()
        model = Model()
        widget.set_item(reaction, model)
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        assert widget.dataTable.rowCount() == 0
        QtTest.QTest.mouseClick(widget.add_button, QtCore.Qt.LeftButton)
        assert widget.dataTable.rowCount() == 1
        assert mock.test.called is True

    @pytest.mark.usefixtures("patch_dialog_accepted")
    def test_changed_triggered_edition(self):
        widget = EvidenceDisplayWidget()
        evidence = Evidence()
        reaction = Reaction()
        model = Model()
        evidence.set_entity(reaction)
        reaction.add_evidence(evidence)
        widget.set_item(reaction, model)
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        assert widget.dataTable.rowCount() == 1
        widget.dataView.selectRow(0)
        widget.edit_item()
        assert widget.dataTable.rowCount() == 1
        assert mock.test.called is True

    def test_changed_triggered_deletion(self):
        widget = EvidenceDisplayWidget()
        evidence = Evidence()
        reaction = Reaction()
        model = Model()
        evidence.set_entity(reaction)
        widget.set_item(reaction, model)
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        assert widget.dataTable.rowCount() == 1
        widget.dataView.selectRow(0)
        QtTest.QTest.mouseClick(widget.delete_button, QtCore.Qt.LeftButton)
        assert widget.dataTable.rowCount() == 0
        assert mock.test.called is True

    def test_saving_changes(self):
        reaction = Reaction()
        gene = Gene()
        reference = Reference()
        model = Model()
        evidence = Evidence(entity=reaction, link=gene)
        evidence.add_reference(reference)
        widget = EvidenceDisplayWidget()

        model.all_evidences[evidence.internal_id] = evidence

        assert evidence in reaction.evidences
        assert evidence in gene.evidences
        assert evidence.internal_id in model.all_evidences
        assert reference in evidence.references

        # Set reaction and model to widget
        widget.set_item(reaction, model)
        assert widget.dataTable.rowCount() == 1

        # Remove evidence copy from data table
        widget.dataTable.setRowCount(0)

        # Setup new evidence item
        new_evidence = Evidence()
        new_evidence.assertion = "Catalyzed by"
        new_evidence.entity = reaction

        gene = Gene("G_id")
        new_evidence.link = gene

        reference = Reference()
        new_evidence.add_reference(reference, reciprocal=False)

        # Test the setup i.e. that items are only linked in a one way (evidence -> item) fashion
        assert new_evidence not in reaction.evidences
        assert new_evidence not in gene.evidences
        assert new_evidence not in reference.linked_items

        # Add new reference to widget table
        widget.dataTable.update_row_from_item(new_evidence)
        assert widget.dataTable.rowCount() == 1
        assert widget.dataTable.item(0).link is new_evidence

        # Action - Save evidences
        widget.save_state()

        # Check that old instance is detached from all links
        assert evidence not in reaction.evidences
        assert evidence not in gene.evidences
        assert evidence.link is None
        assert len(evidence.references) == 0

        # Old evidence still kept alive by this test
        old_id = evidence.internal_id
        assert old_id in model.all_evidences
        evidence = None
        gc.collect()
        assert old_id not in model.all_evidences

        # Check that new evidence is linked properly
        assert new_evidence in reaction.evidences
        assert new_evidence in gene.evidences
        assert new_evidence.internal_id in model.all_evidences


class TestMetaboliteAttributesDisplayWidget:

    def test_setting_item(self):
        metabolite = Metabolite("test_id", "H2O", "Test metabolie", -5, "m")
        model = Model()

        widget = MetaboliteAttributesDisplayWidget()

        # Test prestate
        assert widget.iDLineEdit.text() == ""
        assert widget.nameLineEdit.text() == ""
        assert widget.compartmentComboBox.currentText() == ""
        assert widget.chargeSpinBox.value() == 0
        assert widget.formulaLineEdit.text() == ""

        widget.set_item(metabolite, model)

        assert widget.iDLineEdit.text() == metabolite.id
        assert widget.nameLineEdit.text() == metabolite.name
        assert widget.compartmentComboBox.currentText() == metabolite.compartment
        assert widget.chargeSpinBox.value() == metabolite.charge
        assert widget.formulaLineEdit.text() == metabolite.formula

        assert widget.valid_inputs() is True
        assert widget.content_changed is False

        widget.set_item(None, model)

        assert widget.iDLineEdit.text() == ""
        assert widget.nameLineEdit.text() == ""
        assert widget.compartmentComboBox.currentText() == ""
        assert widget.chargeSpinBox.value() == 0.
        assert widget.formulaLineEdit.text() == ""

        assert widget.valid_inputs() is False
        assert widget.content_changed is False

    def test_save_state(self):

        metabolite = Metabolite()
        model = Model()

        widget = MetaboliteAttributesDisplayWidget()

        widget.set_item(metabolite, model)

        new_id = "New id"
        new_name = "New name"
        new_charge = 3.
        new_compartment = "m"
        new_formula = "H2O"

        widget.iDLineEdit.setText(new_id)
        widget.nameLineEdit.setText(new_name)
        widget.chargeSpinBox.setValue(new_charge)
        widget.compartmentComboBox.addItem(new_compartment)
        widget.compartmentComboBox.setCurrentIndex(widget.compartmentComboBox.count()-1)
        widget.formulaLineEdit.setText(new_formula)

        widget.save_state()

        assert metabolite.id == new_id
        assert metabolite.name == new_name
        assert metabolite.charge == new_charge
        assert metabolite.compartment == new_compartment
        assert metabolite.formula == new_formula

    def test_changed_triggered_by_idchange(self):

        widget = MetaboliteAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.iDLineEdit, "A")
        assert mock.test.called is True

    def test_changed_triggered_by_name_change(self):
        widget = MetaboliteAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.nameLineEdit, "A")
        assert mock.test.called is True

    def test_changed_triggered_by_formula_change(self):
        widget = MetaboliteAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.formulaLineEdit, "A")
        assert mock.test.called is True

    def test_changed_triggered_by_charge_change(self):
        widget = MetaboliteAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.formulaLineEdit, "3")
        assert mock.test.called is True

    def test_changed_triggered_by_compartment_change(self):
        widget = MetaboliteAttributesDisplayWidget()
        mock = Mock()
        widget.compartmentComboBox.addItem("m")
        widget.compartmentComboBox.setCurrentIndex(-1)
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClick(widget.compartmentComboBox, QtCore.Qt.Key_Down)
        assert mock.test.called is True

    def test_valid_input(self):
        # Note: The compartment needs to be set as valid input
        metabolite = Metabolite(id="test", compartment="m")
        model = Model()

        widget = MetaboliteAttributesDisplayWidget()

        widget.set_item(metabolite, model)
        assert widget.valid_inputs() is True
        widget.iDLineEdit.clear()
        assert widget.valid_inputs() is False


class TestGeneAttributesDisplayWidget:

    def test_setting_item(self):
        gene = Gene("test id", "name", "genome")
        model = Model()

        widget = GeneAttributesDisplayWidget()

        # Test prestate
        assert widget.iDLineEdit.text() == ""
        assert widget.nameLineEdit.text() == ""
        assert widget.genomeLineEdit.text() == ""

        widget.set_item(gene, model)

        assert widget.iDLineEdit.text() == gene.id
        assert widget.nameLineEdit.text() == gene.name
        assert widget.genomeLineEdit.text() == gene.genome

        assert widget.valid_inputs() is True
        assert widget.content_changed is False

        widget.set_item(None, model)

        assert widget.iDLineEdit.text() == ""
        assert widget.nameLineEdit.text() == ""
        assert widget.genomeLineEdit.text() == ""

        assert widget.valid_inputs() is False
        assert widget.content_changed is False

    def test_save_state(self):

        gene = Gene()
        model = Model()

        widget = GeneAttributesDisplayWidget()

        widget.set_item(gene, model)

        new_id = "New id"
        new_name = "New name"
        new_genome = "New genome"

        widget.iDLineEdit.setText(new_id)
        widget.nameLineEdit.setText(new_name)
        widget.genomeLineEdit.setText(new_genome)

        widget.save_state()

        assert gene.id == new_id
        assert gene.name == new_name
        assert gene.genome == new_genome

    def test_changed_triggered_by_idchange(self):

        widget = GeneAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.iDLineEdit, "A")
        assert mock.test.called is True

    def test_changed_triggered_by_name_change(self):
        widget = GeneAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.nameLineEdit, "A")
        assert mock.test.called is True

    def test_changed_triggered_by_genome_change(self):
        widget = GeneAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.genomeLineEdit, "A")
        assert mock.test.called is True

    def test_valid_input(self):
        gene = Gene(id="test")
        model = Model()

        widget = GeneAttributesDisplayWidget()

        widget.set_item(gene, model)
        assert widget.valid_inputs() is True
        widget.iDLineEdit.clear()
        assert widget.valid_inputs() is False


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


class TestReactionSettingDisplayWidget:

    def test_setting_item(self):
        parent = QWidget()
        widget = ReactionSettingDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        setting = ReactionSetting(reaction, 1000., -1000., 5.)
        model = Model()

        test.add_setting(setting)

        widget.dataTable.populate_table = Mock()

        widget.set_item(test, model)

        widget.dataTable.populate_table.assert_called_once_with(test.reaction_settings)
        assert widget.model is model
        assert widget.model_test is test

    def test_content_changed(self):
        parent = QWidget()
        widget = ReactionSettingDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        setting = ReactionSetting(reaction, 1000., -1000., 5.)
        model = Model()

        test.add_setting(setting)
        widget.set_item(test, model)

        assert widget.content_changed is False

    def test_saving_items(self):

        parent = QWidget()
        widget = ReactionSettingDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        setting = ReactionSetting(reaction, 1000., -1000., 5.)
        model = Model()

        test.add_setting(setting)
        widget.set_item(test, model)

        new_test = ModelTest()
        widget.model_test = new_test

        assert len(new_test.reaction_settings) == 0
        widget.save_state()
        assert len(new_test.reaction_settings) == 1

        new_setting = list(new_test.reaction_settings)[0]

        assert new_setting == setting
        assert new_setting is not setting

    def test_addition_emits_changed(self):
        parent = QWidget()
        widget = ReactionSettingDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        setting = ReactionSetting(reaction, 1000., -1000., 5.)
        model = Model()

        test.add_setting(setting)
        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.dataTable.update_row_from_item(ReactionSetting(Reaction()))
        assert detector.test.called is True
        assert widget.content_changed is True

    def test_modification_emits_changed(self):
        parent = QWidget()
        widget = ReactionSettingDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        setting = ReactionSetting(reaction, 1000., -1000., 5.)
        model = Model()

        test.add_setting(setting)
        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.dataTable.item(0, 1).setData(500, 2)
        assert detector.test.called is True
        assert widget.content_changed is True

    def test_deletion_emits_changed(self):
        parent = QWidget()
        widget = ReactionSettingDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        setting = ReactionSetting(reaction, 1000., -1000., 5.)
        model = Model()

        test.add_setting(setting)
        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.tableView.selectRow(0)
        QtTest.QTest.mouseClick(widget.button_del_item, QtCore.Qt.LeftButton)
        assert widget.dataTable.rowCount() == 0
        assert detector.test.called is True
        assert widget.content_changed is True


class TestGeneSettingDisplayWidget:

    def test_setting_item(self):
        parent = QWidget()
        widget = GeneSettingDisplayWidget(parent)
        test = ModelTest()
        gene = Gene()
        setting = GeneSetting(gene, False)
        model = Model()

        test.add_setting(setting)

        widget.dataTable.populate_table = Mock()

        widget.set_item(test, model)

        widget.dataTable.populate_table.assert_called_once_with(test.gene_settings)
        assert widget.model is model
        assert widget.model_test is test

    def test_saving_items(self):

        parent = QWidget()
        widget = GeneSettingDisplayWidget(parent)
        test = ModelTest()
        gene = Gene()
        setting = GeneSetting(gene, False)
        model = Model()

        test.add_setting(setting)
        widget.set_item(test, model)

        new_test = ModelTest()
        widget.model_test = new_test

        assert len(new_test.gene_settings) == 0
        widget.save_state()
        assert len(new_test.gene_settings) == 1

        new_setting = list(new_test.gene_settings)[0]

        assert new_setting == setting
        assert new_setting is not setting

    def test_addition_emits_changed(self):
        parent = QWidget()
        widget = GeneSettingDisplayWidget(parent)
        test = ModelTest()
        gene = Gene()
        setting = GeneSetting(gene, False)
        model = Model()

        test.add_setting(setting)
        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.dataTable.update_row_from_item(GeneSetting(Gene(), True))
        assert detector.test.called is True
        assert widget.content_changed is True

    def test_modification_emits_changed(self):
        parent = QWidget()
        widget = GeneSettingDisplayWidget(parent)
        test = ModelTest()
        gene = Gene()
        setting = GeneSetting(gene, True)
        model = Model()

        test.add_setting(setting)
        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.dataTable.item(0, 1).setText("inactive")
        assert detector.test.called is True
        assert widget.content_changed is True

    def test_deletion_emits_changed(self):
        parent = QWidget()
        widget = GeneSettingDisplayWidget(parent)
        test = ModelTest()
        gene = Gene()
        setting = GeneSetting(gene, False)
        model = Model()

        test.add_setting(setting)
        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.tableView.selectRow(0)
        QtTest.QTest.mouseClick(widget.button_del_item, QtCore.Qt.LeftButton)
        assert widget.dataTable.rowCount() == 0
        assert detector.test.called is True
        assert widget.content_changed is True


class TestReferenceDisplayWidget:

    def test_setting_item(self):
        parent = QWidget()
        widget = ReferenceDisplayWidget(parent)
        test = ModelTest()
        model = Model()

        widget.dataTable.populate_table = Mock()

        widget.set_item(test, model)

        widget.dataTable.populate_table.assert_called_once_with(test.references)
        assert widget.model is model
        assert widget.item is test

    def test_saving_items(self):

        parent = QWidget()
        widget = ReferenceDisplayWidget(parent)
        test = ModelTest()
        reference = Reference()
        test.add_reference(reference)

        model = Model()

        widget.set_item(test, model)

        new_test = ModelTest()
        widget.item = new_test

        assert len(new_test.references) == 0
        widget.save_state()
        assert len(new_test.references) == 1

        new_reference = list(new_test.references)[0]

        assert new_reference is reference

    def test_addition_emits_changed(self):
        parent = QWidget()
        widget = ReferenceDisplayWidget(parent)
        test = ModelTest()
        reference = Reference()
        test.add_reference(reference)
        model = Model()

        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.dataTable.update_row_from_item(Reference())
        assert detector.test.called is True
        assert widget.content_changed is True

    def test_deletion_emits_changed(self):
        parent = QWidget()
        widget = ReferenceDisplayWidget(parent)
        test = ModelTest()
        reference = Reference()
        test.add_reference(reference)
        model = Model()

        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.tableView.selectRow(0)
        QtTest.QTest.mouseClick(widget.button_del_item, QtCore.Qt.LeftButton)
        assert widget.dataTable.rowCount() == 0
        assert detector.test.called is True
        assert widget.content_changed is True


class TestOutcomeDisplayWidget:

    def test_setting_item(self):
        parent = QWidget()
        widget = OutcomeDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        outcome = Outcome(reaction, 0., "greater than")
        model = Model()

        test.add_outcome(outcome)

        widget.dataTable.populate_table = Mock()

        widget.set_item(test, model)

        widget.dataTable.populate_table.assert_called_once_with(test.outcomes)
        assert widget.model is model
        assert widget.model_test is test

    def test_saving_items(self):

        parent = QWidget()
        widget = OutcomeDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        outcome = Outcome(reaction, 0., "greater than")
        model = Model()

        test.add_outcome(outcome)
        widget.set_item(test, model)

        new_test = ModelTest()
        widget.model_test = new_test

        assert len(new_test.outcomes) == 0
        widget.save_state()
        assert len(new_test.outcomes) == 1

        new_setting = list(new_test.outcomes)[0]

        assert new_setting == outcome
        assert new_setting is not outcome

    def test_addition_emits_changed(self):

        parent = QWidget()
        widget = OutcomeDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        outcome = Outcome(reaction, 0., "greater than")
        model = Model()

        test.add_outcome(outcome)
        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.dataTable.update_row_from_item(Outcome(Reaction()))
        assert detector.test.called is True
        assert widget.content_changed is True

    def test_modification_emits_changed(self):

        parent = QWidget()
        widget = OutcomeDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        outcome = Outcome(reaction, 0., "greater than")
        model = Model()

        test.add_outcome(outcome)
        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.dataTable.item(0, 1).setText("less than")
        assert detector.test.called is True
        assert widget.content_changed is True

    def test_deletion_emits_changed(self):

        parent = QWidget()
        widget = OutcomeDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        outcome = Outcome(reaction, 0., "greater than")
        model = Model()

        test.add_outcome(outcome)
        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.tableView.selectRow(0)
        QtTest.QTest.mouseClick(widget.button_del_item, QtCore.Qt.LeftButton)
        assert widget.dataTable.rowCount() == 0
        assert detector.test.called is True
        assert widget.content_changed is True