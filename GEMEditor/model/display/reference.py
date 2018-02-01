from GEMEditor.model.display.tables import ReferenceTable
from GEMEditor.model.display.ui.SettingDisplayWiget import Ui_SettingsDisplayWidget
from GEMEditor.model.selection import ReferenceSelectionDialog
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QAbstractItemView


class ReferenceDisplayWidget(QWidget, Ui_SettingsDisplayWidget):

    changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(ReferenceDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        self.dataTable = ReferenceTable(self)
        self.tableView.setModel(self.dataTable)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.button_add_current.setVisible(False)

        self.model = None
        self.item = None

        self.setup_signals()

    def setup_signals(self):
        self.button_add_item.clicked.connect(self.add_reference)
        self.button_del_item.clicked.connect(self.tableView.delete_selected_rows)
        self.tableView.selectionModel().selectionChanged.connect(self.toggle_condition_del_button)

        self.dataTable.rowsRemoved.connect(self.changed.emit)
        self.dataTable.rowsInserted.connect(self.changed.emit)
        self.dataTable.dataChanged.connect(self.changed.emit)

    def set_item(self, item, model, *args):
        """ Set the item to the current widget

        Parameters
        ----------
        item : GEMEditor.data_classes.ModelTest
        model : GEMEditor.model.classes.cobra.Model

        Returns
        -------
        None
        """
        self.item = item
        self.model = model

        self.dataTable.setRowCount(0)
        if self.item:
            self.dataTable.populate_table(item.references)

    @QtCore.pyqtSlot()
    def add_reference(self):
        dialog = ReferenceSelectionDialog(self.model)

        if dialog.exec_():
            for reference in dialog.selected_items():
                if reference not in set([self.dataTable.item(i).link for i in range(self.dataTable.rowCount())]):
                    self.dataTable.update_row_from_item(reference)

    @QtCore.pyqtSlot()
    def toggle_condition_del_button(self):
        status = len(self.tableView.get_selected_indexes()) > 0
        self.button_del_item.setEnabled(status)

    @property
    def content_changed(self):
        if self.item:
            return self.item.references != self.dataTable.get_items()

        return False

    def valid_input(self):
        return True

    def save_state(self):
        # Delete old references
        for x in list(self.item.references):
            self.item.remove_reference(x)

        # Set new references
        for x in self.dataTable.get_items():
            self.item.add_reference(x)
