import string
from GEMEditor.base.classes import ProgressDialog
from GEMEditor.model.display.ui.MetaboliteAttributeDisplayWidget import \
    Ui_MetaboliteAttributeDisplayWidget as Ui_MetAttribs
from GEMEditor.model.display.ui.ReactionsDisplayWidget import Ui_ReactionsDisplayWidget
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QWidget


SBML_SYMBOLS = set(string.ascii_letters+string.digits+"_")
FORMULA_CHARS = set(string.digits+string.ascii_letters)


class MetaboliteAttributesDisplayWidget(QWidget, Ui_MetAttribs):

    changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(MetaboliteAttributesDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        self.model = None
        self.metabolite = None
        self._id_valid = True
        self._formula_valid = True
        self._comp_valid = True
        self.default_id_border = self.iDLineEdit.styleSheet()

        # Toggle the warning signs
        self.validate_id()
        self.validate_compartment()
        self.validate_formula()

        self.setup_connections()

    def setup_connections(self):
        # Connect validators
        self.iDLineEdit.textChanged.connect(self.validate_id)
        self.formulaLineEdit.textChanged.connect(self.validate_formula)
        self.compartmentComboBox.currentTextChanged.connect(self.validate_compartment)

        # Connect inputs to changed
        self.chargeSpinBox.valueChanged.connect(self.changed.emit)
        self.nameLineEdit.textChanged.connect(self.changed.emit)

    def set_item(self, item, model):
        self.model = model
        self.metabolite = item
        self.populate_widgets()

    def save_state(self):
        """ Save the current state of the inputs to the metabolite that is currently
        edited"""
        self.metabolite.name = self.nameLineEdit.text()
        self.metabolite.charge = self.chargeSpinBox.value()
        self.metabolite.formula = self.formulaLineEdit.text()
        self.metabolite.compartment = self.compartmentComboBox.currentText()

        if self.metabolite.id != self.iDLineEdit.text():
            self.metabolite.id = self.iDLineEdit.text()
            self.model.repair(rebuild_relationships=False)

        if not self.metabolite.model:
            self.model.gem_add_metabolites((self.metabolite,))
        else:
            with ProgressDialog(title="Updating tables..") as progress:
                self.model.gem_update_metabolites((self.metabolite,), progress)

    @property
    def content_changed(self):
        """ Check if there has been a change in the metabolite inputs """

        if self.metabolite:
            return (self.iDLineEdit.text() != self.metabolite.id or
                    self.nameLineEdit.text() != self.metabolite.name or
                    self.formulaLineEdit.text() != self.metabolite.formula or
                    self.chargeSpinBox.value() != self.metabolite.charge or
                    self.compartmentComboBox.currentText() != self.metabolite.compartment)
        else:
            return False

    def clear_information(self):
        """ Clear all information present in the input widgets """
        self.iDLineEdit.clear()
        self.nameLineEdit.clear()
        self.formulaLineEdit.clear()
        self.chargeSpinBox.clear()
        self.chargeSpinBox.setValue(0)
        self.compartmentComboBox.clear()

    def populate_widgets(self):
        """ Update the information displayed in the individual input elements """
        self.clear_information()

        if self.metabolite is not None:

            # Populate the compartment combobox
            self.compartmentComboBox.addItems(sorted(self.model.gem_compartments.keys()))

            self.iDLineEdit.setText(self.metabolite.id)
            self.iDLineEdit.setCursorPosition(0)
            self.nameLineEdit.setText(self.metabolite.name)
            self.nameLineEdit.setCursorPosition(0)
            self.formulaLineEdit.setText(self.metabolite.formula)
            self.formulaLineEdit.setCursorPosition(0)
            self.chargeSpinBox.setValue(self.metabolite.charge or 0)

            # Add the compartment in case it is not in the model compartment
            # dictionary. Only if compartment is set.
            current_index = self.compartmentComboBox.findText(self.metabolite.compartment)
            if current_index == -1 and self.metabolite.compartment:
                self.compartmentComboBox.addItem(self.metabolite.compartment)
                self.compartmentComboBox.setCurrentIndex(self.compartmentComboBox.count()-1)
            else:
                self.compartmentComboBox.setCurrentIndex(current_index)

    @QtCore.pyqtSlot(str)
    def validate_id(self, new_id=None):
        tooltip = ""

        if not new_id:
            tooltip = "Empty Id!"
            self._id_valid = False
        elif any(c not in SBML_SYMBOLS for c in new_id):
            invalid_chars = set([c for c in new_id if c not in SBML_SYMBOLS])
            quoted = ['"{}"'.format(x) for x in invalid_chars]
            tooltip = 'Invalid characters: {}'.format(", ".join(quoted))
            self._id_valid = False
        elif self.metabolite and new_id != self.metabolite.id and new_id in self.model.metabolites:
            tooltip = "Id exists already in model!"
            self._id_valid = False
        else:
            self._id_valid = True

        self.labelIdStatus.setVisible(not self._id_valid)
        self.labelIdStatus.setToolTip(tooltip)
        self.iDLineEdit.setStyleSheet(self.default_id_border if self._id_valid else "border: 1px solid red;")
        self.changed.emit()

    @QtCore.pyqtSlot(str)
    def validate_formula(self, new_formula=None):
        tooltip = ""

        if not new_formula:
            self._formula_valid = True
        elif any(c not in FORMULA_CHARS for c in new_formula):
            invalid_chars = set(new_formula) - FORMULA_CHARS
            quoted = ['"{}"'.format(x) for x in invalid_chars]
            tooltip = 'Invalid characters: {}'.format(", ".join(quoted))
            self._formula_valid = False
        else:
            self._formula_valid = True

        self.formulaLineEdit.setStyleSheet(self.default_id_border if self._formula_valid else "border: 1px solid red;")
        self.labelFormulaStatus.setToolTip(tooltip)
        self.labelFormulaStatus.setVisible(not self._formula_valid)
        self.changed.emit()

    @QtCore.pyqtSlot(str)
    def validate_compartment(self, new_compartment=None):
        if not new_compartment:
            self.labelCompartmentStatus.setVisible(True)
            self.labelCompartmentStatus.setToolTip("Select compartment!")
            self._comp_valid = False
        else:
            self.labelCompartmentStatus.setVisible(False)
            self._comp_valid = True
        self.changed.emit()

    def valid_inputs(self):
        """ Check that all input elements that are required to have a valid input
        actually do so """
        return all((self._id_valid, self._formula_valid, self._comp_valid))


class ReactionsDisplayWidget(QWidget, Ui_ReactionsDisplayWidget):

    changed = QtCore.pyqtSignal()

    def __init__(self):
        super(ReactionsDisplayWidget, self).__init__()
        self.setupUi(self)
        self.model = None
        self.item = None
        self.reactionTable = QtGui.QStandardItemModel(self)
        self.tableViewReactions.setModel(self.reactionTable)
        self.reactionTable.setHorizontalHeaderLabels(["ID", "Subsystem", "Formula"])

    def set_item(self, item, model):
        self.model = model
        self.item = item

        if item:
            self.reactionTable.setRowCount(0)
            for reaction in item.reactions:
                self.reactionTable.appendRow([QtGui.QStandardItem(reaction.id),
                                              QtGui.QStandardItem(reaction.subsystem),
                                              QtGui.QStandardItem(reaction.reaction)])

    def save_state(self):
        # Read only widget
        pass

    @property
    def content_changed(self):
        # Read only
        return False