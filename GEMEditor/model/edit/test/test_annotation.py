import pytest
from unittest.mock import Mock
from PyQt5 import QtTest
from PyQt5.QtWidgets import QApplication, QDialogButtonBox
from GEMEditor.model.classes.annotation import Annotation
from GEMEditor.model.classes.cobra import Metabolite, Reaction, Gene
from GEMEditor.model.edit.annotation import EditAnnotationDialog


# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])

valid_annotations = [(Metabolite(), 'KEGG Compound', 'kegg.compound', "C00001"),
                     (Reaction(), 'MetaNetX Reaction', 'metanetx.reaction', 'MNXR107773'),
                     (Gene(), 'UniProtKB', 'uniprot', 'P35557')]


class TestEditAnnotationDialog:

    @pytest.mark.parametrize("item", [Metabolite(), Reaction(), Gene()])
    def test_new_annotation(self, item):
        dialog = EditAnnotationDialog(item)
        assert dialog.annotationLineEdit.text() == ""
        assert dialog.typeComboBox.count() != 0

    @pytest.mark.parametrize("item", [Metabolite(), Reaction(), Gene()])
    def test_return_unkown_collection(self, item):
        annotation = Annotation("Unknown", "Identifier")
        dialog = EditAnnotationDialog(item, annotation)
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True
        assert dialog.get_annotation() == annotation

    @pytest.mark.parametrize("item, text, collection, identifier", valid_annotations)
    def test_input_valid_annotations(self, item, text, collection, identifier):
        dialog = EditAnnotationDialog(item)
        dialog.typeComboBox.setCurrentText(text)

        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False
        QtTest.QTest.keyClicks(dialog.annotationLineEdit, identifier)
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True
        assert dialog.get_annotation() == Annotation(collection, identifier)

    def test_setting_annotation_updates_label_and_button(self):
        reaction = Reaction("r1")
        dialog = EditAnnotationDialog(reaction)
        mock = dialog.statusLabel.setPixmap = Mock()

        dialog.set_annotation(Annotation("ec-code", "2.7.1.1"), reaction)
        mock.assert_called_with(dialog.status_okay)
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True
        dialog.set_annotation(Annotation("ec-code", "2.7.1.1.-"), reaction)
        mock.assert_called_with(dialog.status_error)
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False
        dialog.set_annotation(Annotation("Unknown", "Identifier"), reaction)
        mock.assert_called_with(dialog.status_unknown)
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True
