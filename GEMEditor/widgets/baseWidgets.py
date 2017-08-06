from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QAction, QMenu, QStatusBar


class TableDisplayWidget(QWidget):

    changed = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.delete_button = None
        self.edit_button = None
        self.add_button = None

    def setup_signals(self):
        self.dataView.selectionModel().selectionChanged.connect(self.toggle_buttons)
        self.dataTable.dataChanged.connect(self.changed.emit)
        self.dataTable.rowsInserted.connect(self.changed.emit)
        self.dataTable.rowsRemoved.connect(self.changed.emit)

    def add_item(self):
        raise NotImplementedError

    def edit_item(self):
        raise NotImplementedError

    @QtCore.pyqtSlot()
    def delete_item(self):
        """ Delete all selected rows from data table """
        self.dataView.delete_selected_rows()

    @QtCore.pyqtSlot()
    def toggle_buttons(self):
        enabled = len(self.get_selected_indexes()) > 0
        if self.delete_button:
            self.delete_button.setEnabled(enabled)
        if self.edit_button:
            self.edit_button.setEnabled(enabled)

    def get_selected_indexes(self):
        """ Get currently selected items """
        return self.dataView.selectedIndexes()

    def add_standard_menu_actions(self, menu):
        """ Return the standard context menu with addition, edit and deletion """
        # Add action
        add_action = QAction(self.tr("Add {}".format(self.dataType)), menu)
        add_action.triggered.connect(self.add_item)
        menu.addAction(add_action)

        # Show edit and deletion option only if an item is selected
        if self.dataView.selectedIndexes():
            # Edit action
            edit_action = QAction(self.tr("Edit {}".format(self.dataType)), menu)
            edit_action.triggered.connect(self.edit_item)
            menu.addAction(edit_action)

            # Delete action
            delete_action = QAction(self.tr("Delete {}".format(self.dataType)), menu)
            delete_action.triggered.connect(self.delete_item)
            menu.addAction(delete_action)

        return menu

    @QtCore.pyqtSlot(QtCore.QPoint)
    def showContextMenu(self, pos):
        """ Show the context menu using the standard one"""
        menu = QMenu()
        self.add_standard_menu_actions(menu)
        menu.exec_(self.dataView.viewport().mapToGlobal(pos))


class StatusBar(QStatusBar):
    """ Class for being able to a add a status bar via the Designer
     i.e. by pomoting widget"""

    def __init__(self, *args, **kwargs):
        super(StatusBar, self).__init__(*args, **kwargs)