from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QComboBox
from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from GEMEditor.base.ui import Ui_EmptyDialogHorzButtons, Ui_ListDisplayDialog, Ui_DataFrameDialog
from GEMEditor.base.classes import Settings


class CustomStandardDialog(QDialog):
    def __init__(self, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)

        # Store the dialog type in order to
        # distinguish dialogs in settings
        self.dialog_type = ""

    @QtCore.pyqtSlot()
    def save_dialog_geometry(self):
        # Store the geometry of the dialog during the closing
        settings = Settings()
        settings.setValue(self.__class__.__name__+"Geometry"+str(self.dialog_type), self.saveGeometry())
        settings.sync()

    def restore_dialog_geometry(self):
        # Restore the geometry of the dialog
        # Should be called in the __init__(self) of the subclass
        settings = Settings()
        geometry = settings.value(self.__class__.__name__+"Geometry"+str(self.dialog_type))
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


class ListDisplayDialog(QDialog, Ui_ListDisplayDialog):

    def __init__(self, display_list, parent=None):
        super(ListDisplayDialog, self).__init__(parent)
        self.setupUi(self)
        self.listWidget.addItems(display_list)


class DataFrameDialog(QDialog, Ui_DataFrameDialog):

    def __init__(self, dataframe):
        super(DataFrameDialog, self).__init__()
        self.setupUi(self)

        def dataitem(value):
            item = QStandardItem()
            try:
                item.setData(float(value), 2)
            except ValueError:
                item.setText(str(value))
            return item

        self.datatable = QStandardItemModel(self)
        self.datatable.setColumnCount(dataframe.shape[1])
        for row in dataframe.itertuples(index=True):
            self.datatable.appendRow([dataitem(x) for x in row])
        self.datatable.setHorizontalHeaderLabels(["Index"]+[x.title() for x in dataframe.axes[1]])
        self.proxymodel = QSortFilterProxyModel(self)
        self.proxymodel.setSourceModel(self.datatable)
        self.tableView.setModel(self.proxymodel)
        self.proxymodel.setDynamicSortFilter(True)
        self.proxymodel.sort(0)
