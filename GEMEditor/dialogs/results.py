from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QSortFilterProxyModel
from GEMEditor.base.dialogs import CustomStandardDialog
from GEMEditor.widgets.tables import ReactionBaseTable, MetaboliteTable
from GEMEditor.ui.ResultDialog import Ui_Dialog
from GEMEditor.widgets.proxymodels import FluxTableProxyFilter
from GEMEditor.data_classes import EscherMapGenerator
from GEMEditor.analysis.networks import setup_turnover_map
from GEMEditor.map.escher import MapDisplayDialog


class ResultDialog(CustomStandardDialog, Ui_Dialog):
    def __init__(self, proxyclass):
        CustomStandardDialog.__init__(self)
        self.setupUi(self)
        self.dataTable = QtGui.QStandardItemModel(self)
        self.proxyModel = proxyclass(self)
        self.proxyModel.setFilterKeyColumn(-1)
        self.proxyModel.setDynamicSortFilter(True)
        self.proxyModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.dataView.setModel(self.proxyModel)

        self.searchInput.textChanged.connect(self.proxyModel.setFilterFixedString)

    def populate_table(self, items, solution_dict):
        self.dataTable.blockSignals(True)
        self.dataTable.setRowCount(0)
        for i, item in enumerate(items):
            try:
                solution_value = solution_dict[item.id]
            except KeyError:
                solution_value = "NA"
            self.add_item_to_table(item, solution_value, row=i)
        self.dataTable.blockSignals(False)
        self.proxyModel.setSourceModel(self.dataTable)

    def add_item_to_table(self, item, solution, row):
        raise NotImplemented

    @QtCore.pyqtSlot()
    def save_header_state(self):
        settings = QtCore.QSettings()
        settings.setValue(self.__class__.__name__+"DataViewHeader",
                          self.dataView.horizontalHeader().saveState())
        settings.sync()

    def restore_header_state(self):
        header_state = QtCore.QSettings().value(self.__class__.__name__+"DataViewHeader")
        if header_state is not None:
            self.dataView.horizontalHeader().restoreState(header_state)


class FluxValueDialog(ResultDialog):

    def __init__(self, model, solution):
        ResultDialog.__init__(self, proxyclass=FluxTableProxyFilter)
        self.setWindowTitle(self.tr("Flux values"))
        self.filterComboBox.addItems(FluxTableProxyFilter.options)
        self.populate_table(model.reactions, solution.x_dict)
        self.dataTable.setHorizontalHeaderLabels(ReactionBaseTable.header + ("Flux value",))
        self.filterComboBox.currentIndexChanged.connect(self.proxyModel.set_custom_filter)
        self.restore_dialog_geometry()
        self.restore_header_state()

    def add_item_to_table(self, reaction, flux_value, row):
        items = ReactionBaseTable.row_from_item(reaction)
        flux_item = QtGui.QStandardItem()
        flux_item.setData(flux_value, 2)
        items.append(flux_item)
        self.dataTable.appendRow(items)
        if flux_value == reaction.upper_bound and flux_value != 0:
            flux_item.setForeground(QtGui.QBrush(QtCore.Qt.red, QtCore.Qt.SolidPattern))
            items[5].setForeground(QtGui.QBrush(QtCore.Qt.red, QtCore.Qt.SolidPattern))
        elif flux_value == reaction.lower_bound and flux_value != 0:
            flux_item.setForeground(QtGui.QBrush(QtCore.Qt.red, QtCore.Qt.SolidPattern))
            items[4].setForeground(QtGui.QBrush(QtCore.Qt.red, QtCore.Qt.SolidPattern))

    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Copy):
            self.copySelectionToClipboard()
        elif event.matches(QtGui.QKeySequence.Delete):
            self.deleteItemSlot()
        QWidget.keyPressEvent(self, event)

    def copySelectionToClipboard(self):
        selection = self.dataView.get_selected_indexes()
        if selection:
            selection_dict = {}
            for element in sorted(selection, key=lambda x: (x.row(), x.column())):
                element_text = self.dataTable.itemFromIndex(element).text()
                try:
                    selection_dict[element.row()].append(element_text)
                except KeyError:
                    selection_dict[element.row()] = [element_text]
            text = "\n".join(["\t".join(selection_dict[key]) for key in selection_dict.keys()])
            clipboard = QApplication.clipboard()
            clipboard.setText(text)


class DualValueDialog(ResultDialog):
    def __init__(self, model, solution):
        ResultDialog.__init__(self, QSortFilterProxyModel)
        self.setWindowTitle(self.tr("Dual values"))
        self.populate_table(model.metabolites, solution.y_dict)
        self.model = model
        self.solution = solution
        self.dataTable.setHorizontalHeaderLabels(MetaboliteTable.header+("Dual Value",))
        self.filterComboBox.setVisible(False)
        self.line.setVisible(False)
        self.label_filter.setVisible(False)
        self.dataView.doubleClicked.connect(self.open_turnover_graph)
        self.restore_dialog_geometry()
        self.restore_header_state()

    def add_item_to_table(self, metabolite, solution, row):
        items = MetaboliteTable.row_from_item(metabolite)
        dual_value = QtGui.QStandardItem()
        dual_value.setData(solution, 2)
        items.append(dual_value)
        self.dataTable.insertRow(row, items)

    @QtCore.pyqtSlot()
    def open_turnover_graph(self):
        items = self.dataView.get_selected_rows(get_first_only=True)
        if items:
            metabolite = self.model.metabolites.get_by_id(self.dataTable.item(items[0]).text())
            map_string = setup_turnover_map(metabolite)
            builder = EscherMapGenerator(map_string)
            dialog = MapDisplayDialog(builder.get_escher_map())
            dialog.set_reaction_data(self.solution.x_dict)
            self.model.dialogs.add(dialog)
            dialog.show()
