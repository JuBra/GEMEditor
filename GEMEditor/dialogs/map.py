from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog, QListWidgetItem
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from GEMEditor.ui.MapDialog import Ui_MapDialog
from GEMEditor.ui.MapListDialog import Ui_MapListDialog
from GEMEditor.ui.WebViewDialog import Ui_WebViewDialog
from GEMEditor.analysis.networks import setup_map
from GEMEditor.data_classes import EscherMapGenerator
from escher.plots import Builder
import os

standard_escher_get_html_options = {"js_source": "web",
                                    "menu": "all",
                                    "scroll_behavior": "zoom",
                                    "minified_js": True,
                                    "html_wrapper": True,
                                    "never_ask_before_quit": True,
                                    "fill_screen": True,
                                    "protocol": "http",
                                    "enable_editing": True,
                                    "enable_keys": True,
                                    "height": "100%"}


class MapDialog(QDialog, Ui_MapDialog):
    def __init__(self, parent=None, reactions=None):
        super(MapDialog, self).__init__(parent)
        self.setupUi(self)
        self.reactions = reactions or []
        self.builder = Builder()

        self.webView.settings().setAttribute(QWebEngineSettings.DeveloperExtrasEnabled, True)
        self.webView.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.webView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.buttonDraw.clicked.connect(self.draw_map)

        if self.reactions:
            self.draw_map()

    @QtCore.pyqtSlot()
    def draw_map(self):
        if not self.reactions:
            return

        # Get escher compatible json
        escher_json = setup_map(reactions=self.reactions,
                                cofactors=self.parent().cofactors,
                                k=self.inputDistance.value(),
                                iterations=self.inputIterations.value(),
                                scaling=self.inputScaling.value(),
                                x_margin=self.inputXMargin.value(),
                                y_margin=self.inputYMargin.value())
        self.builder.map_json = escher_json
        self.builder._load_map()

        escher_html = self.builder._get_html(**standard_escher_get_html_options)

        self.webView.setHtml(escher_html)
        self.webView.page().mainFrame().evaluateJavaScript("zoom_extent_canvas()")

    def set_reactions(self, reaction_list):
        self.reactions = reaction_list

    def resizeEvent(self, QResizeEvent):
        super(MapDialog, self).resizeEvent(QResizeEvent)
        self.webView.page().mainFrame().evaluateJavaScript("window.escher.zoom_extent_canvas()")


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
        for element in self.maps:
            self.listWidget.addItem(QListWidgetItem(element.path))

    @QtCore.pyqtSlot()
    def delete_map(self):
        selected_indexes = sorted(self.listWidget.selectedIndexes(), key=lambda x: x.row(), reverse=True)
        for index in selected_indexes:
            self.maps.pop(index.row())
        self.update_items()

    @QtCore.pyqtSlot()
    def show_map(self):
        selected_indexes = self.listWidget.selectedIndexes()
        if selected_indexes and self.model:
            row = selected_indexes[0].row()
            map_builder = self.maps[row].get_escher_map()
            if map_builder:
                dialog = MapDisplayDialog(map_builder)
                self.model.dialogs.add(dialog)
                dialog.show()

    @QtCore.pyqtSlot()
    def load_maps(self):
        last_path = QtCore.QSettings().value("MapsLastPath", None)

        filenames, filter = QFileDialog().getOpenFileNamesAndFilter(self,
                                                                          self.tr("Select maps.."),
                                                                          last_path,
                                                                          self.tr("JSON file (*.json)"))

        if filenames:
            loaded_maps = [x.path for x in self.maps]
            for i, file_path in enumerate(filenames):
                if i == 0:
                    QtCore.QSettings().setValue("MapsLastPath", os.path.split(file_path)[0])

                if file_path in loaded_maps:
                    reply = QMessageBox.question(self, "Map already loaded?",
                                                       "The file '{}' has already been loaded. Do you want to reload this file?".format(file_path),
                                                       QMessageBox.Yes, QMessageBox.No)

                    if reply == QMessageBox.Yes:
                        index = loaded_maps.index(file_path)
                        with open(file_path) as read_file:
                            content = read_file.read()
                        self.maps[index] = EscherMapGenerator(content, file_path)
                    else:
                        continue
                else:
                    with open(file_path) as read_file:
                        content = read_file.read()
                    self.maps.append(EscherMapGenerator(content, file_path))
            self.update_items()


class MapDisplayDialog(QDialog, Ui_WebViewDialog):

    def __init__(self, map_builder):
        super(MapDisplayDialog, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window)

        self.map_builder = map_builder
        self.webView.settings().setAttribute(QWebEngineSettings.DeveloperExtrasEnabled, True)
        self.webView.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.webView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.webView.settings().setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        self.webView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)

        self.update_map()

    def update_map(self):
        if self.map_builder:
            self.webView.setHtml(self.map_builder._get_html(**standard_escher_get_html_options))
            self.webView.reload()

    def set_reaction_data(self, solution):
        self.map_builder.reaction_data = solution
        self.update_map()

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
