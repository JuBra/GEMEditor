from collections import OrderedDict
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSortFilterProxyModel, pyqtSlot, QPoint
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QKeySequence
from PyQt5.QtWidgets import QWidget, QDialog, QAction, QMenu, QApplication, QMessageBox
from GEMEditor.base.classes import Settings
from GEMEditor.map.dialog import MapDisplayDialog
from GEMEditor.map.turnover import TurnoverDialog
from GEMEditor.model.display.tables import ReactionBaseTable, MetaboliteTable
from GEMEditor.solution.base import status_objective_from_solution, set_objective_to_label, set_status_to_label, \
    fluxes_from_solution, shadow_prices_from_solution
from GEMEditor.solution.ui import Ui_SearchTab, Ui_SolutionDialog


class BaseSolutionTab(QWidget, Ui_SearchTab):

    def __init__(self, ProxyModel, parent=None):
        super(BaseSolutionTab, self).__init__(parent)
        self.setupUi(self)

        # Store values
        self.model = None
        self.solution = None

        # Setup table
        self.dataTable = QStandardItemModel(self)
        self.proxyModel = ProxyModel(self)

        try:
            self.filterComboBox.addItems(self.proxyModel.options)
            self.filterComboBox.currentIndexChanged.connect(self.proxyModel.set_custom_filter)
        except AttributeError:
            # No custom filter options
            self.label_filter.setVisible(False)
            self.filterComboBox.setVisible(False)
            self.line.setVisible(False)
        else:
            # Show filter label and combobox
            self.label_filter.setVisible(True)
            self.filterComboBox.setVisible(True)
            self.line.setVisible(True)

        # Set filter properties
        self.proxyModel.setFilterKeyColumn(-1)
        self.proxyModel.setDynamicSortFilter(True)
        self.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.dataView.setModel(self.proxyModel)
        self.dataView.setDragEnabled(False)

        self.searchInput.textChanged.connect(self.proxyModel.setFilterFixedString)

    def set_solution(self, solution, model):
        """ Set the solution to the widget

        Parameters
        ----------
        solution: cobra.Solution
        method:

        Returns
        -------

        """
        self.solution = solution
        self.model = model
        self.populate_table(model=model, solution=solution)

    def populate_table(self, model, solution):
        raise NotImplementedError

    def run_population(self, items, values, row_factory):
        self.dataTable.blockSignals(True)
        self.dataTable.setRowCount(0)

        # Add rows to table
        for i, item in enumerate(items):
            row_items = row_factory(item)
            solution_item = QStandardItem()
            try:
                value = values[item.id]
            except KeyError:
                value = 0
            finally:
                solution_item.setData(float(value), 2)

            row_items.append(solution_item)
            self.dataTable.appendRow(row_items)

        self.dataTable.blockSignals(False)
        self.proxyModel.setSourceModel(self.dataTable)

    def save_geometry(self, prefix="", settings=None):
        settings = settings or Settings()
        settings.setValue(prefix+self.__class__.__name__,
                          self.dataView.horizontalHeader().saveState())

    def restore_geometry(self, prefix="", settings=None):
        settings = settings or Settings()
        state = settings.value(prefix+self.__class__.__name__)
        if state:
            self.dataView.horizontalHeader().restoreState(state)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Copy):
            self.copy_selection_to_clipboard()
        QWidget.keyPressEvent(self, event)

    def copy_selection_to_clipboard(self):
        indices = self.dataView.selectedIndexes()
        if not indices:
            return

        source_indices = [self.proxyModel.mapToSource(x) for x in indices]

        # Collect selected information by row
        row_data = OrderedDict()
        for idx in sorted(source_indices, key=lambda x: (x.row(), x.column())):
            item = self.dataTable.itemFromIndex(idx)
            row = idx.row()
            if row not in row_data:
                row_data[row] = [item.text()]
            else:
                row_data[row].append(item.text())

        # Row items and rows to copy them to clipboard
        content = "\n".join(["\t".join(v) for k, v in sorted(row_data.items(), key=lambda x: x[0])])
        clipboard = QApplication.clipboard()
        clipboard.setText(content)


class ReactionTab(BaseSolutionTab):

    def __init__(self, parent=None):
        super(ReactionTab, self).__init__(FluxTableProxyFilter, parent)
        self.dataTable.setHorizontalHeaderLabels(ReactionBaseTable.header + ("Flux",))

        self.dataView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dataView.customContextMenuRequested.connect(self.show_context_menu)

    def populate_table(self, model, solution):
        self.dataTable.setRowCount(0)
        if not solution or not model:
            return
        else:
            fluxes = fluxes_from_solution(solution)

        self.run_population(model.reactions, fluxes, ReactionBaseTable.row_from_item)
        self.color_values_at_bound()

    def color_values_at_bound(self):
        if not self.model:
            return

        col = self.dataTable.columnCount() - 1
        for i in range(self.dataTable.rowCount()):
            flux_item = self.dataTable.item(i, col)
            value = flux_item.data(2)
            if not value:
                continue

            # Get reaction settings
            lower_bound = self.dataTable.item(i, 4).data(2)
            upper_bound = self.dataTable.item(i, 5).data(2)

            # Color flux value if close to boundary
            if value >= 0.99 * upper_bound or value <= 0.99 * lower_bound:
                flux_item.setForeground(QBrush(Qt.red, Qt.SolidPattern))

    @pyqtSlot(QPoint)
    def show_context_menu(self, pos):
        idx = self.dataView.indexAt(pos)
        if idx.isValid():
            menu = QMenu()
            action_maps = QAction("Show on maps")
            action_maps.triggered.connect(lambda x: self.open_maps(idx))
            menu.addAction(action_maps)
            menu.exec_(self.dataView.viewport().mapToGlobal(pos))

    @pyqtSlot()
    def open_maps(self, idx):
        if idx.isValid():
            # Get selected metabolite
            source_idx = self.proxyModel.mapToSource(idx)
            reaction_id = self.dataTable.item(source_idx.row()).text()
            reaction = self.model.reactions.get_by_id(reaction_id)

            maps = [m for m in self.model.gem_maps.values()
                    if reaction in m]
            if not maps:
                QMessageBox().information(None, "Not found", "No map containing this reaction found.")
            else:
                dialog = MapDisplayDialog(maps)
                dialog.set_reaction_data(self.solution)
                self.model.dialogs.add(dialog)
                dialog.show()


