from PyQt5.QtWidgets import QDialog
from GEMEditor.
from .ui.ManualMetaboliteMatchDialog import Ui_Dialog


class MatchMetaboliteDialog(QDialog, Ui_Dialog):

    def __init__(self, database):
        super(MatchMetaboliteDialog, self).__init__()
        self.setupUi(self)
        self.unmatched_items = None

    def _set_model_item(self, metabolite):
        pass

    def _set_database_items(self, items):
        pass

    def set_unmatched_items(self, items):
        pass

    def _next_database_entry(self):
        pass

    def _previous_database_entry(self):
        pass

    def _update_database_button_states(self):
        pass

    def _save_selection(self):
        pass

    def _skip_selection(self):
        pass

