import string

from GEMEditor.ui.ReactionsDisplayWidget import Ui_ReactionsDisplayWidget
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QRegularExpressionValidator
from PyQt5.QtWidgets import QWidget, QApplication
from GEMEditor import use_progress
from GEMEditor.model.display.ui.MetaboliteAttributeDisplayWidget import \
    Ui_MetaboliteAttributeDisplayWidget as Ui_MetAttribs


class MetaboliteAttributesDisplayWidget(QWidget, Ui_MetAttribs):

    changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(MetaboliteAttributesDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        self.model = None
        self.metabolite = None
        self.default_id_border = self.iDLineEdit.styleSheet()

        # Setup validator for SBML compliant ids
        self.validator = QRegularExpressionValidator()
        self.validator.setRegularExpression(QRegularExpression(r"^[a-zA-Z0-9_]*$"))
        self.iDLineEdit.setValidator(self.validator)

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
        self.iDLineEdit.textChanged.connect(self.changed.emit)
        self.nameLineEdit.textChanged.connect(self.changed.emit)
        self.formulaLineEdit.textChanged.connect(self.changed.emit)
        self.chargeSpinBox.valueChanged.connect(self.changed.emit)
        self.compartmentComboBox.currentIndexChanged.connect(self.changed.emit)

    def set_item(self, item, model):
        self.model = model
        self.metabolite = item
        self.populate_widgets()

    @use_progress
    def save_state(self, progress):
        """ Save the current state of the inputs to the metabolite that is currently
        edited"""
        update_reactions = False
        update_balance = False
        self.metabolite.name = self.nameLineEdit.text()
        self.metabolite.compartment = self.compartmentComboBox.currentText()

        if self.metabolite.id != self.iDLineEdit.text():
            self.metabolite.id = self.iDLineEdit.text()
            self.model.repair(rebuild_relationships=False)
            update_reactions = True

        if self.metabolite.charge != self.chargeSpinBox.value():
            self.metabolite.charge = self.chargeSpinBox.value()
            update_reactions = True
            update_balance = True

        if self.metabolite.formula != self.formulaLineEdit.text():
            self.metabolite.formula = self.formulaLineEdit.text()
            update_reactions = True
            update_balance = True

        if update_reactions is True:
            progress.setRange(0, len(self.metabolite.reactions))
            progress.setLabelText("Saving metabolite..")

            # Update reaction rows that contain this metabolite
            self.model.QtReactionTable.blockSignals(True)
            for i, reaction in enumerate(self.metabolite.reactions):
                progress.setValue(i)
                QApplication.processEvents()
                if update_balance:
                    reaction.update_balancing_status()
                self.model.QtReactionTable.update_row_from_id(reaction.id)
            self.model.QtReactionTable.blockSignals(False)
            self.model.QtReactionTable.all_data_changed()

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
        if not new_id:
            self.iDLineEdit.setStyleSheet("border: 1px solid red;")
            self.labelIdStatus.setToolTip("Empty Id!")
            self.labelIdStatus.setVisible(True)
        elif self.metabolite and new_id != self.metabolite.id and new_id in self.model.metabolites:
            self.iDLineEdit.setStyleSheet("border: 1px solid red;")
            self.labelIdStatus.setToolTip("Id exists already in model!")
            self.labelIdStatus.setVisible(True)
        else:
            self.iDLineEdit.setStyleSheet(self.default_id_border)
            self.labelIdStatus.setVisible(False)

    @QtCore.pyqtSlot(str)
    def validate_formula(self, new_formula=None):
        if not new_formula:
            return

        chars = string.digits+string.ascii_letters
        invalid_chars = set([x for x in new_formula if x not in chars])
        if invalid_chars:
            self.labelFormulaStatus.setVisible(True)
            quoted = ['"{}"'.format(x) for x in invalid_chars]
            self.labelFormulaStatus.setToolTip('Invalid characters: {}'.format(", ".join(quoted)))
            self.formulaLineEdit.setStyleSheet("border: 1px solid red;")
        else:
            self.labelFormulaStatus.setVisible(False)
            self.formulaLineEdit.setStyleSheet(self.default_id_border)

    @QtCore.pyqtSlot(str)
    def validate_compartment(self, new_compartment=None):
        if not new_compartment:
            self.labelCompartmentStatus.setVisible(True)
            self.labelCompartmentStatus.setToolTip("Select compartment!")
        else:
            self.labelCompartmentStatus.setVisible(False)

    def valid_inputs(self):
        """ Check that all input elements that are required to have a valid input
        actually do so """

        if self.metabolite and self.iDLineEdit.text():
            return ((self.iDLineEdit.text() not in self.model.metabolites or
                     self.iDLineEdit.text() == self.metabolite.id) and
                    self.compartmentComboBox.currentText() != "")
        else:
            return False


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