from GEMEditor.base.classes import Settings
from GEMEditor.base.dialogs import CustomStandardDialog
from GEMEditor.model.selection.ui import Ui_SelectionDialog
from GEMEditor.ui.GeneTreeSelectionDialog import Ui_GeneTreeSelection
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5.QtWidgets import QDialogButtonBox


class TableDisplayDialog(CustomStandardDialog, Ui_SelectionDialog):
    
    def __init__(self, items, model, DataModel=QtGui.QStandardItemModel, ProxyModel=QSortFilterProxyModel):
        super(TableDisplayDialog, self).__init__()
        self.setupUi(self)
        self.items = items
        self.model = model
        self.dataTable = DataModel(self)
        self.proxyModel = ProxyModel(self)
        self.dataView.setModel(self.proxyModel)
        self.proxyModel.setSourceModel(self.dataTable)
        self.proxyModel.setFilterKeyColumn(-1)
        self.proxyModel.setDynamicSortFilter(True)
        self.proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.finished.connect(self.save_dialog_geometry)
        if hasattr(self.dataTable, "header"):
            self.dataTable.setHorizontalHeaderLabels(self.dataTable.header)
        self.populate_table()

    def populate_table(self):
        self.dataTable.populate_table(self.items)

    @QtCore.pyqtSlot(str)
    def update_filter(self, new):
        self.proxyModel.setFilterFixedString(new)

    def restore_dialog_geometry(self):
        super(TableDisplayDialog, self).restore_dialog_geometry()
        header_state = Settings().value(self.__class__.__name__ + "TableHeader")
        if header_state:
            self.dataView.horizontalHeader().restoreState(header_state)

    def save_dialog_geometry(self):
        super(TableDisplayDialog, self).save_dialog_geometry()
        Settings().setValue(self.__class__.__name__ + "TableHeader",
                                    self.dataView.horizontalHeader().saveState())


class TreeSelectionDialog(CustomStandardDialog, Ui_GeneTreeSelection):

    def __init__(self, parent, source_table, title="Select gene..."):
        super(TreeSelectionDialog, self).__init__(parent)
        self.setupUi(self)
        self.dataTable = source_table
        self.treeView.setModel(self.dataTable)
        self.setWindowTitle(title)

        self.treeView.selectionModel().currentChanged.connect(self.toggle_ok_button)

    @QtCore.pyqtSlot()
    def toggle_ok_button(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self.selected_items() is not None)

    def selected_items(self):
        index = self.treeView.currentIndex()
        table_item = self.dataTable.itemFromIndex(index)
        if table_item is not None:
            return table_item.link
