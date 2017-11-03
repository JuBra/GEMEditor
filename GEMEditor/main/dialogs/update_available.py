from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.QtCore import pyqtSlot
from GEMEditor.main.dialogs.ui import Ui_UpdateAvailableDialog


class UpdateAvailableDialog(QDialog, Ui_UpdateAvailableDialog):

    def __init__(self, parent=None):
        super(UpdateAvailableDialog, self).__init__(parent)
        self.setupUi(self)
        self.status = None

        # Connect buttons
        self.buttonBox.button(QDialogButtonBox.Yes).clicked.connect(self.set_status_yes)
        self.buttonBox.button(QDialogButtonBox.No).clicked.connect(self.set_status_no)

    def show_again(self):
        # The checkbox asks if the dialog should not be shown again
        return not self.checkBox.isChecked()

    @pyqtSlot()
    def set_status_yes(self):
        self.status = QDialogButtonBox.Yes

    @pyqtSlot()
    def set_status_no(self):
        self.status = QDialogButtonBox.No
