import webbrowser
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.QtCore import pyqtSlot
from GEMEditor import __projectpage__
from GEMEditor.main.update.ui import Ui_UpdateAvailableDialog
from GEMEditor.base.classes import Settings


class UpdateAvailableDialog(QDialog, Ui_UpdateAvailableDialog):

    def __init__(self, latest_version):
        super(UpdateAvailableDialog, self).__init__()
        self.setupUi(self)
        self.status = None
        self.latest_version = latest_version
        self.setWindowTitle("Version {} available".format(latest_version))

        # Connect buttons
        self.buttonBox.button(QDialogButtonBox.Yes).clicked.connect(self.open_project_page)
        self.buttonBox.button(QDialogButtonBox.No).clicked.connect(self.ignore_version)

    @pyqtSlot()
    def ignore_version(self):
        if self.checkBox.isChecked():
            Settings().setValue("IgnoreVersion", self.latest_version)

    @pyqtSlot()
    def open_project_page(self):
        webbrowser.open(__projectpage__)

    def version_is_ignored(self):
        return Settings().value("IgnoreVersion") == self.latest_version
