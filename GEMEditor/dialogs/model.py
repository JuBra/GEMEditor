from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialogButtonBox, QDialog, QToolTip, QProgressDialog, QApplication
from GEMEditor.ui.AddCompartmentDialog import Ui_AddCompartmentDialog
from GEMEditor.ui.EditModelDialog import Ui_EditModelDialog
from six import iteritems
from GEMEditor.widgets.tables import CompartmentTable


class AddCompartmentDialog(QDialog, Ui_AddCompartmentDialog):
    existing_msg = "A compartment with the abbreviation '{0}' already exists!"
    wrong_format_msg = "The abbreviation should be only one character!"

    def __init__(self, compartment_table):
        QDialog.__init__(self)
        self.setupUi(self)
        self.compartment_table = compartment_table
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def check_inputs(self):
        # The abbreviation should be one letter that is not yet part of the compartment list
        abbrev_input = self.abbreviationInput.text()
        if len(abbrev_input) != 1:
            self.abbreviationInput.setToolTip(self.wrong_format_msg)
            QToolTip.showText(self.abbreviationInput.mapToGlobal(QtCore.QPoint(0, 0)), self.wrong_format_msg)
            self.abbreviationInput.setStyleSheet("border: 1px solid red;")
            return False
        elif self.compartment_table.findItems(abbrev_input, QtCore.Qt.MatchExactly, 0):
            msg = self.existing_msg.format(abbrev_input)
            self.abbreviationInput.setToolTip(msg)
            QToolTip.showText(self.abbreviationInput.mapToGlobal(QtCore.QPoint(0, 0)), msg)
            self.abbreviationInput.setStyleSheet("border: 1px solid red;")
            return False
        self.abbreviationInput.setStyleSheet("")
        self.abbreviationInput.setToolTip("Insert abbreviation")
        QToolTip.hideText()
        return True

    @QtCore.pyqtSlot()
    def activateButton(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self.check_inputs())

    @property
    def get_compartment(self):
        return (self.abbreviationInput.text(),
                self.nameInput.text())


class EditModelDialog(QDialog, Ui_EditModelDialog):

    def __init__(self, parent, model):
        super(EditModelDialog, self).__init__(parent)
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
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        # Connect the toggling of the active button
        self.compartmentTable.rowsInserted.connect(self.activateButton)
        self.compartmentTable.rowsRemoved.connect(self.activateButton)
        self.compartmentTable.dataChanged.connect(self.activateButton)

    @QtCore.pyqtSlot()
    def activateButton(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self.has_required_input() and self.input_changed())

    def has_required_input(self):
        """ Check that all required fields are filled """
        return bool(self.modelIdInput.text() and self.compartmentTable.rowCount())

    def input_changed(self):
        """ Check that the input is different than in the beginning """
        if (self.model.id != self.modelIdInput.text() or
            self.model.name != self.modelNameInput.text() or
                self.model.gem_compartments != dict(self.compartmentTable.get_items())):
            return True
        else:
            return False

    def populate_table(self):
        """ Populate the compartment table """
        self.compartmentTable.populate_table(iteritems(self.model.gem_compartments))
        self.compartmentTableView.setModel(self.compartmentTable)

    @QtCore.pyqtSlot()
    def add_compartment(self):
        dialog = AddCompartmentDialog(self.compartmentTable)
        status = dialog.exec_()
        if status:
            self.compartmentTable.update_row_from_item(dialog.get_compartment)

    @QtCore.pyqtSlot()
    def delete_compartment(self):
        self.compartmentTableView.delete_selected_rows()

    @QtCore.pyqtSlot()
    def save_changes(self):
        self.model.id = self.modelIdInput.text()
        self.model.name = self.modelNameInput.text()

        changed_compartments = dict(self.compartmentTable.get_items())

        # Deleted compartments
        for x, name in self.model.gem_compartments.items():
            if x not in changed_compartments:
                # Get all metabolites in compartment x
                metabolites = [y for y in self.model.metabolites if y.compartment == x]

                if metabolites:
                    progress = QProgressDialog("Deleting compartment: {1} ({0})".format(x.lower(), name),
                                                     "Cancel",
                                                     0, len(metabolites),
                                                     self)
                    progress.setWindowModality(QtCore.Qt.WindowModal)
                    progress.setAutoClose(False)
                    progress.show()
                    # Remove metabolites in compartment x
                    for i, metabolite in enumerate(metabolites):
                        progress.setValue(i)
                        QApplication.processEvents()
                        metabolite.remove_from_model('subtractive')
                    progress.close()
        self.model.gem_compartments = changed_compartments
        self.model.setup_tables()