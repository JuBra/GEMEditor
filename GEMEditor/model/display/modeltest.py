from GEMEditor.base.delegates import FloatInputDelegate, ComboBoxDelegate
from GEMEditor.model.classes.modeltest import ReactionSetting, GeneSetting, Outcome
from GEMEditor.model.display.tables import ReactionSettingsTable, GeneSettingsTable, OutcomesTable
from GEMEditor.model.display.ui.SettingDisplayWiget import Ui_SettingsDisplayWidget
from GEMEditor.model.selection import ReactionSelectionDialog, GeneSelectionDialog
from GEMEditor.solution.base import fluxes_from_solution
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QWidget


class ReactionSettingDisplayWidget(QWidget, Ui_SettingsDisplayWidget):

    changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(ReactionSettingDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        self.dataTable = ReactionSettingsTable(self)
        self.tableView.setModel(self.dataTable)
        self.tableView.setItemDelegateForColumn(1, FloatInputDelegate(parent=self.tableView, precision=1))
        self.tableView.setItemDelegateForColumn(2, FloatInputDelegate(parent=self.tableView, precision=1))
        self.tableView.setItemDelegateForColumn(3, FloatInputDelegate(parent=self.tableView, precision=1))

        self.model = None
        self.model_test = None

        self.setup_signals()

    def setup_signals(self):
        self.button_add_current.clicked.connect(self.add_current)
        self.button_add_item.clicked.connect(self.add_setting)
        self.button_del_item.clicked.connect(self.tableView.delete_selected_rows)
        self.tableView.selectionModel().selectionChanged.connect(self.toggle_condition_del_button)

        self.dataTable.rowsRemoved.connect(self.changed.emit)
        self.dataTable.rowsInserted.connect(self.changed.emit)
        self.dataTable.dataChanged.connect(self.changed.emit)

    def set_item(self, model_test, model):
        """ Set the item to the current widget

        Parameters
        ----------
        model_test : GEMEditor.data_classes.ModelTest
        model : GEMEditor.model.classes.cobra.Model

        Returns
        -------
        None
        """
        self.model_test = model_test
        self.model = model

        self.dataTable.setRowCount(0)
        if self.model_test:
            self.dataTable.populate_table(model_test.reaction_settings)

    @QtCore.pyqtSlot()
    def add_setting(self):
        dialog = ReactionSelectionDialog(self.model)

        if dialog.exec_():
            for reaction in dialog.selected_items():
                if reaction not in set([self.dataTable.item(i).link for i in range(self.dataTable.rowCount())]):
                    self.dataTable.update_row_from_item(ReactionSetting(reaction=reaction,
                                                                        upper_bound=reaction.upper_bound,
                                                                        lower_bound=reaction.lower_bound,
                                                                        objective_coefficient=reaction.objective_coefficient))

    @QtCore.pyqtSlot()
    def add_current(self):
        known_reactions = set([self.dataTable.item(i).link for i in range(self.dataTable.rowCount())])

        for reaction in self.model.reactions:
            if reaction in known_reactions:
                continue
            elif (reaction.boundary is True and reaction.lower_bound != 0.) or reaction.objective_coefficient != 0.:
                self.dataTable.update_row_from_item(ReactionSetting(reaction=reaction,
                                                                    upper_bound=reaction.upper_bound,
                                                                    lower_bound=reaction.lower_bound,
                                                                    objective_coefficient=reaction.objective_coefficient))

    @QtCore.pyqtSlot()
    def toggle_condition_del_button(self):
        status = len(self.tableView.get_selected_indexes()) > 0
        self.button_del_item.setEnabled(status)

    @property
    def content_changed(self):
        if self.model_test:
            return self.model_test.reaction_settings != self.dataTable.get_items()
        else:
            return False

    def valid_input(self):
        if self.dataTable.rowCount() == 0:
            return False
        else:
            return all(x.is_valid() for x in self.dataTable.get_items())

    def save_state(self):
        self.model_test.reaction_settings = self.dataTable.get_items()


class GeneSettingDisplayWidget(QWidget, Ui_SettingsDisplayWidget):

    changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(GeneSettingDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        self.dataTable = GeneSettingsTable(self)
        self.tableView.setModel(self.dataTable)
        self.tableView.setItemDelegateForColumn(1, ComboBoxDelegate(parent=self.tableView,
                                                                    choices=["active", "inactive"],
                                                                    select_option=False))

        self.model = None
        self.model_test = None

        self.setup_signals()

    def setup_signals(self):
        self.button_add_current.clicked.connect(self.add_current)
        self.button_add_item.clicked.connect(self.add_setting)
        self.button_del_item.clicked.connect(self.tableView.delete_selected_rows)
        self.tableView.selectionModel().selectionChanged.connect(self.toggle_condition_del_button)

        self.dataTable.rowsRemoved.connect(self.changed.emit)
        self.dataTable.rowsInserted.connect(self.changed.emit)
        self.dataTable.dataChanged.connect(self.changed.emit)

    def set_item(self, model_test, model):
        """ Set the item to the current widget

        Parameters
        ----------
        model_test : GEMEditor.data_classes.ModelTest
        model : GEMEditor.model.classes.cobra.Model

        Returns
        -------
        None
        """
        self.model_test = model_test
        self.model = model

        self.dataTable.setRowCount(0)
        if self.model_test:
            self.dataTable.populate_table(model_test.gene_settings)

    @QtCore.pyqtSlot()
    def add_setting(self):
        dialog = GeneSelectionDialog(self.model)

        if dialog.exec_():
            for gene in dialog.selected_items():
                if gene not in set([self.dataTable.item(i).link for i in range(self.dataTable.rowCount())]):
                    self.dataTable.update_row_from_item(GeneSetting(gene=gene, activity=False))

    @QtCore.pyqtSlot()
    def add_current(self):
        known_genes = set([self.dataTable.item(i).link for i in range(self.dataTable.rowCount())])

        for gene in self.model.reactions:
            if gene not in known_genes and not gene.functional:
                self.dataTable.update_row_from_item(GeneSetting(gene=gene,
                                                                activity=gene.functional))

    @QtCore.pyqtSlot()
    def toggle_condition_del_button(self):
        status = len(self.tableView.get_selected_indexes()) > 0
        self.button_del_item.setEnabled(status)

    @property
    def content_changed(self):
        if self.model_test:
            return self.model_test.gene_settings != self.dataTable.get_items()
        else:
            return False

    def valid_input(self):
        return all(x.is_valid() for x in self.dataTable.get_items())

    def save_state(self):
        self.model_test.gene_settings = self.dataTable.get_items()


class OutcomeDisplayWidget(QWidget, Ui_SettingsDisplayWidget):

    changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(OutcomeDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        self.dataTable = OutcomesTable(self)
        self.tableView.setModel(self.dataTable)

        self.tableView.setItemDelegateForColumn(1, ComboBoxDelegate(parent=self.tableView,
                                                                    choices=["greater than", "less than"],
                                                                    select_option=False))
        self.tableView.setItemDelegateForColumn(2, FloatInputDelegate(parent=self.tableView, precision=2, default=0.01))

        # There are no standard outcomes
        self.button_add_current.setVisible(False)

        # Store model and current test
        self.model = None
        self.model_test = None

        # Setup icons for displaying failure/success of the individual outcomes
        scaling_settings = (QtCore.QSize(15, 15), QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
        self.ok_icon = QtGui.QIcon(QtGui.QPixmap(":/status_okay").scaled(*scaling_settings))
        self.error_icon = QtGui.QIcon(QtGui.QPixmap(":/status_error").scaled(*scaling_settings))

        # Setup the signals for widget interactions
        self.setup_signals()

    def setup_signals(self):
        self.button_add_item.clicked.connect(self.add_outcome)
        self.button_del_item.clicked.connect(self.tableView.delete_selected_rows)
        self.tableView.selectionModel().selectionChanged.connect(self.toggle_condition_del_button)

        self.dataTable.rowsRemoved.connect(self.changed.emit)
        self.dataTable.rowsInserted.connect(self.changed.emit)
        self.dataTable.dataChanged.connect(self.changed.emit)

    def set_item(self, model_test, model, solution=None):
        """ Set the item to the current widget

        Parameters
        ----------
        model_test : GEMEditor.data_classes.ModelTest
        model : GEMEditor.model.classes.cobra.Model
        solution : cobra.Solution.Solution

        Returns
        -------
        None
        """

        # Reset table
        self.dataTable.setRowCount(0)

        # Set the current test and model
        self.model_test = model_test
        self.model = model

        # Populate widget
        if self.model_test:
            self.dataTable.populate_table(model_test.outcomes)

            # Display the failure/success for individual outcomes
            if solution:
                fluxes = fluxes_from_solution(solution)
                for i, outcome in enumerate(model_test.outcomes):
                    new_item = QtGui.QStandardItem()
                    if outcome.check(fluxes):
                        new_item.setIcon(self.ok_icon)
                    else:
                        new_item.setIcon(self.error_icon)
                    self.dataTable.setVerticalHeaderItem(i, new_item)

    @QtCore.pyqtSlot()
    def add_outcome(self):
        dialog = ReactionSelectionDialog(self.model)

        if dialog.exec_():
            for reaction in dialog.selected_items():
                if reaction not in set([self.dataTable.item(i).link for i in range(self.dataTable.rowCount())]):
                    self.dataTable.update_row_from_item(Outcome(reaction))

    @QtCore.pyqtSlot()
    def toggle_condition_del_button(self):
        status = len(self.tableView.get_selected_indexes()) > 0
        self.button_del_item.setEnabled(status)

    @property
    def content_changed(self):
        return self.model_test.outcomes != self.dataTable.get_items()

    def valid_input(self):
        if self.dataTable.rowCount() == 0:
            return False
        else:
            return all(x.is_valid() for x in self.dataTable.get_items())

    def save_state(self):
        self.model_test.outcomes = self.dataTable.get_items()