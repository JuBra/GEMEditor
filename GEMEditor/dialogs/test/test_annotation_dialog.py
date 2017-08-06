from GEMEditor.dialogs.annotation import EditAnnotationDialog, AutoAnnotationOptionDialog
from GEMEditor.cobraClasses import Metabolite
from PyQt5 import QtGui, QtTest
from PyQt5.QtWidgets import QCheckBox, QDialogButtonBox, QApplication
import sys


app = QApplication(sys.argv)


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


class TestAutoAnnotationSettingsDialog:

    def test_no_option_checked(self):

        dialog = AutoAnnotationOptionDialog()

        # Check that ok button is enabled by default
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled()

        # Uncheck all boxes
        for x in dialog.children():
            if isinstance(x, QCheckBox):
                x.setChecked(False)

        # Check that ok button is disabled when no item is selected
        assert not dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled()

    def test_all_checked(self):

        dialog = AutoAnnotationOptionDialog()

        # Check that ok button is enabled by default
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled()

        # Uncheck all boxes
        for x in dialog.children():
            if isinstance(x, QCheckBox):
                x.setChecked(True)

        # Check that ok button is still enabled
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled()

        result = dialog.get_settings()
        assert result["Annotations"] == 1
        assert result["Charge"] == 1
        assert result["Name"] == 1
