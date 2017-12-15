from collections import OrderedDict
from PyQt5.QtCore import Qt, QSortFilterProxyModel, pyqtSlot, QPoint
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QDialog, QAction, QMenu, QApplication, QMessageBox
from GEMEditor.base import Settings, restore_state
from GEMEditor.map.dialog import MapDisplayDialog
from GEMEditor.map.turnover import TurnoverDialog
from GEMEditor.solution.base import status_objective_from_solution, set_objective_to_label, set_status_to_label
from GEMEditor.solution.ui import Ui_SearchTab, Ui_SolutionDialog
from GEMEditor.solution.tables import FBATable, FBAProxy, FVATable, FVAProxy, ReactionDeletionTable, DeletionProxy, GeneDeletionTable, ShadowPriceTable


class BaseSolutionTab(QWidget, Ui_SearchTab):

    def __init__(self, Table, Proxy, parent=None):
        super(BaseSolutionTab, self).__init__(parent)
        self.setupUi(self)

        # Store values
        self.model = None
        self.solution = None

        # Setup table
        self.dataTable = Table(self)
        self.proxyModel = Proxy(self)

        try:
            self.filterComboBox.addItems(self.proxyModel.options)
            self.filterComboBox.currentTextChanged.connect(self.proxyModel.set_filter)
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
        finally:
            self.searchInput.textChanged.connect(self.proxyModel.setFilterFixedString)

        # Set filter properties
        self.proxyModel.setSourceModel(self.dataTable)
        self.proxyModel.setFilterKeyColumn(-1)
        self.proxyModel.setDynamicSortFilter(True)
        self.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.dataView.setModel(self.proxyModel)
        self.dataView.setDragEnabled(False)

    def set_solution(self, model, solution):
        """ Set the solution to the widget

        Parameters
        ----------
        model: GEMEditor.model.classes.Model,
            Model for which the solution has been generated
        solution: cobra.core.Solution or pandas.Dataframe,
            Solution to display

        """
        self.solution = solution
        self.model = model
        self.dataTable.set_solution(model, solution)

    def save_geometry(self, settings):
        settings.setValue(self.__class__.__name__+"TableHeader",
                          self.dataView.horizontalHeader().saveState())

    def restore_geometry(self, settings):
        restore_state(self.dataView.horizontalHeader(),
                      settings.value(self.__class__.__name__+"TableHeader"))

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

    def __init__(self, Table, Proxy, parent=None):
        super(ReactionTab, self).__init__(Table, Proxy, parent)

        self.dataView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dataView.customContextMenuRequested.connect(self.show_context_menu)

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
    def __init__(self, Table, Proxy, parent=None):
        super(MetaboliteTab, self).__init__(Table, Proxy, parent)

        # Allow custom context menu
        self.dataView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dataView.customContextMenuRequested.connect(self.show_context_menu)

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


class GeneTab(BaseSolutionTab):

    def __init__(self, Table, Proxy, parent=None):
        super(GeneTab, self).__init__(Table, Proxy, parent)


class SolutionDialog(QDialog, Ui_SolutionDialog):

    def __init__(self):
        super(SolutionDialog, self).__init__()
        self.setupUi(self)
        self.solution = None
        self.model = None

        self.setWindowTitle("Solution")
        self.setWindowFlags(Qt.Window)
        self.finished.connect(self.save_geometry)

    def add_tab(self, tab, description):
        self.tabWidget.addTab(tab, description)

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
            self.tabWidget.widget(i).set_solution(model, solution)

    @pyqtSlot()
    def save_geometry(self):
        with Settings(group=self.__class__.__name__) as settings:
            settings.setValue("DialogGeometry", self.saveGeometry())

            for i in range(self.tabWidget.count()):
                self.tabWidget.widget(i).save_geometry(settings)

    def restore_geometry(self):
        with Settings(group=self.__class__.__name__) as settings:
            restore_state(self, settings.value("DialogGeometry"))

            for i in range(self.tabWidget.count()):
                self.tabWidget.widget(i).restore_geometry(settings)


def factory_solution(model, solution):
    """ Factory for solution dialogs

    Parameters
    ----------
    model: GEMEditor.model.classes.Model,
        Model for which the solution was calculated
    solution: cobra.core.Solution or pandas.Dataframe,
        Simulation solution to visualized

    Returns
    -------
    dialog: SolutionDialog,
        SolutionDialog instance

    """
    dialog = SolutionDialog()
    method = solution.method
    if method == "fba":
        dialog.add_tab(factory_reaction_tab(method), "Reactions")
        dialog.add_tab(MetaboliteTab(ShadowPriceTable, QSortFilterProxyModel), "Metabolites")
    elif method == "fva":
        dialog.add_tab(factory_reaction_tab(method), "Reactions")
    elif method == "single_reaction_deletion":
        dialog.add_tab(factory_reaction_tab(method), "Reactions")
    elif method == "single_gene_deletion":
        dialog.add_tab(GeneTab(GeneDeletionTable, DeletionProxy), "Genes")

    dialog.set_solution(solution, model)
    dialog.restore_geometry()
    return dialog


def factory_reaction_tab(method):
    if method == "fba":
        return ReactionTab(FBATable, FBAProxy)
    elif method == "fva":
        return ReactionTab(FVATable, FVAProxy)
    elif method == "single_reaction_deletion":
        return ReactionTab(ReactionDeletionTable, DeletionProxy)
