import re
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from GEMEditor.database import get_options
from GEMEditor.model.classes.annotation import Annotation
from GEMEditor.model.edit.ui.EditAnnotationsDialog import Ui_EditAnnotationDialog


class EditAnnotationDialog(QDialog, Ui_EditAnnotationDialog):

    def __init__(self, item, annotation=None):
        super(EditAnnotationDialog, self).__init__()
        self.setupUi(self)

        # Store status images
        self.status_unknown = QtGui.QPixmap(":/status_undefined")
        self.status_okay = QtGui.QPixmap(":/status_okay")
        self.status_error = QtGui.QPixmap(":/status_error")

        # Store validators
        self._validators = dict()
        self._collections = dict()

        self.set_annotation(annotation, item)
        self._setup_signals()

    def _setup_signals(self):
        self.annotationLineEdit.textChanged.connect(self.validate_annotation)
        self.typeComboBox.currentTextChanged.connect(self.validate_annotation)

    def set_annotation(self, annotation, item):
        """ Populate the display according to the information provided """

        databases = get_options(item.__class__.__name__)
        self._update_mappings(databases)

        # Get options for user to select from
        options = dict((x.miriam_collection, x.name) for x in databases)
        if annotation and annotation.collection not in options:
            options[annotation.collection] = annotation.collection

        # Add options to combobox
        entries = sorted(options.values())
        self.typeComboBox.clear()
        self.typeComboBox.addItems(entries)

        # Update widgets from annotation
        if annotation:
            self.typeComboBox.setCurrentIndex(entries.index(options[annotation.collection]))
            self.annotationLineEdit.setText(annotation.identifier)

        self.validate_annotation()

    def _update_mappings(self, databases):
        """ Update the mappings with relevant information

        Parameters
        ----------
        databases: list,
            The list containing the relevant database entries

        """
        self._validators.clear()
        self._validators.update((x.miriam_collection, x.validator) for x in databases)

        self._collections.clear()
        self._collections.update((x.name, x.miriam_collection) for x in databases)

    def _get_collection(self):
        """ Return the current database choice

        Returns
        -------
        str:
            The currently selected collection

        """
        choice = self.typeComboBox.currentText()
        if choice in self._collections:
            return self._collections[choice]
        else:
            return choice

    @QtCore.pyqtSlot()
    def validate_annotation(self):
        identifier = self.annotationLineEdit.text()
        collection = self._get_collection()
        if collection not in self._validators:
            # Unknown collection
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            self.statusLabel.setPixmap(self.status_unknown)
        elif identifier and re.match(self._validators[collection], identifier):
            # Valid identifier
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            self.statusLabel.setPixmap(self.status_okay)
        else:
            # Empty or invalid id
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
            self.statusLabel.setPixmap(self.status_error)

    def get_annotation(self):
        """ Return an annotation object from the user input """
        return Annotation(collection=self._get_collection(),
                          identifier=self.annotationLineEdit.text())
