import string
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget
from GEMEditor.model.display.ui.GeneAttributesDisplayWidget import Ui_Form as Ui_GeneAttribs


SBML_SYMBOLS = set(string.ascii_letters+string.digits+"_")


class GeneAttributesDisplayWidget(QWidget, Ui_GeneAttribs):

    changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(GeneAttributesDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        self.model = None
        self.gene = None
        self.default_id_border = self.iDLineEdit.styleSheet()
        self._id_valid = True

        # Hide status icons before initialization
        self.labelIdStatus.setVisible(False)
        self.validate_id()

        self.setup_connections()

    def setup_connections(self):
        # Connect validators
        self.iDLineEdit.textChanged.connect(self.validate_id)

        # Connect inputs to changed
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
        tooltip = ""

        if not new_id:
            tooltip = "Empty Id!"
            self._id_valid = False
        elif any(c not in SBML_SYMBOLS for c in new_id):
            invalid_chars = set([c for c in new_id if c not in SBML_SYMBOLS])
            quoted = ['"{}"'.format(x) for x in invalid_chars]
            tooltip = 'Invalid characters: {}'.format(", ".join(quoted))
            self._id_valid = False
        elif self.gene and new_id != self.gene.id and new_id in self.model.genes:
            tooltip = "Id exists already in model!"
            self._id_valid = False
        else:
            self._id_valid = True

        self.labelIdStatus.setVisible(not self._id_valid)
        self.labelIdStatus.setToolTip(tooltip)
        self.iDLineEdit.setStyleSheet(self.default_id_border if self._id_valid else "border: 1px solid red;")
        self.changed.emit()

    def valid_inputs(self):
        """ Check that all input elements that are required to have a valid input
        actually do so """
        return self._id_valid
