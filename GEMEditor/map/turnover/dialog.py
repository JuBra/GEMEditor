import logging
import escher
from collections import defaultdict
from GEMEditor.base import Settings, restore_state, restore_geometry
from GEMEditor.map.base import ESCHER_GET_HTML_OPTIONS
from GEMEditor.map.turnover.generate import setup_turnover_map
from GEMEditor.map.turnover.ui import Ui_TurnoverDialog
from GEMEditor.model.display.tables import ReactionBaseTable
from GEMEditor.solution.analysis import get_turnover
from GEMEditor.solution.base import fluxes_from_solution
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWebEngineWidgets import QWebEngineSettings, QWebEnginePage
from PyQt5.QtWidgets import QDialog, QAbstractItemView


LOGGER = logging.getLogger(__name__)


class TurnoverDialog(QDialog, Ui_TurnoverDialog):
    """ Dialog used for the display of metabolite turnover

    This dialog shows the turnover of a specific metabolite
    from a given solution. The turnover is displayed in two
    forms:
    1)  A circular diagram showing the reactions
    2)  A table listing the individual contributions of the
        reactions
    Users can select to only show reactions that are active
    in the given solution. This choice is stored in the
    settings. """

    def __init__(self, parent=None):
        super(TurnoverDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.Window)

        # Store input
        self.metabolite = None
        self.solution = None

        # Setup data structures
        self.datatable = QStandardItemModel(self)
        self.datatable.setHorizontalHeaderLabels(("%", "Rate") + ReactionBaseTable.header)
        self.dataView.setModel(self.datatable)
        self.dataView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.webpage = QWebEnginePage(self)
        self.mapView.setPage(self.webpage)
        self.mapView.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.mapView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.mapView.settings().setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        self.mapView.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)

        # Connect signals/slots
        self.finished.connect(self.save_settings)

        # Restore settings
        self._restore_settings()

    def set_solution(self, solution, metabolite):
        self.metabolite = metabolite
        self.solution = solution

        if metabolite:
            self._refresh_map()
            self._populate_tree()
            self.setWindowTitle("{0!s} turnover".format(metabolite.id))

    def _refresh_map(self):
        """ Refresh the map being displayed

        Generate a map from the set solution
        and metabolite. Only display those
        reactions that are active in the set
        solution if hide_active is set.

        Returns
        -------
        None
        """

        if not self.metabolite:
            # Can not display map if metabolite is not set
            return

        # Standard settings for drawing map
        reactions = self.metabolite.reactions
        fluxes = None

        # Change settings according to state
        if self.solution:
            fluxes = dict(fluxes_from_solution(self.solution))
            reactions = [r for r in self.metabolite.reactions
                         if r.id in fluxes and fluxes[r.id] > 0]

        # Generate escher turnover map
        map_json = setup_turnover_map(self.metabolite, reactions)
        builder = escher.Builder(map_json=map_json, reaction_data=fluxes)
        self.mapView.setHtml(builder._get_html(**ESCHER_GET_HTML_OPTIONS))

    def _populate_tree(self):
        """ Populate the datamodel from reactions

        Show the reactions participating in the
        metabolism of the specific metabolite.

        Returns
        -------
        None
        """
        self.datatable.setRowCount(0)
        if not self.metabolite:
            # There is nothing to load
            return
        elif self.solution:
            fluxes = fluxes_from_solution(self.solution)
        else:
            fluxes = defaultdict(int)

        consuming, producing, inactive = QStandardItem(), QStandardItem(), QStandardItem()

        rates = {}
        turnover = get_turnover(fluxes, self.metabolite)

        for reaction in self.metabolite.reactions:
            coeff = reaction.metabolites[self.metabolite]
            rates[reaction] = coeff * fluxes[reaction.id]

        for reaction, rate in sorted(rates.items(), key=lambda x: abs(x[1]), reverse=True):
            percent_item, rate_item = QStandardItem(), QStandardItem(str(rate))
            try:
                percent_item.setText('{:.2%}'.format(abs(rate/turnover)))
            except ZeroDivisionError:
                percent_item.setText('0')

            row = [percent_item, rate_item] + ReactionBaseTable.row_from_item(reaction)

            if rate > 0:
                producing.appendRow(row)
            elif rate < 0:
                consuming.appendRow(row)
            else:
                inactive.appendRow(row)

        consuming.setText("Consuming ({0!s})".format(consuming.rowCount()))
        producing.setText("Producing ({0!s})".format(producing.rowCount()))
        inactive.setText("Inactive ({0!s})".format(inactive.rowCount()))

        root = self.datatable.invisibleRootItem()
        root.setChild(0, consuming)
        root.setChild(1, producing)
        root.setChild(2, inactive)

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
