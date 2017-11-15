from GEMEditor.base.dialogs import CustomStandardDialog
from GEMEditor.model.edit.ui.EditMetaboliteDialog import Ui_MetaboliteEditDialog
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialogButtonBox


class MetaboliteEditDialog(CustomStandardDialog, Ui_MetaboliteEditDialog):

    def __init__(self, parent=None, metabolite=None, model=None):
        CustomStandardDialog.__init__(self, parent)
        self.setupUi(self)

        self.ok_button = self.buttonBox.button(QDialogButtonBox.Ok)
        self.ok_button.setEnabled(False)

        self.set_item(metabolite, model)

        self.setup_links()
        self.restore_dialog_geometry()

    def setup_links(self):
        self.accepted.connect(self.save_state)
        self.finished.connect(self.save_dialog_geometry)

        self.attributeWidget.changed.connect(self.activate_button)
        for i in range(self.tabWidget.count()):
            self.tabWidget.widget(i).changed.connect(self.activate_button)

    def set_item(self, metabolite, model):
        """ Set the metabolite and current model """
        self.attributeWidget.set_item(metabolite, model)
        for i in range(self.tabWidget.count()):
            self.tabWidget.widget(i).set_item(metabolite, model)

    def content_changed(self):
        if self.attributeWidget.content_changed:
            return True
        else:
            for i in range(self.tabWidget.count()):
                if self.tabWidget.widget(i).content_changed is True:
                    return True
        return False

    @QtCore.pyqtSlot()
    def activate_button(self):
        """ Activate the OK button if all requirements i.e. all inputs are valid and there
        has been at least one change in an input item are satisfied """
        self.ok_button.setEnabled(self.attributeWidget.valid_inputs() and self.content_changed())

    @QtCore.pyqtSlot()
    def save_state(self):
        """ Save the current state of the inputs to the metabolite that is currently
        edited"""
        self.attributeWidget.save_state()
        for i in range(self.tabWidget.count()):
            self.tabWidget.widget(i).save_state()

