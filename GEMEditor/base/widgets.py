import webbrowser
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMenu, QAction, QWidget, QAbstractItemView
from PyQt5 import QtCore
from GEMEditor.base.ui.TableSearchWidget import Ui_StandardTab


class AnnotationTableWidget(QTableWidget):

    def __init__(self, *args):
        super(AnnotationTableWidget, self).__init__(*args)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.action_open_browser = QAction(self.tr("Open in browser"), self)
        self.action_open_browser.triggered.connect(self.open_in_browser)

    def populate_annotations(self, annotations):
        """ Populate the table with the annotations

        Parameters
        ----------
        table_widget: QTableWidget
        annotations: annotation

        Returns
        -------

        """

        # Update table dimensions
        self.setRowCount(len(annotations))
        self.setColumnCount(2)

        # Add identifiers
        n = 0
        for annotation in annotations:
            self.setItem(n, 0, QTableWidgetItem(annotation.collection))
            self.setItem(n, 1, QTableWidgetItem(annotation.identifier))
            n += 1

        # Reset header items
        self.setHorizontalHeaderLabels(["Resource", "ID"])

    @QtCore.pyqtSlot(QtCore.QPoint)
    def show_context_menu(self, pos):
        index = self.indexAt(pos)
        if not index.isValid():
            return
        else:
            menu = QMenu()
            menu.addAction(self.action_open_browser)
            menu.exec_(self.viewport().mapToGlobal(pos))

    def open_in_browser(self):
        row = self.currentRow()
        webbrowser.open("http://identifiers.org/{0}/{1}".format(self.item(row, 0).text(),
                                                                self.item(row, 1).text()))


class SearchTableWidget(QWidget, Ui_StandardTab):

    def __init__(self, parent, TableModel, ProxyModel, ViewClass):
        """ Setup widget

        Parameters
        ----------
        TableModel: class
        ProxyModel: class
        """

        super(SearchTableWidget, self).__init__(parent)
        self.setupUi(self)
        self.datatable = TableModel(self)
        self.proxymodel = ProxyModel(self)
        self.dataView = ViewClass(self)
        self.dataView.setModel(self.proxymodel)
        self.proxymodel.setSourceModel(self.datatable)
        self.proxymodel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.proxymodel.setFilterKeyColumn(-1)
        self.proxymodel.setDynamicSortFilter(True)
        self.dataView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set filter options or hide
        if hasattr(self.proxymodel, "options"):
            self.filterComboBox.addItems(self.proxymodel.options)
        else:
            self.label_filter.hide()
            self.line.hide()
            self.filterComboBox.hide()

        # Add view to layout
        self.verticalLayout.addWidget(self.dataView)

        # Connect signals
        self.searchInput.textChanged.connect(self.proxymodel.setFilterFixedString)


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