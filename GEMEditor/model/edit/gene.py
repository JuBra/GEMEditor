from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialogButtonBox
from GEMEditor.ui.GeneEditDialog import Ui_GeneEditDialog
from GEMEditor.base.dialogs import CustomStandardDialog


class GeneEditDialog(CustomStandardDialog, Ui_GeneEditDialog):

    def __init__(self, parent=None, gene=None, model=None):
        CustomStandardDialog.__init__(self, parent)
        self.setupUi(self)
        self.gene = None
        self.model = None

        self.set_item(gene, model)

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.setup_links()
        self.restore_dialog_geometry()

    def setup_links(self):
        self.accepted.connect(self.save_state)
        self.finished.connect(self.save_dialog_geometry)

        self.attributeWidget.changed.connect(self.activate_button)
        for i in range(self.tabWidget.count()):
            self.tabWidget.widget(i).changed.connect(self.activate_button)

    def set_item(self, gene, model):
        """ Set the metabolite and current model """
        self.attributeWidget.set_item(gene, model)
        for i in range(self.tabWidget.count()):
            self.tabWidget.widget(i).set_item(gene, model)

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
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self.attributeWidget.valid_inputs() and self.content_changed())

    @QtCore.pyqtSlot()
    def save_state(self):
        """ Save the current state of the inputs to the metabolite that is currently
        edited"""
        self.attributeWidget.save_state()
        for i in range(self.tabWidget.count()):
            self.tabWidget.widget(i).save_state()
