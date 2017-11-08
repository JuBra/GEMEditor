from GEMEditor.dialogs.annotation import EditAnnotationDialog
from GEMEditor.cobraClasses import Metabolite
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

