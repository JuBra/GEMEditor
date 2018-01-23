import logging
from PyQt5 import QtCore
from PyQt5.QtWidgets import QPushButton, QDialogButtonBox, QDialog
from GEMEditor.base import Settings, restore_geometry, restore_state
from GEMEditor.database.match.ui.ManualMetaboliteMatchDialog import Ui_ManualMatchDialog
from GEMEditor.database.base import MetaboliteEntryDisplayWidget


LOGGER = logging.getLogger(__name__)


class ManualMatchDialog(QDialog, Ui_ManualMatchDialog):

    def __init__(self, parent=None, unmatched_items=None):
        super(ManualMatchDialog, self).__init__(parent)
        self.setupUi(self)

        # Store unmatched item for iteration
        self.unmatched_items = unmatched_items or {}
        if isinstance(unmatched_items, dict):
            self.unmatched_items = list(unmatched_items.items())
            # Sort unmatched according to candidates - easy choices first
            self.unmatched_items.sort(key=lambda x: len(x[1]))

        # Keep track of the current metabolite
        self.current_index = -1
        self.current_metabolite = None
        self.current_entries = None

        # Keep track of matched items
        self.manual_mapped = dict()

        self.button_prev_item = QPushButton("Previous")
        self.button_next_item = QPushButton("Next")
        self.buttonBox.addButton(self.button_prev_item, QDialogButtonBox.ActionRole)
        self.buttonBox.addButton(self.button_next_item, QDialogButtonBox.ActionRole)

        self.connect_signals()
        if self.unmatched_items:
            self.next_metabolite()

        # Restore appearance
        self.restore_appearance()

    def connect_signals(self):

        # Connect entry buttons
        self.button_next_entry.clicked.connect(self.next_entry)
        self.button_select.clicked.connect(self.select_or_deselect_entry)
        self.button_previous_entry.clicked.connect(self.previous_entry)

        # Connect display update when changing index of entries
        self.stackedWidget_database.currentChanged.connect(self.update_entry_label)
        self.stackedWidget_database.currentChanged.connect(self.update_database_buttons)
        self.stackedWidget_database.currentChanged.connect(self.update_selection_status)

        # Connect buttonbox buttons
        self.button_prev_item.clicked.connect(self.previous_metabolite)
        self.button_next_item.clicked.connect(self.next_metabolite)

        # Store appearance upon closing
        self.finished.connect(self.save_appearance)

    @property
    def current_entry_id(self):
        """ Get the entry id from the currently selected """
        entry_index = self.stackedWidget_database.currentIndex()
        return self.current_entries[entry_index]

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
        # Block signals
        self.stackedWidget_database.blockSignals(True)

        # Clear existing widgets
        for idx in reversed(range(self.stackedWidget_database.count())):
            widget = self.stackedWidget_database.widget(idx)
            self.stackedWidget_database.removeWidget(widget)
            # Delete widget in order to avoid lagging
            # when changing widget
            widget.deleteLater()

        # Add new widgets
        for entry in entries:
            # Setup widget
            widget = MetaboliteEntryDisplayWidget(self)
            widget.update_from_database_id(entry)

            # Add widget to the dialog
            self.stackedWidget_database.addWidget(widget)

        # Unblock signals
        self.stackedWidget_database.blockSignals(False)

        # Update view
        self.stackedWidget_database.currentChanged.emit(0)

    def update_metabolite_index(self, new_idx):
        if new_idx in range(len(self.unmatched_items)):
            metabolite, entries = self.unmatched_items[new_idx]

            # Update current items
            self.current_index = new_idx
            self.current_metabolite = metabolite

            # Sort selected entry to be on index 0
            if metabolite in self.manual_mapped:
                mapped_value = self.manual_mapped[metabolite]
                self.current_entries = sorted(entries, key=lambda x: x != mapped_value)
            else:
                self.current_entries = entries

            # Update display
            self.populate_model_metabolite(metabolite)
            self.populate_database_entries(self.current_entries)
            self.update_item_buttons(new_idx)

    def update_entry_index(self, new_idx):
        if new_idx in range(self.stackedWidget_database.count()):
            self.stackedWidget_database.setCurrentIndex(new_idx)

    @QtCore.pyqtSlot()
    def next_metabolite(self):
        self.update_metabolite_index(self.current_index + 1)

    @QtCore.pyqtSlot()
    def previous_metabolite(self):
        self.update_metabolite_index(self.current_index - 1)

    @QtCore.pyqtSlot()
    def next_entry(self):
        """ Move entry display widget to next entry """
        self.update_entry_index(self.stackedWidget_database.currentIndex() + 1)

    @QtCore.pyqtSlot()
    def previous_entry(self):
        """ Move entry display widget to previous entry """
        self.update_entry_index(self.stackedWidget_database.currentIndex() - 1)

    @QtCore.pyqtSlot()
    def select_or_deselect_entry(self):
        """ Add or remove current mapping """

        entry_id = self.current_entry_id
        metabolite = self.current_metabolite

        # Change mapping
        if self.entry_is_active_mapped(entry_id):
            # Delete mapping if already mapped
            del self.manual_mapped[metabolite]
        else:
            # Save mapping if not mapped
            self.manual_mapped[metabolite] = entry_id

        # Update widgets
        self.update_selection_status()
        self.next_metabolite()

    @QtCore.pyqtSlot()
    def update_selection_status(self):
        """ Update selection button and background """
        if self.entry_is_active_mapped(self.current_entry_id):
            self.button_select.setText("deselect")
            self.groupBox_database.setStyleSheet("QGroupBox{background-color: #d9f2e4;}")
        else:
            self.button_select.setText("select")
            self.groupBox_database.setStyleSheet("QGroupBox{background-color: none;}")

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
    def update_item_buttons(self, idx):
        self.button_prev_item.setEnabled(idx > 0)
        self.button_next_item.setEnabled(idx+1 < len(self.unmatched_items))

    def entry_is_active_mapped(self, entry_id):
        try:
            return self.manual_mapped[self.current_metabolite] == entry_id
        except KeyError:
            return False

    def restore_appearance(self):
        settings = Settings(group=self.__class__.__name__)
        restore_geometry(self, settings.value("Geometry"))
        restore_state(self.splitter, settings.value("SplitterState"))

    def save_appearance(self):
        with Settings(group=self.__class__.__name__) as settings:
            settings.setValue("Geometry", self.saveGeometry())
            settings.setValue("SplitterState", self.splitter.saveState())