class MetaboliteTab(BaseSolutionTab):
    def __init__(self, parent=None):
        super(MetaboliteTab, self).__init__(QSortFilterProxyModel, parent)
        self.dataTable.setHorizontalHeaderLabels(MetaboliteTable.header+("Shadow price",))

        # Allow custom context menu
        self.dataView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dataView.customContextMenuRequested.connect(self.show_context_menu)

    def populate_table(self, model, solution):
        self.dataTable.setRowCount(0)
        if not solution or not model:
            return
        else:
            prices = shadow_prices_from_solution(solution)

        self.run_population(model.metabolites, prices, MetaboliteTable.row_from_item)

    @pyqtSlot(QPoint)
    def show_context_menu(self, pos):
        idx = self.dataView.indexAt(pos)
        if idx.isValid():
            menu = QMenu()
            action_turnover = QAction("Open turnover graph")
            action_turnover.triggered.connect(lambda x: self.open_turnover_graph(idx))
            menu.addAction(action_turnover)
            menu.exec_(self.dataView.viewport().mapToGlobal(pos))

    @pyqtSlot()
    def open_turnover_graph(self, idx):
        if idx.isValid():
            # Get selected metabolite
            source_idx = self.proxyModel.mapToSource(idx)
            met_id = self.dataTable.item(source_idx.row()).text()
            metabolite = self.model.metabolites.get_by_id(met_id)

            dialog = TurnoverDialog()
            dialog.set_solution(self.solution, metabolite)
            self.model.dialogs.add(dialog)
            dialog.show()


class SolutionDialog(QDialog, Ui_SolutionDialog):

    def __init__(self, solution, model):
        super(SolutionDialog, self).__init__()
        self.setupUi(self)
        self.solution = None
        self.model = None

        # Setup dialog
        self.tabWidget.addTab(ReactionTab(self), "Reactions")
        self.tabWidget.addTab(MetaboliteTab(self), "Metabolite")
        self.setWindowTitle("Solution")
        self.setWindowFlags(Qt.Window)
        self.finished.connect(self.save_geometry)

        # Update display
        self.set_solution(solution, model)
        self.restore_geometry()

    def set_solution(self, solution, model):
        """ Set solution to dialog

        Parameters
        ----------
        solution
        method

        Returns
        -------

        """
        self.solution = solution
        self.model = model

        # Update labels
        status, objective = status_objective_from_solution(solution)
        set_status_to_label(self.label_status, status)
        set_objective_to_label(self.label_label_objective, objective)

        # Update tables
        for i in range(self.tabWidget.count()):
            self.tabWidget.widget(i).set_solution(self.solution, self.model)

    @pyqtSlot()
    def save_geometry(self, prefix="", settings=None):
        settings = settings or Settings()
        string = prefix+self.__class__.__name__
        settings.setValue(string, self.saveGeometry())
        for i in range(self.tabWidget.count()):
            self.tabWidget.widget(i).save_geometry(string, settings)
        settings.sync()

    def restore_geometry(self, prefix="", settings=None):
        settings = settings or Settings()
        string = prefix + self.__class__.__name__
        state = settings.value(string)
        if state:
            self.restoreGeometry(state)
        for i in range(self.tabWidget.count()):
            self.tabWidget.widget(i).restore_geometry(string, settings)


class FluxTableProxyFilter(QSortFilterProxyModel):

    options = ("All", "Nonzero flux", "Flux at bound", "All boundary", "Active boundary")

    def __init__(self, *args, **kwargs):
        super(FluxTableProxyFilter, self).__init__(*args, **kwargs)
        self.custom_filter = 0

    def filterAcceptsRow(self, p_int, QModelIndex):
        if self.filterRegExp():
            return (self.passes_custom_filter(p_int) and
                    super(FluxTableProxyFilter, self).filterAcceptsRow(p_int, QModelIndex))
        else:
            return self.passes_custom_filter(p_int)

    def passes_custom_filter(self, row):
        if self.custom_filter == 0:
            # All rows
            return True
        elif self.custom_filter == 1:
            # Flux nonequal to zero
            return self.sourceModel().item(row, 7).data(2) != 0.
        elif self.custom_filter == 2:
            # Flux at boundary
            flux = self.sourceModel().item(row, 7).data(2)
            lower_bound = self.sourceModel().item(row, 4).data(2)
            upper_bound = self.sourceModel().item(row, 5).data(2)
            return flux == lower_bound or flux == upper_bound
        elif self.custom_filter == 3:
            # Boundary reaction
            reaction = self.sourceModel().item(row, 0).link
            return reaction.boundary is True
        elif self.custom_filter == 4:
            reaction = self.sourceModel().item(row, 0).link
            flux = self.sourceModel().item(row, 7).data(2)
            return reaction.boundary and flux != 0.
        else:
            raise NotImplementedError

    @QtCore.pyqtSlot(int)
    def set_custom_filter(self, n):
        self.custom_filter = n
        self.invalidateFilter()
