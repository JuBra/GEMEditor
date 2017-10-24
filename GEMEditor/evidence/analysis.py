from collections import defaultdict
from PyQt5.QtWidgets import QDialog, QTreeView, QTableView, QProgressDialog, QAction, QMenu, QMessageBox
from PyQt5.QtGui import QStandardItem
from PyQt5.QtCore import QSortFilterProxyModel, QSettings, pyqtSlot, QPoint, Qt
from GEMEditor.evidence.assertions import assertion_to_group
from GEMEditor.widgets.tables import EvidenceTable
from GEMEditor.widgets.proxymodels import RecursiveProxyFilter
from GEMEditor.base.widgets import SearchTableWidget
from GEMEditor.evidence.ui.DialogEvidenceStatus import Ui_DialogEvidenceStatus


class DialogEvidenceStatus(QDialog, Ui_DialogEvidenceStatus):

    def __init__(self, model):
        super(DialogEvidenceStatus, self).__init__()
        self.setupUi(self)
        self.model = model

        # Add failing tab
        self.tab_failing = SearchTableWidget(self, EvidenceTable, RecursiveProxyFilter, QTreeView)
        self.tab_error = SearchTableWidget(self, EvidenceTable, QSortFilterProxyModel, QTableView)
        self.tab_conflict = SearchTableWidget(self, EvidenceTable, RecursiveProxyFilter, QTreeView)

        self.tabWidget.addTab(self.tab_conflict, "Conflicts")
        self.tabWidget.addTab(self.tab_failing, "Failing")
        self.tabWidget.addTab(self.tab_error, "Errors")

        self.finished.connect(self.save_dialog_state)
        self.tab_failing.dataView.customContextMenuRequested.connect(self.showContextMenu)
        self.tab_failing.dataView.setContextMenuPolicy(Qt.CustomContextMenu)

        self.update_evidences()
        self.restore_dialog_geometry()

    def update_evidences(self):
        progress = QProgressDialog(self)
        conflicts, failing, error = sort_evidences(self.model.all_evidences.values())

        # Populate tables
        self.tab_error.datatable.populate_table(error)
        self.populate_tree(self.tab_failing.datatable, failing, EvidenceTable.row_from_item)
        self.tab_failing.dataView.expandAll()
        self.populate_tree(self.tab_conflict.datatable, conflicts, EvidenceTable.row_from_item)
        self.tab_conflict.dataView.expandAll()

        self.update_labels()
        progress.close()

    @pyqtSlot()
    def update_labels(self):
        # Set labels
        self.tabWidget.setTabText(0, "Conflicts({0!s})".format(self.tab_conflict.datatable.rowCount()))
        self.tabWidget.setTabText(1, "Failing({0!s})".format(self.tab_failing.datatable.rowCount()))
        self.tabWidget.setTabText(2, "Errors({0!s})".format(self.tab_error.datatable.rowCount()))

    @staticmethod
    def populate_tree(data_model, items, row_factory):
        # Clear existing items
        data_model.setRowCount(0)

        # Load new items
        root_item = data_model.invisibleRootItem()
        if items:
            n = 1
            for i, item_list in enumerate(sorted(items, key=lambda x: len(x), reverse=True)):
                if len(item_list) > 1:
                    group_item = QStandardItem("Group {}".format(str(n)))
                    for item in item_list:
                        group_item.appendRow(row_factory(item))
                    n += 1
                    root_item.setChild(i, group_item)
                else:
                    root_item.appendRow(row_factory(item_list[0]))

    @pyqtSlot(QPoint)
    def showContextMenu(self, pos):
        """ Show context menu

        Parameters
        ----------
        pos: QPoint

        Returns
        -------
        None
        """
        menu = QMenu()
        index = self.tab_failing.dataView.indexAt(pos)
        if index.isValid():
            action_fix_evidence = QAction(self.tr("Fix evidence"), menu)
            action_fix_evidence.triggered.connect(self.fix_failing)
            menu.addAction(action_fix_evidence)
            menu.exec_(self.tab_failing.dataView.viewport().mapToGlobal(pos))

    @pyqtSlot()
    def fix_failing(self):
        """ Fix the selected evidence item"""
        view = self.tab_failing.dataView
        proxy = self.tab_failing.proxymodel
        table = self.tab_failing.datatable

        indices = view.selectedIndexes()
        first_index = sorted(indices, key=lambda x: x.column())[0]
        real_index = proxy.mapToSource(first_index)
        item = table.itemFromIndex(real_index)
        parent = item.parent()
        if parent is None:
            if item.child(0, 0):
                evidence = item.child(0,0).link
            else:
                evidence = item.link

            if evidence.fix():
                table.removeRow(real_index.row())
            else:
                QMessageBox().warning(None, "Fix evidence", "Fixing evidence failed!")
        else:
            if item.link.fix():
                parent_idx = table.indexFromItem(parent)
                table.removeRow(parent_idx.row())
            else:
                QMessageBox().warning(None, "Fix evidence", "Fixing evidence failed!")

        self.update_labels()

    @pyqtSlot()
    def save_dialog_state(self):
        settings = QSettings()
        settings.setValue(self.__class__.__name__+"Geometry", self.saveGeometry())
        settings.setValue(self.__class__.__name__ + "ErrorTable",
                          self.tab_error.dataView.horizontalHeader().saveState())
        settings.setValue(self.__class__.__name__ + "ConflictTable",
                          self.tab_conflict.dataView.header().saveState())
        settings.setValue(self.__class__.__name__ + "Failingtable",
                          self.tab_failing.dataView.header().saveState())
        settings.sync()

    def restore_dialog_geometry(self):
        # Restore the geometry of the dialog
        # Should be called in the __init__(self) of the subclass
        settings = QSettings()
        geometry = settings.value(self.__class__.__name__+"Geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)
        error_header = settings.value(self.__class__.__name__ + "ErrorTable")
        if error_header is not None:
            self.tab_error.dataView.horizontalHeader().restoreState(error_header)
        conflict_header = settings.value(self.__class__.__name__ + "ConflictTable")
        if conflict_header is not None:
            self.tab_conflict.dataView.header().restoreState(conflict_header)
        failing_header = settings.value(self.__class__.__name__ + "Failingtable")
        if failing_header is not None:
            self.tab_failing.dataView.header().restoreState(failing_header)


def sort_evidences(evidences):
    """ Sort evidence into groups

    Parameters
    ----------
    evidences: list

    Returns
    -------

    """

    errors = list()
    grouped = defaultdict(list)
    conflicts = list()
    failing = list()

    # Filter out erroneous evidences
    for evidence in evidences:
        if evidence.is_valid() is None:
            errors.append(evidence)
        else:
            key = (evidence.entity, evidence.target, assertion_to_group[evidence.assertion])
            grouped[key].append(evidence)

    # Filter groups that are all valid
    for group in grouped.values():
        # More than one evidence in group
        # Add to conflicts if any evidence invalid
        status = set([x.is_valid() for x in group])
        if len(status) > 1:
            conflicts.append(group)
        elif status.pop() is True:
            continue
        else:
            failing.append(group)

    return conflicts, failing, errors

