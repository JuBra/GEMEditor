from GEMEditor.base.ui.TableDisplayWidgetAddDel import Ui_TableDisplayWidgetAddDel
from GEMEditor.base.widgets import TableDisplayWidget
from GEMEditor.model.display.tables import LinkedReferenceTable
from GEMEditor.model.selection.reference import ReferenceSelectionDialog
from PyQt5 import QtCore
from PyQt5.QtWidgets import QAction


class ReferenceDisplayWidget(TableDisplayWidget, Ui_TableDisplayWidgetAddDel):

    # DataType is used to display the correct names in the context menu
    dataType = "Reference"

    def __init__(self, parent=None):
        TableDisplayWidget.__init__(self, parent)
        self.dataTable = LinkedReferenceTable(self)
        self.setupUi(self)

        self.model = None
        self.display_item = None
        self._content_changed = False

        self.dataView.setModel(self.dataTable)

        self.setup_signals()

    def set_item(self, item, model):
        self.display_item = item
        self.dataTable.setRowCount(0)
        if item:
            self.dataTable.populate_table(item.references)

    @QtCore.pyqtSlot()
    def add_item(self):
        dialog = ReferenceSelectionDialog(self.model)
        if dialog.exec_():
            present = self.dataTable.get_items()
            for x in dialog.selected_items():
                if x not in present:
                    self.dataTable.update_row_from_item(x)

    @QtCore.pyqtSlot()
    def edit_item(self):
        pass

    def add_standard_menu_actions(self, menu):
        """ Return the standard context menu with addition, edit and deletion """
        # Add action
        add_action = QAction(self.tr("Add {}".format(self.dataType)), menu)
        add_action.triggered.connect(self.add_item)
        menu.addAction(add_action)

        # Show edit and deletion option only if an item is selected
        if self.dataView.selectedIndexes():
            # Delete action
            delete_action = QAction(self.tr("Delete {}".format(self.dataType)), menu)
            delete_action.triggered.connect(self.delete_item)
            menu.addAction(delete_action)


