import logging
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QDialogButtonBox, QApplication, QDialog
from GEMEditor.ui.EditSettingsDialog import Ui_EditSettingsDialog
from GEMEditor.ui.AboutDialog import Ui_AboutDialog
from GEMEditor.ui.ListDisplayDialog import Ui_ListDisplayDialog
from GEMEditor.ui.UpdateAvailableDialog import Ui_UpdateAvailableDialog
from GEMEditor import __projectpage__, __version__


class EditSettingsDialog(QDialog, Ui_EditSettingsDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        # Setup the email field with current value
        self.settings = QtCore.QSettings()
        self.eMailLineEdit.setText(self.settings.value("Email"))
        self.eMailLineEdit.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp(r"[^@\s]+@[^@\s]+\.[^@\s.]+$")))

        # Setup debug checkbox with current state
        logger = logging.getLogger("GEMEditor")
        if logger.isEnabledFor(logging.DEBUG):
            self.debugModeCheckBox.setChecked(True)

    @QtCore.pyqtSlot()
    def toggle_ok_button(self):
        """ Check that the current E-mail adresse is valid or empty in order
         to enable the OK button """
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self.eMailLineEdit.hasAcceptableInput() or
                                                                    not self.eMailLineEdit.text())

    @QtCore.pyqtSlot()
    def save_settings(self):
        """ Save the currently entered E-mail """
        self.settings.setValue("Email", self.eMailLineEdit.text())
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


class AboutDialog(QDialog, Ui_AboutDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        appname = QApplication.applicationName()
        self.setWindowTitle(self.tr("About {}".format(appname)))
        self.textDisplay.setHtml("""<h1>About {appName}</h1>
        <p><b>Version {version}</b></p>
        <p>{appName} is an editor for genome-scale metabolic models in order to facilitate selection, modification and
        annotation of genome-scale models.<br>
        This program has been developed at the Technical University of Denmark (DTU).</p>

        {appName} is built on top of excellent free software packages:
        <ul>
        <li>Cobrapy for model solving</li>
        <li>Escher for visualization</li>
        <li>Networkx for network layout</li>
        <li>MetaNetX for annotation</li>
        </ul>
        
        <p>If you need help or want to report a bug, please visit the <a href="{projectPage}">project page</a>.</p>

        <p>If you use {appName} in a scientific publication please cite:<br>
        <b>Brandl J, Andersen MR, unpublished</b></p>
        
        <p>{appName} is distributed under the following license:</b></p>

        <p>The MIT License (MIT)<br>
        Copyright (c) 2016 Technical University of Denmark (DTU)</p>

        <p>Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:</p>

        <p>The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.</p>

        <p>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.</p>

        """.format(appName=appname, projectPage=__projectpage__, version=__version__))


class ListDisplayDialog(QDialog, Ui_ListDisplayDialog):

    def __init__(self, display_list, parent=None):
        super(ListDisplayDialog, self).__init__(parent)
        self.setupUi(self)
        self.listWidget.addItems(display_list)


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

    @QtCore.pyqtSlot()
    def set_status_yes(self):
        self.status = QDialogButtonBox.Yes

    @QtCore.pyqtSlot()
    def set_status_no(self):
        self.status = QDialogButtonBox.No
