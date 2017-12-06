import webbrowser
from GEMEditor.base.ui.TableDisplayWidgetAddDel import Ui_TableDisplayWidgetAddDel
from GEMEditor.base.widgets import TableDisplayWidget
from GEMEditor.model.classes.evidence import Evidence
from GEMEditor.model.display.tables import AnnotationTable, EvidenceTable, LinkedReferenceTable
from GEMEditor.model.display.ui.CommentDisplayWidget import Ui_CommentDisplayWidget
from GEMEditor.model.display.ui.SettingDisplayWiget import Ui_SettingsDisplayWidget
from GEMEditor.model.edit.annotation import EditAnnotationDialog
from GEMEditor.model.edit.evidence import EditEvidenceDialog
from GEMEditor.model.selection import ReferenceSelectionDialog
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMenu, QAction, QWidget, QAbstractItemView


class AnnotationDisplayWidget(TableDisplayWidget, Ui_TableDisplayWidgetAddDel):

    dataType = "Annotation"

    def __init__(self, parent=None):
        TableDisplayWidget.__init__(self, parent)
        self.dataTable = AnnotationTable(self)
        self.setupUi(self)

        self.model = None
        self.display_item = None

        self.dataView.setModel(self.dataTable)
        self.setup_signals()

    @QtCore.pyqtSlot()
    def add_item(self):
        dialog = EditAnnotationDialog(None, self.display_item)
        if dialog.exec_():
            new_annotation = dialog.get_annotation()
            if new_annotation not in self.get_annotation():
                self.dataTable.update_row_from_item(dialog.get_annotation())

    @QtCore.pyqtSlot()
    def edit_item(self):
        row = self.dataView.get_selected_rows(get_first_only=True)[0]
        annotation = self.dataTable.item_from_row(row)
        dialog = EditAnnotationDialog(annotation, self.display_item)
        if dialog.exec_():
            self.dataTable.update_row_from_item(dialog.get_annotation(), row)

    def set_item(self, item, model):
        self.model = model
        self.display_item = item
        if item:
            self.dataTable.populate_table(item.annotation)

    def get_annotation(self):
        """ Get the current annotation from the table """
        return self.dataTable.get_items()

    @QtCore.pyqtSlot(QtCore.QPoint)
    def showContextMenu(self, pos):
        menu = QMenu()

        if self.dataView.get_selected_rows():
            open_browser_action = QAction(self.tr("Open in browser"), menu)
            open_browser_action.triggered.connect(self.open_browser)
            menu.addAction(open_browser_action)
            menu.addSeparator()
        self.add_standard_menu_actions(menu)

        menu.exec_(self.dataView.viewport().mapToGlobal(pos))

    def open_browser(self):
        selected_rows = self.dataView.get_selected_rows()
        for row in selected_rows:
            item = self.dataTable.item(row).link
            webbrowser.open("http://identifiers.org/{0}/{1}".format(item.collection, item.identifier))

    @property
    def content_changed(self):
        return self.display_item.annotation != set(self.get_annotation())

    @QtCore.pyqtSlot()
    def save_state(self):
        """ Save the annotations from the table to the reaction """
        self.display_item.annotation.clear()
        self.display_item.annotation.update(self.dataTable.get_items())


class EvidenceDisplayWidget(TableDisplayWidget, Ui_TableDisplayWidgetAddDel):

    # DataType is used to display the correct names in the context menu
    dataType = "Evidence"

    def __init__(self, parent=None):
        TableDisplayWidget.__init__(self, parent)
        self.dataTable = EvidenceTable(self)
        self.setupUi(self)

        self.model = None
        self.item = None

        self.dataView.setModel(self.dataTable)

        self.setup_signals()

    def set_item(self, item, model):
        self.item = item
        self.model = model
        # Populate the datatable with one-way linked copies i.e. the evidence only points
        # to the items, reference etc. but not vice versa
        if item:
            self.dataTable.populate_table([x.copy() for x in item.evidences])

    @QtCore.pyqtSlot()
    def add_item(self):
        new_evidence = Evidence()
        # Set base_item externally in order to avoid linkage from base_item to
        # evidence
        new_evidence.entity = self.item
        dialog = EditEvidenceDialog(self.window(), self.model, evidence=new_evidence)
        if dialog.exec_():
            self.dataTable.update_row_from_item(new_evidence)

    @QtCore.pyqtSlot()
    def edit_item(self):
        row = self.dataView.get_selected_rows(get_first_only=True)[0]
        evidence = self.dataTable.item_from_row(row)
        dialog = EditEvidenceDialog(self.window(), self.model, evidence=evidence)
        if dialog.exec_():
            self.dataTable.update_row_from_link(row)

    @property
    def content_changed(self):
        if not self.item:
            return False
        else:
            dict1 = dict((x.internal_id, x) for x in self.item.evidences)
            dict2 = dict((x.internal_id, x) for x in self.dataTable.get_items())
            if dict1.keys() != dict2.keys():
                return True

            for x in dict1:
                if dict1[x] != dict2[x]:
                    return True
            return False

    @QtCore.pyqtSlot()
    def save_state(self):
        """ Save the annotations from the table to the reaction """

        # Remove all existing evidences
        for evidence in list(self.item.evidences):
            evidence.delete_links()

        # Setup modified evidences
        for evidence in self.dataTable.get_items():
            evidence.setup_links()
            self.model.all_evidences[evidence.internal_id] = evidence


class CommentDisplayWidget(QWidget, Ui_CommentDisplayWidget):

    changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.commentInput.textChanged.connect(self.changed.emit)
        self.display_item = None

    def set_item(self, item, *args, **kwargs):
        self.display_item = item
        self.commentInput.clear()
        if item:
            self.commentInput.setText(item.comment)

    @property
    def content_changed(self):
        if self.display_item is None:
            return False
        return self.commentInput.toPlainText() != self.display_item.comment

    @QtCore.pyqtSlot()
    def save_state(self):
        self.display_item.comment = self.commentInput.toPlainText()


class ReferenceDisplayWidget(QWidget, Ui_SettingsDisplayWidget):

    changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(ReferenceDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        self.dataTable = LinkedReferenceTable(self)
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