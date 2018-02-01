import webbrowser
from GEMEditor.base.ui.TableDisplayWidgetAddDel import Ui_TableDisplayWidgetAddDel
from GEMEditor.base.widgets import TableDisplayWidget
from GEMEditor.model.classes.evidence import Evidence
from GEMEditor.model.display.tables import AnnotationTable, EvidenceTable
from GEMEditor.model.display.ui.CommentDisplayWidget import Ui_CommentDisplayWidget
from GEMEditor.model.edit.annotation import EditAnnotationDialog
from GEMEditor.model.edit.evidence import EditEvidenceDialog
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMenu, QAction, QWidget


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
        dialog = EditAnnotationDialog(self.display_item)
        if dialog.exec_():
            new_annotation = dialog.get_annotation()
            if new_annotation not in self.get_annotation():
                self.dataTable.update_row_from_item(dialog.get_annotation())

    @QtCore.pyqtSlot()
    def edit_item(self):
        row = self.dataView.get_selected_rows(get_first_only=True)[0]
        annotation = self.dataTable.item_from_row(row)
        dialog = EditAnnotationDialog(self.display_item, annotation)
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
