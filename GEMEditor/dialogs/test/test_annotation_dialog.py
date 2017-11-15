from unittest.mock import Mock

from GEMEditor.dialogs.annotation import EditAnnotationDialog
from GEMEditor.model.classes.cobra import Metabolite, Reaction
from GEMEditor.model.classes.annotation import Annotation
from PyQt5 import QtTest
from PyQt5.QtWidgets import QApplication

# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestEditAnnotationDialog:

    def test_empty_setup(self):
        dialog = EditAnnotationDialog()
        assert dialog.annotationLineEdit.text() == ""
        assert dialog.typeComboBox.count() == 0

    def test_setup_emtpy_annotation(self):
        metabolite = Metabolite()
        dialog = EditAnnotationDialog(item=metabolite)
        assert dialog.annotationLineEdit.text() == ""
        assert dialog.typeComboBox.count() != 0

    def test_get_annotation(self):
        metabolite = Metabolite()
        dialog = EditAnnotationDialog(item=metabolite)
        new_annotation = "new"

        QtTest.QTest.keyClicks(dialog.annotationLineEdit, new_annotation)

        resulting_annotation = dialog.get_annotation()
        assert resulting_annotation.identifier == new_annotation
        assert resulting_annotation.collection == dialog.lookup[dialog.typeComboBox.currentText()].collection

    def test_setting_annotation_updates_label(self):
        dialog = EditAnnotationDialog()
        mock = dialog.statusLabel.setPixmap = Mock()
        reaction = Reaction("r1")

        dialog.set_annotation(Annotation("ec-code", "2.7.1.1"), reaction)
        mock.assert_called_with(dialog.status_okay)
        dialog.set_annotation(Annotation("ec-code", "2.7.1.1.-"), reaction)
        mock.assert_called_with(dialog.status_error)

