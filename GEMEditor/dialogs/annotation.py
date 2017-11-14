import re
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from GEMEditor.ui.EditAnnotationsDialog import Ui_EditAnnotationDialog
from GEMEditor.data_classes import Annotation
from GEMEditor.facts import Metabolite_annotations, Reaction_annotations, Gene_annotations, Resource
from GEMEditor.cobraClasses import Reaction, Metabolite, Gene


class EditAnnotationDialog(QDialog, Ui_EditAnnotationDialog):

    def __init__(self, annotation=None, item=None):
        super(EditAnnotationDialog, self).__init__()
        self.setupUi(self)
        self.annotation = None
        self.item = None
        self.lookup = {}

        # Store status images
        self.status_unknown = QtGui.QPixmap(":/status_undefined")
        self.status_okay = QtGui.QPixmap(":/status_okay")
        self.status_error = QtGui.QPixmap(":/status_error")

        self.set_annotation(annotation, item)
        self.setup_links()

    def setup_links(self):
        self.annotationLineEdit.textChanged.connect(self.validate_annotation)
        self.typeComboBox.currentTextChanged.connect(self.validate_annotation)

    def set_annotation(self, annotation, item):
        """ Populate the display according to the information provided """

        self.annotation = annotation
        self.item = item

        self.set_options(item)
        if annotation:
            try:
                display_name = self.lookup[annotation.collection].display_name
            except KeyError:
                self.lookup[annotation.collection] = Resource(annotation.collection, annotation.collection, r".*")
                self.typeComboBox.addItem(annotation.collection)
                display_name = annotation.collection
            finally:
                index = self.typeComboBox.findText(display_name)
                self.annotationLineEdit.setText(annotation.identifier)
        else:
            index = 0
        self.typeComboBox.setCurrentIndex(index)
        self.validate_annotation()

    def set_options(self, item):
        self.typeComboBox.clear()
        self.lookup.clear()

        if isinstance(item, Reaction):
            self.lookup.update(Reaction_annotations)
        elif isinstance(item, Metabolite):
            self.lookup.update(Metabolite_annotations)
        elif isinstance(item, Gene):
            self.lookup.update(Gene_annotations)
        else:
            return

        self.typeComboBox.addItems(sorted([x.display_name for x in set(self.lookup.values())]))

    @QtCore.pyqtSlot()
    def validate_annotation(self):
        text = self.annotationLineEdit.text()
        try:
            pattern = self.lookup[self.typeComboBox.currentText()].validator
        except KeyError:
            # Unknown status
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
            self.statusLabel.setPixmap(self.status_unknown)
        else:
            if text and re.match(pattern, text):
                self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
                self.statusLabel.setPixmap(self.status_okay)
            else:
                self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
                self.statusLabel.setPixmap(self.status_error)

    def get_annotation(self):
        """ Return an annotation object from the user input """
        text = self.typeComboBox.currentText()
        return Annotation(collection=self.lookup[text].collection,
                          identifier=self.annotationLineEdit.text())
