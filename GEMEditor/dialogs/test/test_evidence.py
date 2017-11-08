import pytest
from GEMEditor.dialogs.evidence import EditEvidenceDialog
from GEMEditor.cobraClasses import Model, Reaction, Gene
from GEMEditor.data_classes import Reference
from GEMEditor.evidence_class import Evidence
from PyQt5.QtWidgets import QApplication, QWidget, QDialogButtonBox
from unittest.mock import Mock


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
        assert self.dialog.label_link.text() == ""
        assert self.dialog.textBox_comment.toPlainText() == ""

        # Assert that the state of the reference table is right
        assert self.dialog.referenceTable.rowCount() == 0
        assert self.dialog.referenceView.model() is self.dialog.referenceTable

        # Check that there are as many mapped mehtod options as in the option
        assert self.dialog.comboBox_assertion.count() == 0

        # Check that the stacked widgets is on the first tab
        assert self.dialog.stackedWidget.currentIndex() == 0

    def test_set_current_evidence(self):

        evidence = Evidence(entity=Reaction("id"), link=Gene("test"), term="Term", eco="ECO:0000ß", assertion="Presence", comment="Comment")
        evidence.add_reference(Reference())

        # Action
        self.dialog.set_evidence(evidence)

        # Check correctness of changes
        assert self.dialog.lineEdit_term.text() == evidence.term
        assert self.evidence.eco in self.dialog.label_eco.text()
        assert self.dialog.textBox_comment.toPlainText() == evidence.comment
        assert self.dialog.label_link.text() == evidence.link.id
        assert self.dialog.referenceTable.rowCount() == 1
        assert self.dialog.referenceTable.get_items() == list(evidence.references)

        # Check that assertion in the corresponding items
        assert self.dialog.options[evidence.entity.__class__] == tuple(self.dialog.comboBox_assertion.itemText(x) for x in range(self.dialog.comboBox_assertion.count()))
        # Check that right assertion is selected
        assert self.dialog.comboBox_assertion.currentText() == self.evidence.assertion

    def test_set_empty_evidence(self):

        # Action
        self.dialog.set_evidence(Evidence())

        assert self.dialog.lineEdit_term.text() == ""
        assert self.dialog.label_eco.text() == ""
        assert self.dialog.textBox_comment.toPlainText() == ""
        assert self.dialog.label_link.text() == ""
        assert self.dialog.referenceTable.rowCount() == 0
        assert self.dialog.comboBox_assertion.currentText() == ""

    def test_save_information(self):

        evidence = Evidence(entity=Reaction(""))
        new_ref = Reference()
        new_link = Gene()
        new_eco = "ECO:0000000"

        # Setup
        self.dialog.set_evidence(evidence)

        self.dialog.comboBox_assertion.setCurrentIndex(1)
        self.dialog.textBox_comment.setPlainText("Test comment")
        self.dialog.referenceTable.populate_table([new_ref])
        self.dialog.set_linked_item(new_link)
        self.dialog.comboBox.setCurrentIndex(1)
        self.dialog.set_eco(new_eco)

        # Action
        self.dialog.save_state()

        # Save information
        assert evidence.assertion == self.dialog.comboBox_assertion.currentText()
        assert evidence.comment == self.dialog.textBox_comment.toPlainText()
        assert evidence.references == set([new_ref])
        assert evidence.link == new_link
        assert evidence.eco == new_eco

    def test_save_changes2(self):
        """ Test that only the selected page of term/link is saved to the evidence"""

        evidence = Evidence(entity=Reaction(""))
        new_term = "New term"
        new_link = Gene("id")

        self.dialog.set_evidence(evidence)

        # Set dialog attributes
        self.dialog.lineEdit_term.setText(new_term)
        self.dialog.set_linked_item(new_link)

        # Check saving of term
        self.dialog.comboBox.setCurrentIndex(0)
        self.dialog.save_state()
        assert evidence.term == new_term
        assert evidence.link is None

        # Check saving of linked item
        self.dialog.comboBox.setCurrentIndex(1)
        self.dialog.save_state()
        assert evidence.term == ""
        assert evidence.link is new_link

    def test_content_changed_type(self):
        # Test changing of type
        assert self.dialog.comboBox.currentIndex() == 0
        assert self.dialog.content_changed is False

        # Action
        self.dialog.comboBox.setCurrentIndex(1)

        # Check property
        assert self.dialog.content_changed is True

    @pytest.mark.usefixtures("full_evidence")
    def test_content_changed_link(self):
        self.dialog.set_current_evidence(self.evidence)

        assert self.dialog.content_changed is False

        # Action
        self.dialog.link = Gene("g1")

        # Check property
        assert self.dialog.content_changed is True

    def test_content_changed_reference(self):
        # Test changing of reference
        assert self.dialog.referenceTable.rowCount() == 0
        assert self.dialog.current_evidence.references == []
        assert self.dialog.content_changed is False

        # Action
        self.dialog.referenceTable.update_row_from_item(Reference())

        # Check property
        assert self.dialog.content_changed is True

    @pytest.fixture()
    def patch_reference_selection_accepted(self, monkeypatch):
        reference = Reference()
        monkeypatch.setattr("GEMEditor.dialogs.evidence.ReferenceSelectionDialog", Mock(return_value=Mock(**{"exec_": Mock(return_value=True),
                                                                                                             "selected_items": Mock(return_value=[reference])})))
        return reference

    @pytest.fixture()
    def patch_reference_selection_cancelled(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.dialogs.evidence.ReferenceSelectionDialog.exec_", Mock(return_value=False))

    @pytest.mark.usefixtures("patch_reference_selection_cancelled")
    def test_add_reference_cancelled(self):
        self.dialog.add_items = Mock()

        # Action
        self.dialog.add_reference()

        # Check that add items has not been called if dialog is cancelled
        assert self.dialog.add_items.called is False

    def test_add_reference_accepted(self, patch_reference_selection_accepted):
        self.dialog.add_items = Mock()

        # Action
        self.dialog.add_reference()

        # Check that add items has not been called if dialog is cancelled
        self.dialog.add_items.assert_called_once_with(self.dialog.referenceTable, [patch_reference_selection_accepted])

    @pytest.fixture()
    def patch_gene_selection_accepted(self, monkeypatch):
        gene = Gene()
        monkeypatch.setattr("GEMEditor.dialogs.evidence.GeneSelectionDialog", Mock(return_value=Mock(**{"exec_": Mock(return_value=True),
                                                                                                        "selected_items": Mock(return_value=[gene])})))
        return gene

    @pytest.fixture()
    def patch_gene_selection_cancelled(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.dialogs.evidence.GeneSelectionDialog.exec_", Mock(return_value=False))

    def test_add_gene_accepted(self, patch_gene_selection_accepted):
        self.dialog.set_current_evidence(self.evidence)

        # Action
        self.dialog.add_link()

        # Check that add items has not been called if dialog is cancelled
        self.dialog.add_items.assert_called_once_with(self.dialog.itemTable, [patch_gene_selection_accepted])

    @pytest.mark.usefixtures("patch_gene_selection_cancelled")
    def test_add_gene_cancelled(self):
        self.dialog.add_items = Mock()

        # Action
        self.dialog.add_gene()

        # Check that add items has not been called if dialog is cancelled
        assert self.dialog.add_items.called is False

    def test_toggle_button_true(self):
        # Prior state
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False

        # Action
        self.dialog.comboBox.setCurrentIndex(1)

        # Test changes
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True

        # Action2
        self.dialog.comboBox.setCurrentIndex(0)

        # Test revert change
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False

    def test_change_visibility(self):
        self.dialog.label_link.setVisible = Mock()
        self.dialog.label_link_id.setVisible = Mock()
        self.dialog.button_change_item.setVisible = Mock()

        for i, value in enumerate(self.dialog.options):
            self.dialog.comboBox.setCurrentIndex(i)
            assert self.dialog.label_link.setVisible.called_with(value in self.dialog.link_visibility)
            assert self.dialog.label_link_id.setVisible.setVisible.called_with(value in self.dialog.link_visibility)
            assert self.dialog.button_change_item.setVisible.called_with(value in self.dialog.link_visibility)

    def test_save_changes_type(self):
        # Test type saving in save state
        for i, value in enumerate(self.dialog.options):
            self.dialog.comboBox.setCurrentIndex(i)
            self.dialog.save_state()
            assert self.evidence.type == value

    def test_save_changes_items(self):
        new_gene = Gene()
        self.dialog.link = new_gene
        assert self.dialog.comboBox.currentIndex() == 0

        # Check tha the linked item is saved depending on the options
        # selected in the combobox
        for i in range(self.dialog.comboBox.count()):
            self.dialog.current_evidence.link = None
            self.dialog.comboBox.setCurrentIndex(i)
            self.dialog.save_state()

            if self.dialog.comboBox.currentText() in self.dialog.link_visibility:
                assert self.dialog.current_evidence.link is new_gene
            else:
                assert self.dialog.current_evidence.link is None

    def test_save_changes_types(self):

        for i, value in enumerate(self.dialog.options):
            for n, item in enumerate(self.dialog.options_method_map):
                self.dialog.current_evidence.type = ""
                self.dialog.current_evidence.method_type = ""
                self.dialog.current_evidence.link = None
                self.dialog.current_evidence.method_item = None
                self.dialog.link = Gene()
                self.dialog.method_item = Gene()
                self.dialog.comboBox.setCurrentIndex(i)
                self.dialog.combobox_method.setCurrentIndex(n)

                self.dialog.save_state()

                assert self.dialog.current_evidence.method_type == self.dialog.combobox_method.currentText()
                assert self.dialog.current_evidence.type == self.dialog.comboBox.currentText()

                if self.dialog.link_visible:
                    assert self.dialog.current_evidence.link is self.dialog.link
                else:
                    assert self.dialog.current_evidence.link is None

                if self.dialog.method_link_visible:
                    assert self.dialog.current_evidence.method_item is self.dialog.method_item
                else:
                    assert self.dialog.current_evidence.method_item is None

    def test_save_changes_references(self):
        # Setup test conditions
        old_reference = Reference()
        self.evidence.references = [old_reference]
        new_reference = Reference()

        # Check prior state
        assert self.dialog.referenceTable.rowCount() == 0
        self.dialog.referenceTable.update_row_from_item(new_reference)
        assert self.dialog.referenceTable.rowCount() == 1

        # Action
        self.dialog.save_state()

        # Check post state
        assert self.evidence.references == [new_reference]

    def test_save_comment(self):
        new_comment = "Test comment"
        self.dialog.textedit_comment.setPlainText(new_comment)

        # Action
        self.dialog.save_state()

        # Check result
        assert self.evidence.comment == new_comment


class TestEcoSelectionDialog:

    def test_reminder(self):
        assert False
