from PyQt5.QtWidgets import QDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView


class MapDialog(QDialog):

    def __init__(self, *args):
        super(MapDialog, self).__init__(*args)
        self.webview = QWebEngineView(self)

    def update_map(self, reaction_data=None,
                   gene_data=None, metabolite_data=None):
        pass
