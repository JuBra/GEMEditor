from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QErrorMessage, QMessageBox, QMenu, QAction
from GEMEditor.base.dialogs import CustomStandardDialog
from GEMEditor.dialogs.standard import TableDisplayDialog
from GEMEditor.analysis.duplicates import merge_reactions
from GEMEditor.ui.TreeViewDialog import Ui_Duplicates
from GEMEditor.ui.LocalizationDialog import Ui_Dialog
from GEMEditor.widgets.tables import EvidenceTable, ReactionBaseTable
from GEMEditor.widgets.delegates import ComboBoxDelegate


class DuplicateDialog(CustomStandardDialog, Ui_Duplicates):

    def __init__(self, items_dict):
        super(DuplicateDialog, self).__init__()
        self.setupUi(self)
        self.items = None
        self.dataModel = QtGui.QStandardItemModel(self)
        self.setWindowTitle("Duplicate reactions")
        # self.dataModel.setColumnCount(7)
        self.dataModel.setHorizontalHeaderLabels(ReactionBaseTable.header)
        self.treeView.setModel(self.dataModel)
        self.set_items(items_dict)
        self.populate_tree()
        self.finished.connect(self.save_dialog_geometry)
        self.treeView.customContextMenuRequested.connect(self.showContextMenu)
        self.restore_dialog_geometry()

    def set_items(self, items_dict):
        """ Set the items for the tree model

        Parameters
        ----------
        items_dict: dict

        Returns
        -------

        """
        self.items = items_dict
        self.dataModel.setRowCount(0)
        self.populate_tree()

    def populate_tree(self):
        root_item = self.dataModel.invisibleRootItem()

        if self.items:
            n = 1
            for reaction_list in self.items.values():
                if len(reaction_list) > 1:
                    group_item = QtGui.QStandardItem("Group {}".format(str(n)))
                    for reaction in reaction_list:
                        group_item.appendRow(ReactionBaseTable.row_from_item(reaction))
                    n += 1
                    root_item.setChild(n-2, group_item)
            self.treeView.expandAll()

    @QtCore.pyqtSlot(QtCore.QPoint)
    def showContextMenu(self, pos):
        menu = QMenu()
        index = self.treeView.indexAt(pos)
        if index.isValid():
            item = self.dataModel.itemFromIndex(index)
            if item.parent() is None:
                set_subsystem_action = QAction(self.tr("Merge"), menu)
                set_subsystem_action.triggered.connect(self.merge_reactions)
                menu.addAction(set_subsystem_action)
                menu.exec_(self.treeView.viewport().mapToGlobal(pos))

    @QtCore.pyqtSlot()
    def merge_reactions(self):
        indices = self.treeView.selectedIndexes()
        first_index = sorted(indices, key=lambda x: x.column())[0]

        item = self.dataModel.itemFromIndex(first_index)
        child_reactions = [item.child(n, 0).link for n in range(item.rowCount())]
        reaction_ids = [reaction.id for reaction in child_reactions]
        reaction_id, status = QInputDialog.getItem(self, "Select the reaction to keep",
                                                         "Reaction:", reaction_ids, 0, False)
        if status:
            merge_reactions(child_reactions, child_reactions.pop(reaction_ids.index(reaction_id)))
            self.dataModel.removeRow(first_index.row())

    def restore_dialog_geometry(self):
        super(DuplicateDialog, self).restore_dialog_geometry()
        header_state = QtCore.QSettings().value(self.__class__.__name__ + "TableHeader")
        if header_state:
            self.treeView.header().restoreState(header_state)

    def save_dialog_geometry(self):
        super(DuplicateDialog, self).save_dialog_geometry()
        QtCore.QSettings().setValue(self.__class__.__name__ + "TableHeader",
                                    self.treeView.header().saveState())


class LocalizationCheck(CustomStandardDialog, Ui_Dialog):

    def __init__(self, model):
        super(LocalizationCheck, self).__init__()
        self.setupUi(self)
        self.model = model
        self.dataTable = QtGui.QStandardItemModel(self)
        self.tableView.setModel(self.dataTable)
        self.tableView.setItemDelegateForColumn(1, ComboBoxDelegate(parent=self.tableView,
                                                                    choices=list(self.model.compartments.values())))
        self.pushButton.clicked.connect(self.select_file)

    @QtCore.pyqtSlot()
    def select_file(self):
        filename, status = QFileDialog().getOpenFileName(self, "Select file..")
        if status and filename:
            with open(filename) as read_file:
                options = set()
                for line in read_file:
                    split_line = line.split("\t")
                    if len(split_line) != 2:
                        QErrorMessage().showMessage("Wrong file format!",
                                                          "The file format should be a tab seperated file where the "
                                                          "first column is the gene ID and the second column contains "
                                                          "a value indicating the compartment!")
                        return
                    options.add(split_line[1])

            self.label_2.setText(filename)
            self.dataTable.setRowCount(0)
            for element in options:
                self.dataTable.appendRow(QtGui.QStandardItem(element),
                                         QtGui.QStandardItem())


class FailingEvidencesDialog(TableDisplayDialog):

    def __init__(self, items_dict, model):
        TableDisplayDialog.__init__(self, items_dict, model, EvidenceTable)
        self.dataTable.setHorizontalHeaderItem(self.dataTable.columnCount()-1, QtGui.QStandardItem("Reason"))
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("Failed evidences")
        self.dataView.customContextMenuRequested.connect(self.showContextMenu)
        self.restore_dialog_geometry()

    def populate_table(self):
        for evidence, reason in self.items.items():
            self.dataTable.appendRow(self.dataTable.row_from_item(evidence)+[QtGui.QStandardItem(reason)])

    @QtCore.pyqtSlot()
    def fix_selection(self):
        selected_rows = sorted(self.dataView.get_selected_rows(), reverse=True)
        unfixed = 0
        for row in sorted(selected_rows, reverse=True):
            evidence = self.dataTable.item_from_row(row)
            status, error = evidence.fix()
            if status is True:
                self.dataTable.removeRow(row)
            else:
                self.dataTable.item(row, self.dataTable.columnCount()-1).setText(error)
                unfixed+=1

        if unfixed:
            QMessageBox().information(self, "Unfixed evidences", "Could not fix {} evidences.".format(str(unfixed)))

    @QtCore.pyqtSlot(QtCore.QPoint)
    def showContextMenu(self, pos):
        menu = QMenu()
        fix_evidences_action = QAction(self.tr("Fix evidences"), menu)
        fix_evidences_action.triggered.connect(self.fix_selection)
        menu.addAction(fix_evidences_action)
        menu.exec_(self.dataView.viewport().mapToGlobal(pos))
