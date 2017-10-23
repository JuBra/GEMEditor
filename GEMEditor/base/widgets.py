from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMenu, QAction, QWidget, QAbstractItemView
from PyQt5 import QtCore, QtGui
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
        QtGui.QDesktopServices().openUrl(
            QtCore.QUrl("http://identifiers.org/{collection}/{identifier}".format(collection=self.item(row, 0).text(),
                                                                                  identifier=self.item(row, 1).text())))


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
