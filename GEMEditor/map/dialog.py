import json
import logging
import escher
import tempfile
import os
import uuid
from GEMEditor.base import Settings, restore_state, restore_geometry
from GEMEditor.map.base import MapWrapper, WrongEscherFormat, ESCHER_OPTIONS_LOCAL, replace_css_paths
from GEMEditor.map.ui import Ui_MapListDialog, Ui_TurnoverDialog
from GEMEditor.map.turnover import setup_turnover_map
from GEMEditor.model.display.tables import ReactionBaseTable
from GEMEditor.solution.base import fluxes_from_solution
from GEMEditor.solution.analysis import get_rates
from PyQt5 import QtCore
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import QDialog, QFileDialog, QListWidgetItem, QMessageBox, QWidget, QVBoxLayout, QTabWidget,\
    QDialogButtonBox, QAbstractItemView


LOGGER = logging.getLogger(__name__)


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
        self.webView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
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


class TurnoverDialog(QDialog, Ui_TurnoverDialog):
    """ Dialog used for the display of metabolite turnover

    This dialog shows the turnover of a specific metabolite
    from a given solution. The turnover is displayed in two
    forms:
    1)  A map showing the active reactions
    2)  A table listing the individual contributions of the
        reactions

    """

    def __init__(self, parent=None):
        super(TurnoverDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Window)

        # Store input
        self.metabolite = None
        self.solution = None
        self.temp_file = os.path.join(tempfile.gettempdir(),
                                      "{0!s}.html".format(uuid.uuid4()))

        # Setup data structures
        self.datatable = QStandardItemModel(self)
        self.datatable.setHorizontalHeaderLabels(("%", "Rate") + ReactionBaseTable.header)
        self.dataView.setModel(self.datatable)
        self.dataView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.mapView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)

        # Connect signals/slots
        self.finished.connect(self.save_settings)
        self.finished.connect(self.delete_temp_file)

        # Restore settings
        self._restore_settings()

    def set_solution(self, solution, metabolite):
        self.metabolite = metabolite
        self.solution = solution

        if metabolite and solution:
            rates = get_rates(solution.fluxes, metabolite)
            self._refresh_map(rates)
            self._populate_tree(rates)
            self.setWindowTitle("{0!s} turnover".format(metabolite.id))

    def _refresh_map(self, rates):
        """ Refresh the map being displayed

        Generate a map from the set solution
        and metabolite. Only display those
        reactions that are active in the set
        solution if hide_active is set.

        Returns
        -------
        None
        """

        # Generate escher turnover map
        builder = escher.Builder(map_json=setup_turnover_map(self.metabolite, rates),
                                 reaction_data=self.solution.fluxes.to_dict())
        html = builder._get_html(**ESCHER_OPTIONS_LOCAL)

        # As Qt does not allow the loading of local files
        # from html set via the setHtml method, write map
        # to file and read it back to webview
        with open(self.temp_file, "w") as ofile:
            ofile.write(replace_css_paths(html))
        self.mapView.load(QtCore.QUrl("file:///" + self.temp_file.replace("\\", "/")))

    def _populate_tree(self, rates):
        """ Populate the datamodel from reactions

        Show the reactions participating in the
        metabolism of the specific metabolite.

        Returns
        -------
        None
        """

        # Delete old entries
        self.datatable.setRowCount(0)

        # Setup items
        consuming, producing, inactive = QStandardItem("Consuming"), QStandardItem("Producing"), QStandardItem(
            "Inactive")

        turnover = sum(v for v in rates.values() if v > 0.)

        for reaction, rate in sorted(rates.items(), key=lambda x: abs(x[1]), reverse=True):

            row = []
            try:
                row.append(QStandardItem('{:.2%}'.format(abs(rate / turnover))))
            except ZeroDivisionError:
                row.append(QStandardItem("0"))
            finally:
                row.append(QStandardItem(str(rate)))
                row.extend(ReactionBaseTable.row_from_item(reaction))

            if rate > 0:
                producing.appendRow(row)
            elif rate < 0:
                consuming.appendRow(row)
            else:
                inactive.appendRow(row)

        # Add nodes
        root = self.datatable.invisibleRootItem()
        for i, item in enumerate((consuming, producing, inactive)):
            item.setText(item.text() + " ({0!s})".format(item.rowCount()))
            root.setChild(i, item)

        # Expand consuming/producing node
        for item in (consuming, producing):
            self.dataView.expand(self.datatable.indexFromItem(item))

    def _restore_settings(self):
        """ Restore dialog geometry from setting

        Returns
        -------

        """
        with Settings(group=self.__class__.__name__) as settings:
            restore_state(self.dataView.header(), settings.value("TableHeader"))
            restore_geometry(self, settings.value("DialogGeometry"))
            restore_state(self.splitter, settings.value("SplitterState"))

    def save_settings(self):
        """ Store dialog geometry in settings

        Returns
        -------
        None
        """
        with Settings(group=self.__class__.__name__) as settings:
            settings.setValue("SplitterState", self.splitter.saveState())
            settings.setValue("TableHeader", self.dataView.header().saveState())
            settings.setValue("DialogGeometry", self.saveGeometry())

    def delete_temp_file(self):
        """ Delete temporary file created when displaying map

        Returns
        -------

        """

        try:
            os.remove(self.temp_file)
        except:
            pass
