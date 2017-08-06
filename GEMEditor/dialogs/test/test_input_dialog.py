from GEMEditor.dialogs.input import SetFluxValueDialog
from PyQt5 import QtTest, QtCore
from PyQt5.QtWidgets import QApplication, QDialogButtonBox
import sys


app = QApplication(sys.argv)


class TestSetFluxValueDialog:

    def test_setup(self):
        dialog = SetFluxValueDialog()
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True
        assert dialog.fluxValueDoubleSpinBox.value() == 0.
        assert dialog.deviationInput.value() == 1
        assert dialog.checkBox.isChecked() is True

    def test_returning_value(self):
        dialog = SetFluxValueDialog()
        value = 5.5
        QtTest.QTest.keyClicks(dialog.fluxValueDoubleSpinBox, str(value))
        assert dialog.fluxValueDoubleSpinBox.value() == value
        assert dialog.checkBox.isChecked() is True
        assert dialog.deviationInput.value() == 1
        return_value = dialog.user_input
        assert return_value[0] == value
        assert return_value[1] == 1

    def test_deviation_is_zero_if_checkbox_unchecked(self):
        dialog = SetFluxValueDialog()
        assert dialog.checkBox.isChecked() is True
        assert dialog.user_input[1] == 1

        QtTest.QTest.mouseClick(dialog.checkBox, QtCore.Qt.LeftButton)

        assert dialog.checkBox.isChecked() is False
        assert dialog.user_input[1] == 0

    def test_changing_deviation(self):
        dialog = SetFluxValueDialog()
        assert dialog.checkBox.isChecked() is True
        assert dialog.user_input[1] == 1

        dialog.deviationInput.clear()
        value = 5
        QtTest.QTest.keyClicks(dialog.deviationInput, str(value))
        assert dialog.user_input[1] == value
        assert dialog.checkBox.isChecked() is True
