from GEMEditor.main.model.ui.ModelAnnotationDisplayWidget import Ui_AnnotationDisplayWidget
from GEMEditor.main.model.ui.modelDisplayWidget import Ui_modelDisaplayWidget
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget


class ModelAnnotationDisplayWidget(QWidget, Ui_AnnotationDisplayWidget):

    def __init__(self, parent):
        super(ModelAnnotationDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        self.model = None

    def set_model(self, model):
        self.model = model
        self.update_information()

    @QtCore.pyqtSlot()
    def update_information(self):

        # Add new stats
        if self.model is not None:
            self.label_num_evidences.setText(str(len(self.model.all_evidences)))
            self.label_num_references.setText(str(len(self.model.references)))
            self.label_num_tests.setText(str(len(self.model.tests)))
        else:
            self.label_num_tests.clear()
            self.label_num_references.clear()
            self.label_num_evidences.clear()


class ModelDisplayWidget(QWidget, Ui_modelDisaplayWidget):

    model_changed = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(ModelDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        self.model = None
        self.tableView.setFixedHeight(125)
        self.tableView.setFixedWidth(200)

    def set_model(self, model, path=None):
        """  Set a new model to be displayed """

        self.model = model
        # Clear existing model data
        self.clear_information()
        self.label_model_path.setText(path)
        self.update_information()
        self.model_changed.emit()

    def set_path(self, path):
        self.label_model_path.setText(path)

    def clear_information(self):
        self.label_model_id.clear()
        self.label_model_name.clear()
        self.label_number_metabolites.clear()
        self.label_number_reactions.clear()
        self.label_number_genes.clear()
        self.tableView.setModel(None)

    @QtCore.pyqtSlot()
    def update_information(self):
        if self.model is not None:
            self.label_model_id.setText(self.model.id)
            self.label_model_name.setText(self.model.name)
            self.label_number_metabolites.setText(str(len(self.model.metabolites)))
            self.label_number_reactions.setText(str(len(self.model.reactions)))
            self.label_number_genes.setText(str(len(self.model.genes)))
            self.tableView.setModel(self.model.QtCompartmentTable)