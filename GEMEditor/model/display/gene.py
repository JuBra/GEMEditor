from PyQt5 import QtCore
from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QRegularExpressionValidator
from PyQt5.QtWidgets import QWidget
from GEMEditor.model.display.ui.GeneAttributesDisplayWidget import Ui_Form as Ui_GeneAttribs


class GeneAttributesDisplayWidget(QWidget, Ui_GeneAttribs):

    changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(GeneAttributesDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        self.model = None
        self.gene = None
        self.default_id_border = self.iDLineEdit.styleSheet()

        # Hide status icons before initialization
        self.labelIdStatus.setVisible(False)

        # Setup validator for SBML compliant ids
        self.validator = QRegularExpressionValidator()
        self.validator.setRegularExpression(QRegularExpression(r"^[a-zA-Z0-9_]*$"))
        self.iDLineEdit.setValidator(self.validator)

        self.validate_id()

        self.setup_connections()

    def setup_connections(self):
        # Connect validators
        self.iDLineEdit.textChanged.connect(self.validate_id)

        # Connect inputs to changed
        self.iDLineEdit.textChanged.connect(self.changed.emit)
        self.nameLineEdit.textChanged.connect(self.changed.emit)
        self.genomeLineEdit.textChanged.connect(self.changed.emit)

    def set_item(self, item, model):
        self.model = model
        self.gene = item
        self.populate_widgets()

    def save_state(self):
        """ Save the current state of the inputs to the gene that is currently
        edited"""

        self.gene.name = self.nameLineEdit.text()
        self.gene.genome = self.genomeLineEdit.text()

        if self.gene.id != self.iDLineEdit.text():
            self.gene.id = self.iDLineEdit.text()
            self.model.repair(rebuild_relationships=False)

    @property
    def content_changed(self):
        """ Check if there has been a change in the gene inputs """

        if self.gene:
            return (self.iDLineEdit.text() != self.gene.id or
                    self.nameLineEdit.text() != self.gene.name or
                    self.genomeLineEdit.text() != self.gene.genome)
        else:
            return False

    def clear_information(self):
        """ Clear all information present in the input widgets """
        self.iDLineEdit.clear()
        self.nameLineEdit.clear()
        self.genomeLineEdit.clear()

    def populate_widgets(self):
        """ Update the information displayed in the individual input elements """
        self.clear_information()

        if self.gene is not None:
            self.iDLineEdit.setText(self.gene.id)
            self.iDLineEdit.setCursorPosition(0)
            self.nameLineEdit.setText(self.gene.name)
            self.nameLineEdit.setCursorPosition(0)
            self.genomeLineEdit.setText(self.gene.genome)
            self.genomeLineEdit.setCursorPosition(0)

    @QtCore.pyqtSlot(str)
    def validate_id(self, new_id=None):
        if not new_id:
            self.iDLineEdit.setStyleSheet("border: 1px solid red;")
            self.labelIdStatus.setToolTip("Empty Id!")
            self.labelIdStatus.setVisible(True)
        elif self.gene and new_id != self.gene.id and new_id in self.model.genes:
            self.iDLineEdit.setStyleSheet("border: 1px solid red;")
            self.labelIdStatus.setToolTip("Id exists already in model!")
            self.labelIdStatus.setVisible(True)
        else:
            self.iDLineEdit.setStyleSheet(self.default_id_border)
            self.labelIdStatus.setVisible(False)

    def valid_inputs(self):
        """ Check that all input elements that are required to have a valid input
        actually do so """

        if self.gene and self.iDLineEdit.text():
            return (self.iDLineEdit.text() not in self.model.genes or
                    self.iDLineEdit.text() == self.gene.id)
        else:
            return False