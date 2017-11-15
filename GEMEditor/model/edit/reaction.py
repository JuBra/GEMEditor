from GEMEditor.base.dialogs import CustomStandardDialog
from GEMEditor.model.edit.ui.EditReactionDialog import Ui_ReactionEditDialog
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialogButtonBox


class ReactionInputDialog(CustomStandardDialog, Ui_ReactionEditDialog):

    def __init__(self, reaction=None, model=None, parent=None):
        CustomStandardDialog.__init__(self, parent)
        self.setupUi(self)
        self.reaction = None
        self.model = None

        # Set the reaction and restore dialog geometry
        self.set_item(reaction, model)
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(False)
        self.setup_links()
        self.restore_dialog_geometry()

    def setup_links(self):
        self.accepted.connect(self.save_state)
        self.finished.connect(self.save_dialog_geometry)

        self.attributeWidget.changed.connect(self.activate_button)
        for i in range(self.tabWidget.count()):
            self.tabWidget.widget(i).changed.connect(self.activate_button)

    def set_item(self, reaction, model):
        """ Set the metabolite and current model """
        self.attributeWidget.set_item(reaction, model)
        for i in range(self.tabWidget.count()):
            self.tabWidget.widget(i).set_item(reaction, model)

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
        """ Activate the okay button if:
            1) The information of the reaction has been changed
            2) All inputs are valid """
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(self.attributeWidget.valid_inputs() and
                                                                self.metaboliteTab.valid_inputs() and
                                                                self.content_changed())

    @QtCore.pyqtSlot()
    def save_state(self):
        """ Save the current state of the inputs to the metabolite that is currently
        edited"""
        self.attributeWidget.save_state()
        for i in range(self.tabWidget.count()):
            self.tabWidget.widget(i).save_state()


