import os
import logging
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QFileDialog, QListWidgetItem
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEnginePage
from GEMEditor.ui.MapListDialog import Ui_MapListDialog
from GEMEditor.ui.WebViewDialog import Ui_WebViewDialog
from escher.plots import Builder
from cobra.core.solution import Solution, LegacySolution

LOGGER = logging.getLogger(__name__)


get_html_options = {"js_source": "web",
                    "menu": "none",
                    "scroll_behavior": "zoom",
                    "html_wrapper": True,
                    "protocol": "https"}


class MapListDialog(QDialog, Ui_MapListDialog):
    def __init__(self, parent, maps, model):
        super(MapListDialog, self).__init__(parent)
        self.setupUi(self)
        self.maps = maps
        self.model = model
        self.update_items()
        self.listWidget.doubleClicked.connect(self.show_map)
        self.addButton.clicked.connect(self.load_maps)
        self.delButton.clicked.connect(self.delete_map)

    def update_items(self):
        self.listWidget.clear()
        for path in self.maps.keys():
            self.listWidget.addItem(QListWidgetItem(path))

    @QtCore.pyqtSlot()
    def delete_map(self):
        selected_items = self.listWidget.selectedItems()
        for item in selected_items:
            del self.maps[item.text()]
        self.update_items()

    @QtCore.pyqtSlot()
    def show_map(self):
        selected_items = self.listWidget.selectedItems()
        for item in selected_items:
            builder = self.maps[item.text()]
            dialog = MapDisplayDialog(builder)
            self.model.dialogs.add(dialog)
            dialog.show()

    @QtCore.pyqtSlot()
    def load_maps(self):
        last_path = QtCore.QSettings().value("MapsLastPath", None)

        # Get file names to open
        file_paths, _ = QFileDialog.getOpenFileNames(self,
                                                     self.tr("Select maps.."),
                                                     last_path,
                                                     self.tr("JSON file (*.json)"))

        # Load maps into escher builder objects
        for i, path in enumerate(file_paths):
            if path in self.maps:
                LOGGER.debug("{} already in list -> skipped.".format(path))
            else:
                LOGGER.debug("Loading map: {}".format(path))
                with open(path) as read_file:
                    content = read_file.read()

                # Add Builder
                builder = Builder(map_json=content)
                self.maps[path] = builder
                LOGGER.debug("Map added.")

            # Store last path
            if i == 0:
                new_path = os.path.split(path)[0]
                QtCore.QSettings().setValue("MapsLastPath", new_path)
                LOGGER.debug("MapsLastPath set to: {}".format(new_path))

        # Update view
        self.update_items()


class MapDisplayDialog(QDialog, Ui_WebViewDialog):

    def __init__(self, map_builder):
        super(MapDisplayDialog, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window)

        self.map_builder = map_builder
        self.webpage = QWebEnginePage()
        self.webView.setPage(self.webpage)
        self.webView.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.webView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.webView.settings().setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        self.webView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)

        self.update_map()

    def update_map(self):
        if self.map_builder:
            LOGGER.debug("Setting map html to webview")
            map_html = self.map_builder._get_html(**get_html_options)
            self.webView.setHtml(map_html)
        else:
            LOGGER.debug("map_builder not set to dialog.")

    def set_reaction_data(self, solution):
        """ Display solution data in map

        Parameters
        ----------
        solution: cobra.Solution

        Returns
        -------

        """

        if isinstance(solution, dict):
            # Set solution to builder
            self.map_builder.reaction_data = solution
            LOGGER.debug("Flux dictionary set to map".format(solution))
            self.update_map()
        elif isinstance(solution, LegacySolution):
            # Set solution to builder
            self.map_builder.reaction_data = solution.x_dict
            LOGGER.debug("Solution {0!s} set to map.".format(solution))
            self.update_map()
        elif isinstance(solution, Solution):
            LOGGER.warning("Display of new cobra solution not implemented")
            return
        elif solution:
            LOGGER.warning("Unexpected type {0!s} passed to set_reaction_data".format(type(solution)))
            return

    def set_gene_data(self, gene_data):
        self.map_builder.gene_data = gene_data
        self.update_map()

    def set_metabolite_data(self, metabolite_data):
        self.map_builder.metabolite_data = metabolite_data
        self.update_map()

    def resizeEvent(self, QResizeEvent):
        super(MapDisplayDialog, self).resizeEvent(QResizeEvent)

        # Workaround for calling the resize canvas function of escher
        # Posting a Ctrl + 1 key combination to the webview
        event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, QtCore.Qt.Key_1, QtCore.Qt.ControlModifier)
        QtCore.QCoreApplication.postEvent(self.webView, event)
