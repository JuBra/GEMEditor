from GEMEditor.base.dialogs import CustomStandardDialog
from GEMEditor.base import Settings, restore_state
from GEMEditor.model.edit.ui.EditTestDialog import Ui_EditTestDialog
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialogButtonBox


class EditModelTestDialog(CustomStandardDialog, Ui_EditTestDialog):

    def __init__(self, parent):
        CustomStandardDialog.__init__(self, parent)
        self.setupUi(self)
        self.model_test = None
        self.model = None

        # Deactivate Ok button
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(False)
        self.setup_signals()
        self.restore_dialog_geometry()

    def setup_signals(self):
        self.accepted.connect(self.save_state)
        self.finished.connect(self.save_dialog_geometry)

        self.nameLineEdit.textChanged.connect(self.activate_button)
        self.commentWidget.changed.connect(self.activate_button)

        for i in range(self.tabWidget.count()):
            self.tabWidget.widget(i).changed.connect(self.activate_button)

        for i in range(self.tabWidget2.count()):
            self.tabWidget2.widget(i).changed.connect(self.activate_button)

    def set_test(self, model_test, model, solution=None):
        self.model_test = model_test
        self.model = model

        if model_test:
            self.nameLineEdit.setText(model_test.description)
            self.commentWidget.set_item(model_test, model)

            for i in range(self.tabWidget.count()):
                self.tabWidget.widget(i).set_item(model_test, model)

            for i in range(self.tabWidget2.count()):
                self.tabWidget2.widget(i).set_item(model_test, model, solution)

    @QtCore.pyqtSlot()
    def activate_button(self):
        """ Activate the okay button if the input is valid"""
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(self.input_valid() and self.content_changed)

    @property
    def content_changed(self):
        if not self.model_test:
            return False
        elif self.nameLineEdit.text() != self.model_test.description:
            return True

        for i in range(self.tabWidget.count()):
            if self.tabWidget.widget(i).content_changed:
                return True

        for i in range(self.tabWidget2.count()):
            if self.tabWidget2.widget(i).content_changed:
                return True

        return False

    def input_valid(self):
        if not self.nameLineEdit.text():
            return False

        for i in range(self.tabWidget.count()):
            if not self.tabWidget.widget(i).valid_input():
                return False

        for i in range(self.tabWidget2.count()):
            if not self.tabWidget2.widget(i).valid_input():
                return False

        return True

    @QtCore.pyqtSlot()
    def save_state(self):
        if self.model_test:
            self.model_test.description = self.nameLineEdit.text()

        self.commentWidget.save_state()

        for i in range(self.tabWidget.count()):
            self.tabWidget.widget(i).save_state()

        for i in range(self.tabWidget2.count()):
            self.tabWidget2.widget(i).save_state()

    def restore_dialog_geometry(self):
        super(EditModelTestDialog, self).restore_dialog_geometry()

        with Settings(group=self.__class__.__name__) as settings:
            restore_state(self.splitter_horizontal, settings.value("SplitterH"))
            restore_state(self.splitter_vertical, settings.value("SplitterV"))

    def save_dialog_geometry(self):
        super(EditModelTestDialog, self).save_dialog_geometry()

        with Settings(group=self.__class__.__name__) as settings:
            settings.setValue("SplitterH", self.splitter_horizontal.saveState())
            settings.setValue("SplitterV", self.splitter_vertical.saveState())
