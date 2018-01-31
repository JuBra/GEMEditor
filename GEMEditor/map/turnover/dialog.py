import logging
import escher
import tempfile
import os
import uuid
import numpy
from GEMEditor.base import Settings, restore_state, restore_geometry
from GEMEditor.map.base import ESCHER_OPTIONS_LOCAL, replace_css_paths
from GEMEditor.map.turnover.generate import setup_turnover_map
from GEMEditor.map.turnover.ui import Ui_TurnoverDialog
from GEMEditor.model.display.tables import ReactionBaseTable
from GEMEditor.solution.analysis import get_rates
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
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
        self.mapView.load(QUrl("file:///"+self.temp_file.replace("\\", "/")))

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
        consuming, producing, inactive = QStandardItem("Consuming"), QStandardItem("Producing"), QStandardItem("Inactive")

        turnover = sum(v for v in rates.values() if v > 0.)

        for reaction, rate in sorted(rates.items(), key=lambda x: abs(x[1]), reverse=True):

            row = []
            try:
                row.append(QStandardItem('{:.2%}'.format(abs(rate/turnover))))
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
            item.setText(item.text()+" ({0!s})".format(item.rowCount()))
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
