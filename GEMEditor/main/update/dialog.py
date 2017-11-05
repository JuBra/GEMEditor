from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl, pyqtSlot, QSettings
from GEMEditor import __projectpage__, VERSION_IGNORED
from GEMEditor.main.update.ui import Ui_UpdateAvailableDialog


class UpdateAvailableDialog(QDialog, Ui_UpdateAvailableDialog):

    def __init__(self, latest_version, parent=None):
        super(UpdateAvailableDialog, self).__init__(parent)
        self.setupUi(self)
        self.status = None
        self.latest_version = latest_version
        self.setWindowTitle("Version {} available".format(latest_version))

        # Connect buttons
        self.buttonBox.button(QDialogButtonBox.Yes).clicked.connect(self.open_project_page)
        self.buttonBox.button(QDialogButtonBox.No).clicked.connect(self.store_ignore_version)

    @pyqtSlot()
    def store_ignore_version(self):
        if self.checkBox.isChecked():
            settings = QSettings()
            settings.setValue(VERSION_IGNORED, self.latest_version)
            settings.sync()

    @pyqtSlot()
    def open_project_page(self):
        QDesktopServices.openUrl(QUrl(__projectpage__))

    def version_is_ignored(self):
        settings = QSettings()
        return self.latest_version == settings.value(VERSION_IGNORED)

