import logging
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFileDialog
from PyQt5.QtCore import QSettings, QRegExp, pyqtSlot
from PyQt5.QtGui import QRegExpValidator
from GEMEditor.main.settings.ui import Ui_EditSettingsDialog
from GEMEditor.database import database_path as DB_PATH


class EditSettingsDialog(QDialog, Ui_EditSettingsDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        # Setup the email field with current value
        self.settings = QSettings()
        self.eMailLineEdit.setText(self.settings.value("Email"))
        self.eMailLineEdit.setValidator(QRegExpValidator(QRegExp(r"[^@\s]+@[^@\s]+\.[^@\s.]+$")))

        # Setup database path
        self.label_database_path.setText(self.settings.value("DATABASE_PATH", DB_PATH))
        self.pushButton_change_path.clicked.connect(self.change_database_path)

        # Setup debug checkbox with current state
        logger = logging.getLogger("GEMEditor")
        if logger.isEnabledFor(logging.DEBUG):
            self.debugModeCheckBox.setChecked(True)

    @pyqtSlot()
    def toggle_ok_button(self):
        """ Check that the current E-mail adresse is valid or empty in order
         to enable the OK button """
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self.eMailLineEdit.hasAcceptableInput() or
                                                                    not self.eMailLineEdit.text())

    @pyqtSlot()
    def change_database_path(self):
        current_path = self.settings.value("DATABASE_PATH", DB_PATH)
        filename, filter = QFileDialog.getSaveFileName(self, self.tr("Change location"), current_path,
                                                       self.tr("Database (*.db)"))
        if filename:
            self.label_database_path.setText(filename)

    @pyqtSlot()
    def save_settings(self):
        """ Save the currently entered E-mail """
        self.settings.setValue("Email", self.eMailLineEdit.text())
        self.settings.setValue("DATABASE_PATH", self.label_database_path.text())
        self.settings.sync()

        logger = logging.getLogger("GEMEditor")
        # Set logger to debug mode
        if self.debugModeCheckBox.isChecked() and not logger.isEnabledFor(logging.DEBUG):
            logging.disable(logging.NOTSET)
            logger.info("DEBUG MODE ON")
        # Switch debug mode off
        elif not self.debugModeCheckBox.isChecked() and logger.isEnabledFor(logging.DEBUG):
            logging.disable(logging.DEBUG)
            logger.info("DEBUG MODE OFF")
