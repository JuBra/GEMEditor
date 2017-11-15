import logging
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialogButtonBox, QDialog, QToolTip
from GEMEditor.base import text_is_different
from GEMEditor.model.classes.cobra import Compartment
from GEMEditor.model.edit.ui import Ui_AddCompartmentDialog, Ui_EditModelDialog
from GEMEditor.widgets.tables import CompartmentTable


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

        # Connect slots
        self.input_id.textChanged.connect(self.activate_button)
        self.input_name.textChanged.connect(self.activate_button)

    def check_inputs(self):
        # The abbreviation should be one letter that is not yet part of the compartment list
        abbrev_input = self.input_id.text()
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
            self.input_id.setStyleSheet("")
            self.input_id.setToolTip("Insert abbreviation")
            QToolTip.hideText()
        else:
            self.input_id.setToolTip(message)
            QToolTip.showText(self.input_id.mapToGlobal(QtCore.QPoint(0, 0)), message)
            self.input_id.setStyleSheet("border: 1px solid red;")

    @QtCore.pyqtSlot()
    def activate_button(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self.check_inputs())

    @property
    def get_compartment(self):
        return Compartment(id=self.input_id.text(),
                           name=self.input_name.text())


class EditModelDialog(QDialog, Ui_EditModelDialog):

    def __init__(self, model):
        super(EditModelDialog, self).__init__()
        self.setupUi(self)
        self.model = model

        # Setup the compartment table
        self.compartmentTable = CompartmentTable(self)
        self.compartmentTableView.setModel(self.compartmentTable)

        # Populate display
        self.input_id.setText(model.id)
        self.input_name.setText(model.name)
        self.populate_table()

        # Deactivate okay button
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(False)

        # Connect slots
        self.button_add_compartment.clicked.connect(self.add_compartment)
        self.button_del_compartment.clicked.connect(self.delete_compartment)

        # Connect the toggling of the active button
        self.input_id.textChanged.connect(self.activate_button)
        self.input_name.textChanged.connect(self.activate_button)
        self.compartmentTable.rowsInserted.connect(self.activate_button)
        self.compartmentTable.rowsRemoved.connect(self.activate_button)
        self.compartmentTable.dataChanged.connect(self.activate_button)

    @QtCore.pyqtSlot()
    def activate_button(self):
        self.buttonBox.button(QDialogButtonBox.Save).setEnabled(self.has_required_input() and self.input_changed())

    def has_required_input(self):
        """ Model should have at least 1 compartment"""
        return self.compartmentTable.rowCount()

    def input_changed(self):
        """ Check that the input is different than in the beginning """
        return text_is_different(self.model.id, self.input_id.text()) or \
               text_is_different(self.model.name, self.input_name.text()) or \
               self.compartments_changed()

    def populate_table(self):
        """ Populate the compartment table """
        self.compartmentTable.populate_table(self.model.gem_compartments.values())

    def _add_new_compartment_to_table(self, compartment):
        row_data = self.compartmentTable.row_from_item(compartment)
        # Reset compartment attributes to trigger changed state
        compartment.id = None
        compartment.name = None
        self.compartmentTable.appendRow(row_data)

    @QtCore.pyqtSlot()
    def add_compartment(self):
        dialog = AddCompartmentDialog(self.compartmentTable)
        if dialog.exec_():
            compartment = dialog.get_compartment
            self._add_new_compartment_to_table(compartment)

    @QtCore.pyqtSlot()
    def delete_compartment(self):
        self.compartmentTableView.delete_selected_rows()

    def compartments_changed(self):
        if self.compartmentTable.rowCount() != len(self.model.gem_compartments):
            return True

        for i in range(self.compartmentTable.rowCount()):
            compartment = self.compartmentTable.item_from_row(i)
            current_tuple = (self.compartmentTable.item(i).text(),
                             self.compartmentTable.item(i, 1).text())
            if compartment != current_tuple:
                return True
        return False

    @QtCore.pyqtSlot()
    def save_changes(self):
        # Change model ID
        new_id = self.input_id.text()
        if text_is_different(self.model.id, new_id):
            LOGGER.debug("Model id changed from '{0!s}' to '{1!s}'".format(self.model.id, new_id))
            self.model.id = new_id

        # Change model name
        new_name = self.input_name.text()
        if text_is_different(self.model.name, new_name):
            LOGGER.debug("Model name changed from '{0!s}' to '{1!s}'".format(self.model.name, new_name))
            self.model.name = new_name

        old_compartments = set(self.model.gem_compartments.values())

        # Edit compartments
        for i in range(self.compartmentTable.rowCount()):
            comp = self.compartmentTable.item_from_row(i)
            if comp.id is None:
                # New compartment
                comp.id = self.compartmentTable.item(i).text()
                self.model.gem_compartments[comp.id] = comp
                LOGGER.debug("Compartment('{0!s}', '{1!s}') added to model".format(comp.id, comp.name))
            else:
                # Compartment already present
                new_comp_id = self.compartmentTable.item(i).text()
                old_comp_id = comp.id
                if old_comp_id != new_comp_id:
                    # Change id
                    comp.id = new_comp_id
                    # Rename metabolites
                    metabolites = [y for y in self.model.metabolites if y.compartment == old_comp_id]
                    for m in metabolites:
                        m.compartment = new_comp_id

                    # Update metabolite table entries
                    self.model.gem_update_metabolites(metabolites)

                    # Substitue old entry
                    del self.model.gem_compartments[old_comp_id]
                    self.model.gem_compartments[new_comp_id] = comp

            # Set name
            comp.name = self.compartmentTable.item(i, 1).text()

            # Remove item from old comparrment list
            old_compartments.discard(comp)

        # Remove compartments that have been removed from the model
        for compartment in old_compartments:
            metabolites = [y for y in self.model.metabolites if y.compartment == compartment.id]
            self.model.gem_remove_metabolites(metabolites)
            del self.model.gem_compartments[compartment.id]
