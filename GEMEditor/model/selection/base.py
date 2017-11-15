from GEMEditor.base.dialogs import CustomStandardDialog
from GEMEditor.ui.SelectionDialog import Ui_SelectionDialog
from PyQt5 import QtCore
from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5.QtWidgets import QAbstractItemView, QDialogButtonBox


class SelectionDialog(CustomStandardDialog, Ui_SelectionDialog):
    def __init__(self,
                 source_table,
                 selection_mode=QAbstractItemView.ExtendedSelection,
                 selection_behavior=QAbstractItemView.SelectItems):
        CustomStandardDialog.__init__(self)
        self.setupUi(self)
        self.source_table = source_table
        self.resize(self.dataView.horizontalHeader().width(), self.height())
        self.proxyModel = QSortFilterProxyModel(self)
        self.proxyModel.setSourceModel(source_table)
        self.proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxyModel.setFilterKeyColumn(-1)
        self.dataView.setModel(self.proxyModel)
        self.dataView.setSelectionBehavior(selection_behavior)
        self.dataView.setSelectionMode(selection_mode)
        self.proxyModel.sort(0)

        self.dataView.selectionModel().selectionChanged.connect(self.activate_button)
        self.dataView.doubleClicked.connect(self.accept)

        self.restore_dialog_geometry()

    def selected_items(self):
        return [self.source_table.item_from_row(x) for x in self.dataView.get_selected_rows()]

    @QtCore.pyqtSlot()
    def activate_button(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(len(self.dataView.selectedIndexes()))

    @QtCore.pyqtSlot(str)
    def update_filter(self, new):
        self.proxyModel.setFilterFixedString(new)
