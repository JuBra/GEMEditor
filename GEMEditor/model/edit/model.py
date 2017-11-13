import logging
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialogButtonBox, QDialog, QToolTip
from GEMEditor.model.edit.ui import Ui_AddCompartmentDialog, Ui_EditModelDialog
from six import iteritems
from GEMEditor.widgets.tables import CompartmentTable
from GEMEditor.cobraClasses import Compartment
from GEMEditor.base import text_is_different, ProgressDialog


LOGGER = logging.getLogger(__name__)


class AddCompartmentDialog(QDialog, Ui_AddCompartmentDialog):
    """ Dialog for adding or modifying model compartments """

    existing_msg = "A compartment with the abbreviation '{0}' already exists!"
    wrong_format_msg = "The abbreviation should be only one character!"

    def __init__(self, compartment_table):
        super(AddCompartmentDialog, self).__init__()
        self.setupUi(self)
        self.compartment_table = compartment_table
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def check_inputs(self):
        # The abbreviation should be one letter that is not yet part of the compartment list
        abbrev_input = self.abbreviationInput.text()
        if len(abbrev_input) != 1:
            self.set_id_tooltip(valid=False, message=self.wrong_format_msg)
            return False
        elif self.compartment_table.findItems(abbrev_input, QtCore.Qt.MatchExactly, 0):
            self.set_id_tooltip(valid=False, message=self.existing_msg.format(abbrev_input))
            return False
        else:
            self.set_id_tooltip(valid=True, message="")
            return True

    def set_id_tooltip(self, valid, message):
        if valid is True:
            self.abbreviationInput.setStyleSheet("")
            self.abbreviationInput.setToolTip("Insert abbreviation")
            QToolTip.hideText()
        else:
            self.abbreviationInput.setToolTip(message)
            QToolTip.showText(self.abbreviationInput.mapToGlobal(QtCore.QPoint(0, 0)), message)
            self.abbreviationInput.setStyleSheet("border: 1px solid red;")

    @QtCore.pyqtSlot()
    def activateButton(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self.check_inputs())

    @property
    def get_compartment(self):
        return (self.abbreviationInput.text(),
                self.nameInput.text())


class EditModelDialog(QDialog, Ui_EditModelDialog):

    def __init__(self, model):
        super(EditModelDialog, self).__init__()
        self.setupUi(self)
        self.model = model

        # Setup the compartment table
        self.compartmentTable = CompartmentTable(self)
        self.compartmentTableView.setModel(self.compartmentTable)

        # Populate display
        self.modelIdInput.setText(model.id)
        self.modelNameInput.setText(model.name)
        self.populate_table()

        # Deactivate okay button
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(False)

        # Connect the toggling of the active button
        self.compartmentTable.rowsInserted.connect(self.activateButton)
        self.compartmentTable.rowsRemoved.connect(self.activateButton)
        self.compartmentTable.dataChanged.connect(self.activateButton)

    @QtCore.pyqtSlot()
    def activateButton(self):
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(self.has_required_input() and self.input_changed())

    def has_required_input(self):
        """ Model should have at least 1 compartment"""
        return bool(self.compartmentTable.rowCount())

    def input_changed(self):
        """ Check that the input is different than in the beginning """
        return text_is_different(self.model.id, self.modelIdInput.text()) or \
               text_is_different(self.model.name, self.modelNameInput.text()) or \
               self.model.gem_compartments != dict(self.compartmentTable.get_items())

    def populate_table(self):
        """ Populate the compartment table """
        self.compartmentTable.populate_table(iteritems(self.model.gem_compartments))
        self.compartmentTableView.setModel(self.compartmentTable)

    @QtCore.pyqtSlot()
    def add_compartment(self):
        dialog = AddCompartmentDialog(self.compartmentTable)
        if dialog.exec_():
            abbrev, name = dialog.get_compartment
            self.compartmentTable.update_row_from_item((abbrev, Compartment(id=abbrev, name=name)))

    @QtCore.pyqtSlot()
    def delete_compartment(self):
        self.compartmentTableView.delete_selected_rows()

    @QtCore.pyqtSlot()
    def save_changes(self):
        # Change model ID
        new_id = self.modelIdInput.text()
        if text_is_different(self.model.id, new_id):
            LOGGER.debug("Model id changed from '{0!s}' to '{1!s}'".format(self.model.id, new_id))
            self.model.id = new_id

        # Change model name
        new_name = self.modelNameInput.text()
        if text_is_different(self.model.name, new_name):
            LOGGER.debug("Model name changed from '{0!s}' to '{1!s}'".format(self.model.name, new_name))
            self.model.name = new_name

        # Get changed compartment
        changed_compartments = dict(self.compartmentTable.get_items())

        # Deleted compartments
        for x, name in self.model.gem_compartments.items():
            if x not in changed_compartments:
                # Remove all metabolites in deleted compartment
                metabolites = [y for y in self.model.metabolites if y.compartment == x]
                self.model.gem_remove_metabolites(metabolites)

                # Delete evidences linked to compartment
                self.model.gem_compartments[x].delete_all_evidences()
                del self.model.gem_compartments[x]

        for abbrev, compartment in changed_compartments.items():
            if abbrev not in self.model.gem_compartments:
                self.model.gem_compartments[abbrev] = compartment

        # Todo: Update table
