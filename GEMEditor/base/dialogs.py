from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QComboBox
from GEMEditor.base.ui import Ui_EmptyDialogHorzButtons


class CustomStandardDialog(QDialog):
    def __init__(self, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)

    @QtCore.pyqtSlot()
    def save_dialog_geometry(self):
        # Store the geometry of the dialog during the closing
        settings = QtCore.QSettings()
        settings.setValue(self.__class__.__name__+"Geometry", self.saveGeometry())
        settings.sync()

    def restore_dialog_geometry(self):
        # Restore the geometry of the dialog
        # Should be called in the __init__(self) of the subclass
        settings = QtCore.QSettings()
        geometry = settings.value(self.__class__.__name__+"Geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)


class DialogMapCompartment(QDialog, Ui_EmptyDialogHorzButtons):

    def __init__(self, input_compartments, model):
        super(DialogMapCompartment, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("Map compartments")

        # Map input compartments to the corresponding combobox
        self.input_widget_map = {}

        # Setup layout
        layout = QGridLayout(self)

        # Add explaination
        explaination = QLabel("Please select the corresponding compartments in the model:")
        explaination.setWordWrap(True)
        layout.addWidget(explaination, 0, 0, 1, 2)

        # Add widgets
        n = 0
        for i, entry in enumerate(sorted(set(input_compartments))):
            # Add wigets with offset 1
            layout.addWidget(QLabel(str(entry)), i+1, 0)
            combobox = QComboBox()
            combobox.addItems(sorted(model.gem_compartments.keys()))
            layout.addWidget(combobox, i+1, 1)

            # Store mapping
            self.input_widget_map[entry] = combobox

            # Store index for button box addition
            n = i+1

        # Add layout to dialog
        self.setLayout(layout)
        layout.addWidget(self.buttonBox, n+1, 0, 1, 2)

    def get_mapping(self):
        return dict((input_comp, combobox.currentText()) for
                    input_comp, combobox in self.input_widget_map.items())
