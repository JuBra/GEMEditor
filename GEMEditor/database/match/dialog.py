import logging
from PyQt5 import QtCore
from PyQt5.QtWidgets import QPushButton, QDialogButtonBox, QWidget, QDialog, QTableWidgetItem
from GEMEditor.database.ui.MetaboliteEntryDisplayWidget import Ui_MetaboliteEntryDisplayWidget
from GEMEditor.database.ui.ManualMetaboliteMatchDialog import Ui_ManualMatchDialog
from GEMEditor.database.base import DatabaseWrapper


LOGGER = logging.getLogger(__name__)


class MetaboliteEntryDisplayWidget(QWidget, Ui_MetaboliteEntryDisplayWidget):

    def __init__(self):
        super(MetaboliteEntryDisplayWidget, self).__init__()
        self.setupUi(self)

    def set_information(self, metabolite, synonyms=()):
        """ Update the information from the metabolite
        and the synonyms passed

        Parameters
        ----------
        metabolite: GEMEditor.cobraClasses.Metabolite
        synonyms: list

        Returns
        -------
        None
        """

        # Update labels
        self.label_name.setText(str(metabolite.name))
        self.label_charge.setText(str(metabolite.charge))
        self.label_formula.setText(str(metabolite.formula))

        # Update synonyms
        self.list_synonyms.clear()
        for entry in synonyms:
            self.list_synonyms.addItem(entry)

        # Update identifiers
        self.table_identifiers.setRowCount(len(metabolite.annotation))
        self.table_identifiers.setColumnCount(2)

        # Add identifiers
        n = 0
        for annotation in metabolite.annotation:
            self.table_identifiers.setItem(n, 0, QTableWidgetItem(annotation.collection))
            self.table_identifiers.setItem(n, 1, QTableWidgetItem(annotation.identifier))
            n += 1

        # Reset header items
        self.table_identifiers.setHorizontalHeaderLabels(["Resource", "ID"])


class ManualMatchDialog(QDialog, Ui_ManualMatchDialog):

    def __init__(self, parent=None, unmatched_items=None):
        super(ManualMatchDialog, self).__init__(parent)
        self.setupUi(self)
        self.unmatched_items = unmatched_items
        self.current_metabolite = None
        self.current_entries = None
        self.manual_mapped = dict()
        self.database = DatabaseWrapper()

        self.button_save = QPushButton("Save match")
        self.button_skip = QPushButton("Skip")
        self.buttonBox.addButton(self.button_save, QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.button_skip, QDialogButtonBox.ActionRole)

        self.connect_signals()
        self.next_metabolite()

    def connect_signals(self):

        # Connect entry buttons
        self.button_next_entry.clicked.connect(self.next_entry)
        self.button_previous_entry.clicked.connect(self.previous_entry)

        # Connect display update when changing index of entries
        self.stackedWidget_database.currentChanged.connect(self.update_entry_label)
        self.stackedWidget_database.currentChanged.connect(self.update_database_buttons)

        # Connect buttonbox buttons
        self.button_save.clicked.connect(self.save_mapping)
        self.button_skip.clicked.connect(self.next_metabolite)

    def populate_model_metabolite(self, metabolite):
        self.display_model_metabolite.set_metabolite(metabolite)

    def populate_database_entries(self, entries):
        """ Populate the stacked widget for database entries

        Parameters
        ----------
        entries: list

        Returns
        -------
        None
        """

        # Clear existing widgets
        for idx in reversed(range(self.stackedWidget_database.count())):
            self.stackedWidget_database.removeWidget(self.stackedWidget_database.widget(idx))

        # Add new widgets
        for entry in entries:
            widget = MetaboliteEntryDisplayWidget()

            # Setup widget
            metabolite = self.database.get_metabolite_from_id(entry)
            synonyms = self.database.get_synonyms_from_id(entry, entry_type="Metabolite")
            annotations = self.database.get_annotations_from_id(entry, entry_type="Metabolite")
            if metabolite is None:
                raise ValueError("No entry found for '{}'".format(entry))
            metabolite.annotation.update(annotations)
            widget.set_information(metabolite, synonyms)

            # Add widget to the dialog
            self.stackedWidget_database.addWidget(widget)

        # Update view
        self.update_database_buttons(0)
        self.update_entry_label(0)

    @QtCore.pyqtSlot()
    def next_metabolite(self):
        # Return if no unmatched items are set
        if self.unmatched_items is None:
            return

        try:
            metabolite, entries = self.unmatched_items.popitem()
        except KeyError:
            # Close dialog if there is no more metabolite to match
            self.close()
        else:
            # Update current items
            self.current_metabolite = metabolite
            self.current_entries = entries

            # Update display
            self.populate_model_metabolite(metabolite)
            self.populate_database_entries(entries)

    @QtCore.pyqtSlot()
    def next_entry(self):
        """ Move entry display widget to next entry """
        current_index = self.stackedWidget_database.currentIndex()
        if current_index + 1 < self.stackedWidget_database.count():
            self.stackedWidget_database.setCurrentIndex(current_index+1)

    @QtCore.pyqtSlot()
    def previous_entry(self):
        """ Move entry display widget to previous entry """
        current_index = self.stackedWidget_database.currentIndex()
        if current_index > 0:
            self.stackedWidget_database.setCurrentIndex(current_index-1)

    @QtCore.pyqtSlot(int)
    def update_database_buttons(self, idx):
        """ Disable or enable buttons to switch database item

        Parameters
        ----------
        idx: int

        Returns
        -------

        """
        count = self.stackedWidget_database.count()
        self.button_next_entry.setEnabled(idx+1 < count)
        self.button_previous_entry.setEnabled(idx != 0)

    @QtCore.pyqtSlot(int)
    def update_entry_label(self, idx):
        """ Update label according to the index

        Parameters
        ----------
        idx

        Returns
        -------

        """
        self.label.setText("{0!s} / {1!s}".format(idx+1,
                                                  self.stackedWidget_database.count()))

    @QtCore.pyqtSlot()
    def save_mapping(self):

        entries_idx = self.stackedWidget_database.currentIndex()
        if self.current_metabolite is not None:
            self.manual_mapped[self.current_metabolite] = self.current_entries[entries_idx]

        # Move to next metabolite
        self.next_metabolite()

    def closeEvent(self, QCloseEvent):
        LOGGER.debug("Closing dialog.")
        self.database.close()
        super(ManualMatchDialog, self).closeEvent(QCloseEvent)
