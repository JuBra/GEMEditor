import gc
from unittest.mock import Mock

import pytest
from GEMEditor.model.classes.annotation import Annotation
from GEMEditor.model.classes.cobra import Model
from GEMEditor.model.classes.modeltest import ModelTest
from GEMEditor.model.classes.reference import Reference
from GEMEditor.model.display.base import AnnotationDisplayWidget, CommentDisplayWidget, EvidenceDisplayWidget, \
    ReferenceDisplayWidget
from GEMEditor.widgets.test.test_model_widgets import MockSlot
from PyQt5 import QtTest, QtCore


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
        monkeypatch.setattr("GEMEditor.model.edit.evidence.EditEvidenceDialog.exec_", Mock(return_value=True))

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