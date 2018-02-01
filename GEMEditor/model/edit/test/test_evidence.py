import pytest
from unittest.mock import Mock
from GEMEditor.model.classes.cobra import Model, Reaction, Gene
from GEMEditor.model.classes.evidence import Evidence
from GEMEditor.model.classes.reference import Reference
from GEMEditor.model.edit.evidence import EditEvidenceDialog
from PyQt5.QtWidgets import QApplication

# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestEvidenceInputDialog:

    @pytest.fixture(autouse=True)
    def setup_empty_dialog(self):
        self.model = Model()
        self.evidence = Evidence()
        self.entity = Gene("g1")
        self.assertion = "Catalyzing reaction"
        self.target = Reaction("r1")
        self.eco = "ECO:0000250"
        self.comment = "Similarity to XY"
        self.reference = Reference()

        self.dialog = EditEvidenceDialog()

    def complete_evidence(self):
        evidence = Evidence(entity=self.entity,
                            assertion=self.assertion,
                            target=self.target,
                            eco=self.eco,
                            comment=self.comment)
        evidence.add_reference(self.reference)
        return evidence

    def test_empty_setup(self):
        dialog = self.dialog

        # Check that labels are emtpy
        assert not dialog.label_target.text()
        assert not dialog.label_eco.text()
        assert not dialog.textBox_comment.toPlainText()
        assert dialog.combo_assertion.count() == 0

    def test_labels_updated(self):
        dialog = self.dialog
        dialog.referenceWidget.set_item = Mock()
        evidence = self.complete_evidence()

        # Action
        dialog.set_evidence(evidence, None)

        # Check labels
        assert dialog.label_target.text() == evidence.target.id
        assert evidence.eco in dialog.label_eco.text()
        assert dialog.textBox_comment.toPlainText() == evidence.comment
        assert dialog.combo_assertion.currentText() == evidence.assertion

        # Check that combobox shows appropriate choices
        assert self.dialog.options[evidence.entity.__class__] == tuple(
            self.dialog.combo_assertion.itemText(x) for x in range(self.dialog.combo_assertion.count()))

        # Check references are updated
        dialog.referenceWidget.set_item.assert_called_with(evidence, None)

    def test_changes_are_saved(self):
        dialog = self.dialog
        evidence = Evidence(entity=self.entity)
        dialog.set_evidence(evidence, None)

        # Generate new values
        assert self.dialog.combo_assertion.currentIndex() == -1
        new_assertion = self.dialog.combo_assertion.itemText(1)
        new_target = Reaction("r2")
        new_comment = "Comment"
        new_eco = "ECO:0000000"

        # Set new values
        self.dialog.set_assertion(new_assertion)
        self.dialog.set_eco(new_eco)
        self.dialog.set_target(new_target)
        self.dialog.set_comment(new_comment)
        self.dialog.referenceWidget.dataTable.update_row_from_item(self.reference)

        # Action
        self.dialog.save_state()

        # Check updates
        assert evidence.target is new_target
        assert evidence in new_target.evidences

        assert evidence.comment == new_comment
        assert evidence.eco == new_eco
        assert evidence.assertion == new_assertion

        assert self.reference in evidence.references
        assert evidence in self.reference.linked_items


    @pytest.fixture()
    def patch_gene_selection_accepted(self, monkeypatch):
        gene = Gene()
        monkeypatch.setattr("GEMEditor.dialogs.evidence.GeneSelectionDialog", Mock(return_value=Mock(**{"exec_": Mock(return_value=True),
                                                                                                        "selected_items": Mock(return_value=[gene])})))
        return gene

    @pytest.fixture()
    def patch_gene_selection_cancelled(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.dialogs.evidence.GeneSelectionDialog.exec_", Mock(return_value=False))

    # Todo: Reimplement
    # def test_add_gene_accepted(self, patch_gene_selection_accepted):
    #     self.dialog.set_evidence(self.evidence)
    #
    #     # Action
    #     self.dialog.add_link()
    #
    #     # Check that add items has not been called if dialog is cancelled
    #     self.dialog.add_items.assert_called_once_with(self.dialog.itemTable, [patch_gene_selection_accepted])
    #
    # @pytest.mark.usefixtures("patch_gene_selection_cancelled")
    # def test_add_gene_cancelled(self):
    #     self.dialog.add_items = Mock()
    #
    #     # Action
    #     self.dialog.ad
    #
    #     # Check that add items has not been called if dialog is cancelled
    #     assert self.dialog.add_items.called is False

    # Todo: Implement button toggling when redesigning dialog
    # def test_toggle_button_true(self):
    #     # Prior state
    #     assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False
    #
    #     # Action
    #     self.dialog.comboBox.setCurrentIndex(1)
    #
    #     # Test changes
    #     assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True
    #
    #     # Action2
    #     self.dialog.comboBox.setCurrentIndex(0)
    #
    #     # Test revert change
    #     assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False

    def test_save_changes_assertion(self):
        self.dialog.set_evidence(self.evidence, None)
        # Test type saving in save state
        self.dialog.combo_assertion.addItem("New assertion")
        self.dialog.combo_assertion.setCurrentText("New assertion")
        self.dialog.save_state()
        assert self.evidence.assertion == "New assertion"


class TestEcoSelectionDialog:

    def test_reminder(self):
        # Todo: Implement test
        assert True
