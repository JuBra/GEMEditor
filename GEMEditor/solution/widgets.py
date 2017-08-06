from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush
from PyQt5.QtCore import Qt
from GEMEditor.ui.StandardTab import Ui_StandardTab
from GEMEditor.widgets.proxymodels import FluxTableProxyFilter
from GEMEditor.widgets.tables import ReactionBaseTable


class SolutionReactionTab(QWidget, Ui_StandardTab):

    def __init__(self):
        super(SolutionReactionTab, self).__init__()
        self.setupUi(self)

        # Setup table
        self.dataTable = QStandardItemModel(self)
        self.proxyModel = FluxTableProxyFilter(self)

        # Set filter properties
        self.proxyModel.setFilterKeyColumn(-1)
        self.proxyModel.setDynamicSortFilter(True)
        self.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)

        # Show filter label and combobox
        self.label_filter.setVisible(True)
        self.filterComboBox.setVisible(True)
        self.line.setVisible(True)

        # Connect filter
        self.filterComboBox.addItems(self.proxyModel.options)
        self.filterComboBox.currentIndexChanged.connect(self.proxyModel.set_custom_filter)

    def set_solution(self, solution, method):
        """ Set the solution to the widget
        
        Parameters
        ----------
        solution: cobra.Solution
        method: 

        Returns
        -------

        """
        
        # Clear table
        self.dataTable.setRowCount(0)

        # Only precede if both solution and method are specified
        if not (solution and method):
            return

        # Populate table
        if method == "fba":
            self.dataTable.setHorizontalHeaderLabels(ReactionBaseTable.header + ("Flux value",))
        elif method == "fva":
            self.dataTable.setHorizontalHeaderLabels(ReactionBaseTable.header + ("Min", "Max"))

        self.populate_table()

    def populate_table(self, solution, method):
        self.dataTable.blockSignals(True)

        if method == "fba":
            for i, reaction in enumerate(solution.reactions):
                # Get reaction items from standard reaction table
                reaction_items = ReactionBaseTable.row_from_item(reaction)
                flux_item = QStandardItem()
                flux_value = solution.fluxes[reaction.id]
                flux_item.setData(flux_value, 2)
                reaction_items.append(flux_item)
                self.dataTable.appendRow(reaction_items)
                
                if flux_value == reaction.upper_bound and flux_value != 0:
                    flux_item.setForeground(QBrush(Qt.red, Qt.SolidPattern))
                    reaction_items[5].setForeground(QBrush(Qt.red, Qt.SolidPattern))
                elif flux_value == reaction.lower_bound and flux_value != 0:
                    flux_item.setForeground(QBrush(Qt.red, Qt.SolidPattern))
                    reaction_items[4].setForeground(QBrush(Qt.red, Qt.SolidPattern))

        self.dataTable.blockSignals(False)
        self.proxyModel.setSourceModel(self.dataTable)




