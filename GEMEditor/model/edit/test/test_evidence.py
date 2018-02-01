from unittest.mock import Mock

import pytest
from GEMEditor.model.classes.cobra import Model, Reaction, Gene
from GEMEditor.model.classes.evidence import Evidence
from GEMEditor.model.classes.reference import Reference
from GEMEditor.model.edit.evidence import EditEvidenceDialog
from PyQt5.QtWidgets import QApplication, QWidget

# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestEvidenceInputDialog:

    @pytest.fixture(autouse=True)
    def setup_empty_dialog(self):
        self.widget = QWidget()
        self.model = Model()
        self.reaction = Reaction()
        self.evidence = Evidence()
        self.evidence.entity = self.reaction
        self.dialog = EditEvidenceDialog(self.widget)

    def test_empty_setup(self):

        # Check that all linked items are None
        assert self.dialog.evidence is None
        assert self.dialog.model is None
        assert self.dialog.linked_item is None

        # Check that all labels are emtpy
        assert self.dialog.label_eco.text() == ""
        assert self.dialog.textBox_comment.toPlainText() == ""

        # Assert that the state of the reference table is right
        # Todo: Move check to test case of reference widget
        # assert self.dialog.referenceTab.referenceTable.rowCount() == 0
        # assert self.dialog.referenceView.model() is self.dialog.referenceTable

        # Check that there are as many mapped method options as in the option
        assert self.dialog.comboBox_assertion.count() == 0


    def test_set_current_evidence(self):

        evidence = Evidence(entity=Reaction("id"), eco="ECO:0000ß", assertion="Presence", comment="Comment")
        evidence.add_reference(Reference())

        # Action
        self.dialog.set_evidence(evidence)

        # Check correctness of changes
        assert self.evidence.eco in self.dialog.label_eco.text()
        assert self.dialog.textBox_comment.toPlainText() == evidence.comment

        # Todo: Move to a test of reference display widget
        # assert self.dialog.referenceTable.rowCount() == 1
        # assert self.dialog.referenceTable.get_items() == list(evidence.references)

        # Check that assertion in the corresponding items
        assert self.dialog.options[evidence.entity.__class__] == tuple(self.dialog.comboBox_assertion.itemText(x) for x in range(self.dialog.comboBox_assertion.count()))
        # Check that right assertion is selected
        assert self.dialog.comboBox_assertion.currentText() == self.evidence.assertion

    def test_set_empty_evidence(self):

        # Action
        self.dialog.set_evidence(Evidence())

        assert self.dialog.label_eco.text() == ""
        assert self.dialog.textBox_comment.toPlainText() == ""
        assert self.dialog.comboBox_assertion.currentText() == ""

    def test_save_information(self):

        evidence = Evidence(entity=Reaction(""))
        new_ref = Reference()
        new_eco = "ECO:0000000"

        # Setup
        self.dialog.set_evidence(evidence)

        self.dialog.comboBox_assertion.setCurrentIndex(1)
        self.dialog.textBox_comment.setPlainText("Test comment")

        # Todo: Move to reference widget test
        #self.dialog.referenceTable.populate_table([new_ref])
        self.dialog.set_eco(new_eco)

        # Action
        self.dialog.save_state()

        # Save information
        assert evidence.assertion == self.dialog.comboBox_assertion.currentText()
        assert evidence.comment == self.dialog.textBox_comment.toPlainText()
        # Todo: Move to reference widget test
        # assert evidence.references == set([new_ref])
        assert evidence.eco == new_eco


    # Todo: Replace with test of button status changed
    # def test_content_changed_type(self):
    #     # Test changing of type
    #     assert self.dialog.comboBox.currentIndex() == 0
    #     assert self.dialog.content_changed is False
    #
    #     # Action
    #     self.dialog.comboBox.setCurrentIndex(1)
    #
    #     # Check property
    #     assert self.dialog.content_changed is True

    # Todo: Move to test of reference widget
    # def test_content_changed_reference(self):
    #     # Test changing of reference
    #     assert self.dialog.referenceTable.rowCount() == 0
    #     assert self.dialog.current_evidence.references == []
    #     assert self.dialog.content_changed is False
    #
    #     # Action
    #     self.dialog.referenceTable.update_row_from_item(Reference())
    #
    #     # Check property
    #     assert self.dialog.content_changed is True

    @pytest.fixture()
    def patch_reference_selection_accepted(self, monkeypatch):
        reference = Reference()
        monkeypatch.setattr("GEMEditor.dialogs.standard.ReferenceSelectionDialog", Mock(return_value=Mock(**{"exec_": Mock(return_value=True),
                                                                                                             "selected_items": Mock(return_value=[reference])})))
        return reference

    @pytest.fixture()
    def patch_reference_selection_cancelled(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.dialogs.standard.ReferenceSelectionDialog.exec_", Mock(return_value=False))

    # Todo: Move to test of reference widget
    # @pytest.mark.usefixtures("patch_reference_selection_cancelled")
    # def test_add_reference_cancelled(self):
    #     self.dialog.add_items = Mock()
    #
    #     # Action
    #     self.dialog.add_reference()
    #
    #     # Check that add items has not been called if dialog is cancelled
    #     assert self.dialog.add_items.called is False

    # Todo: Move to test of reference widget
    # def test_add_reference_accepted(self, patch_reference_selection_accepted):
    #     self.dialog.add_items = Mock()
    #
    #     # Action
    #     self.dialog.add_reference()
    #
    #     # Check that add items has not been called if dialog is cancelled
    #     self.dialog.add_items.assert_called_once_with(self.dialog.referenceTable, [patch_reference_selection_accepted])

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
        self.dialog.set_evidence(self.evidence)
        # Test type saving in save state
        self.dialog.comboBox_assertion.addItem("New assertion")
        self.dialog.comboBox_assertion.setCurrentText("New assertion")
        self.dialog.save_state()
        assert self.evidence.assertion == "New assertion"


    # def test_save_changes_references(self):
    #     # Todo: Move to reference widget test
    #     # Todo: Substitute with save_state call
    #     # Setup test conditions
    #     old_reference = Reference()
    #     self.evidence.references = [old_reference]
    #     new_reference = Reference()
    #
    #     # Check prior state
    #     assert self.dialog.referenceTable.rowCount() == 0
    #     self.dialog.referenceTable.update_row_from_item(new_reference)
    #     assert self.dialog.referenceTable.rowCount() == 1
    #
    #     # Action
    #     self.dialog.save_state()
    #
    #     # Check post state
    #     assert self.evidence.references == [new_reference]

    def test_save_comment(self):
        self.dialog.set_evidence(self.evidence)
        new_comment = "Test comment"
        self.dialog.textBox_comment.setPlainText(new_comment)

        # Action
        self.dialog.save_state()

        # Check result
        assert self.evidence.comment == new_comment


class TestEcoSelectionDialog:

    def test_reminder(self):
        # Todo: Implement test
        assert True
