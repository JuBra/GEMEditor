import json
import logging
import os
from GEMEditor.map.base import MapWrapper, WrongEscherFormat
from GEMEditor.map.ui import Ui_MapListDialog
from GEMEditor.solution.base import fluxes_from_solution
from GEMEditor.base.classes import Settings
from PyQt5 import QtCore
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEnginePage, QWebEngineView
from PyQt5.QtWidgets import QDialog, QFileDialog, QListWidgetItem, QMessageBox, QWidget, QVBoxLayout, QTabWidget,\
    QDialogButtonBox

LOGGER = logging.getLogger(__name__)


get_html_options = {"js_source": "web",
                    "menu": "none",
                    "scroll_behavior": "zoom",
                    "html_wrapper": True,
                    "protocol": "https"}


class MapListDialog(QDialog, Ui_MapListDialog):
    """ Open escher maps dialog

    Displays loaded maps in a list and lets
    the user add additional maps from files
    or delete existing ones """

    def __init__(self, parent, model):
        """ Initialize

        Parameters
        ----------
        parent: QWidget or None
        model: GEMEditor.model.classes.cobra.Model
        """

        super(MapListDialog, self).__init__(parent)
        self.setupUi(self)
        self.model = model
        self.maps = model.gem_maps
        self.update_items()

        # Connect buttons
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
            dialog = MapDisplayDialog((builder,))
            self.model.dialogs.add(dialog)
            dialog.show()

    @QtCore.pyqtSlot()
    def load_maps(self):
        settings = Settings()
        last_path = settings.value("MapsLastPath", None)

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
                LOGGER.debug("Loading map: {0!s}".format(path))
                with open(path) as read_file:
                    content = read_file.read()
                    try:
                        loaded_map = MapWrapper(map_json=content, path=path)
                    except json.JSONDecodeError:
                        LOGGER.debug("The file is not properly formatted JSON and has been skipped.")
                        QMessageBox().critical(None, "Format error",
                                               "'{0!s}' is not proper JSON and has been skipped.".format(path))
                        continue
                    except WrongEscherFormat as e:
                        LOGGER.debug(e, exc_info=True)
                        QMessageBox().critical(None, "Format error",
                                               "'{0!s}' is not proper escher JSON and has been skipped.".format(path))
                        continue
                    else:
                        self.maps[path] = loaded_map
                        LOGGER.debug("Map added.")

            if i == 0 and os.path.dirname(path) != last_path:
                new_path = os.path.dirname(path)
                settings.setValue("MapsLastPath", new_path)
                LOGGER.debug("Setting '{0!s}' set to '{1!s}'".format("MapsLastPath", new_path))

        # Update view
        self.update_items()


class MapDisplayWidget(QWidget):

    def __init__(self, map_builder, parent=None):
        super(MapDisplayWidget, self).__init__(parent)
        self.map_builder = map_builder

        # Setup widget
        self.webpage = QWebEnginePage()
        self.webView = QWebEngineView(self)
        self.webView.setPage(self.webpage)
        layout = QVBoxLayout(self)
        layout.addWidget(self.webView)
        self.setLayout(layout)

        # Change view settings
        self.webView.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.webView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.webView.settings().setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        self.webView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)

    def update_map(self, **kwargs):
        if self.map_builder:
            LOGGER.debug("Setting map html to webview")
            self.webView.setHtml(self.map_builder.get_html(**kwargs))

    def set_reaction_data(self, solution):
        """ Display solution data in map

        Parameters
        ----------
        solution: cobra.Solution

        Returns
        -------

        """

        fluxes = fluxes_from_solution(solution)
        self.update_map(reaction_data=dict(fluxes))

    def set_gene_data(self, gene_data):
        self.update_map(gene_data=gene_data)

    def set_metabolite_data(self, metabolite_data):
        self.update_map(metabolite_data=metabolite_data)


class MapDisplayDialog(QDialog):

    def __init__(self, map_builders=()):
        super(MapDisplayDialog, self).__init__()
        self.setWindowFlags(QtCore.Qt.Window)

        self.widgets = []

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        if len(map_builders) == 1:
            widget = MapDisplayWidget(map_builders[0])
            layout.addWidget(widget)
            self.widgets.append(widget)
        else:
            tabwidget = QTabWidget(self)
            layout.addWidget(tabwidget)
            for builder in map_builders:
                widget = MapDisplayWidget(builder)
                tabwidget.addTab(widget, builder.display_path)
                self.widgets.append(widget)

        # Add a button box
        buttonbox = QDialogButtonBox(QDialogButtonBox.Close)
        buttonbox.rejected.connect(self.reject)
        layout.addWidget(buttonbox)

        self.update_map()

    def update_map(self, **kwargs):
        for widget in self.widgets:
            widget.update_map(**kwargs)

    def set_reaction_data(self, solution):
        """ Display solution data in map

        Parameters
        ----------
        solution: cobra.Solution

        Returns
        -------

        """
        for widget in self.widgets:
            widget.set_reaction_data(solution)

    def set_gene_data(self, gene_data):
        for widget in self.widgets:
            widget.set_gene_data(gene_data)

    def set_metabolite_data(self, metabolite_data):
        for widget in self.widgets:
            widget.set_metabolite_data(metabolite_data)
