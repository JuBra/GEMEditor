from PyQt5.QtWidgets import QDialog
from GEMEditor.ui.SetFluxvalueDialog import Ui_SetFluxValueDialog


class SetFluxValueDialog(QDialog, Ui_SetFluxValueDialog):

    def __init__(self, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)

    @property
    def user_input(self):
        if self.checkBox.isChecked():
            return self.fluxValueDoubleSpinBox.value(), self.deviationInput.value()
        else:
            return self.fluxValueDoubleSpinBox.value(), 0.
