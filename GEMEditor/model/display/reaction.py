from GEMEditor.base import reaction_balance
from GEMEditor.base.delegates import FloatInputDelegate
from GEMEditor.base.tables import LinkedItem
from GEMEditor.base.widgets import TableDisplayWidget
from GEMEditor.model.classes.cobra import iterate_tree, Reaction, Gene, GeneGroup
from GEMEditor.model.display.tables import StoichiometryTable
from GEMEditor.model.display.ui.GenesDisplayWidget import Ui_GenesDisplayWidget
from GEMEditor.model.display.ui.MetaboliteDisplayWidget import Ui_Form as Ui_MetDisplayWidget
from GEMEditor.model.display.ui.ReactionAttributeDisplayWidget import Ui_Form as Ui_ReactionAttribs
from GEMEditor.model.display.ui.StoichiometryDisplayWidget import Ui_StoichiometryDisplayWidget
from GEMEditor.model.selection import MetaboliteSelectionDialog, GeneSelectionDialog
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QRegularExpressionValidator
from PyQt5.QtWidgets import QWidget, QCompleter, QAction, QMenu


class ReactionAttributesDisplayWidget(QWidget, Ui_ReactionAttribs):

    changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(ReactionAttributesDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        self.model = None
        self.reaction = None
        self.default_id_border = self.idLineEdit.styleSheet()

        # Setup validator for SBML compliant ids
        self.validator = QRegularExpressionValidator()
        self.validator.setRegularExpression(QRegularExpression(r"^[a-zA-Z0-9_]*$"))
        self.idLineEdit.setValidator(self.validator)

        # Toggle id status
        self.validate_id()
        self.setup_connections()

    def setup_connections(self):
        # Connect validators
        self.idLineEdit.textChanged.connect(self.validate_id)

        # Connect inputs to changed
        self.idLineEdit.textChanged.connect(self.changed.emit)
        self.nameLineEdit.textChanged.connect(self.changed.emit)
        self.subsystemLineEdit.textChanged.connect(self.changed.emit)
        self.upperBoundInput.valueChanged.connect(self.changed.emit)
        self.lowerBoundInput.valueChanged.connect(self.changed.emit)
        self.objectiveCoefficientInput.valueChanged.connect(self.changed.emit)

        # Connect setting of the boundaries
        self.upperBoundInput.valueChanged.connect(self.set_range_lower_bound)
        self.lowerBoundInput.valueChanged.connect(self.set_range_upper_bound)

    def set_item(self, reaction, model):
        self.model = model
        self.reaction = reaction

        if reaction:
            # Set the range for the boundary inputs
            self.upperBoundInput.setRange(reaction.lower_bound, max(reaction.upper_bound, 1000.))
            self.lowerBoundInput.setRange(min(reaction.lower_bound, -1000.), reaction.upper_bound)

        self.populate_widgets()

    def save_state(self):
        """ Save the current content of the input widgets to the reaction

        This slot is triggered by the accepted() signal of the dialog.
        """

        if self.reaction.id != self.idLineEdit.text():
            self.reaction.id = self.idLineEdit.text()
            self.model.repair(rebuild_relationships=False)
        self.reaction.name = self.nameLineEdit.text()
        self.reaction.lower_bound = self.lowerBoundInput.value()
        self.reaction.upper_bound = self.upperBoundInput.value()
        self.reaction.subsystem = self.subsystemLineEdit.text()
        if self.reaction.model:
            self.reaction.objective_coefficient = self.objectiveCoefficientInput.value()

    @property
    def content_changed(self):
        """ Check if the content of the input widgets is different
        from the original information of the reaction """

        if self.reaction:
            return (self.idLineEdit.text() != self.reaction.id or
                    self.nameLineEdit.text() != self.reaction.name or
                    self.subsystemLineEdit.text() != self.reaction.subsystem or
                    self.upperBoundInput.value() != self.reaction.upper_bound or
                    self.lowerBoundInput.value() != self.reaction.lower_bound or
                    self.objectiveCoefficientInput.value() != self.reaction.objective_coefficient)
        else:
            return False

    def clear_information(self):
        """ Clear all information in the input widgets
        that are direct children of the dialog """

        self.idLineEdit.clear()
        self.nameLineEdit.clear()
        self.subsystemLineEdit.clear()
        self.upperBoundInput.clear()
        self.lowerBoundInput.clear()
        self.objectiveCoefficientInput.clear()

    def populate_widgets(self):
        """ Update the information displayed in the individual input elements """
        self.clear_information()

        if self.reaction is not None:
            self.idLineEdit.setText(self.reaction.id)
            self.idLineEdit.setCursorPosition(0)
            self.nameLineEdit.setText(self.reaction.name)
            self.nameLineEdit.setCursorPosition(0)
            self.subsystemLineEdit.setText(self.reaction.subsystem)
            self.subsystemLineEdit.setCursorPosition(0)
            self.upperBoundInput.setValue(self.reaction.upper_bound)
            self.lowerBoundInput.setValue(self.reaction.lower_bound)
            self.objectiveCoefficientInput.setValue(self.reaction.objective_coefficient)
            # Disable objective coefficient input if model not set
            self.objectiveCoefficientInput.setEnabled(self.reaction.model is not None)
            self.setWindowTitle(self.reaction.id)

            # Set the subsystem completer
            completer = QCompleter(list(self.model.subsystems.keys()), self)
            completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
            self.subsystemLineEdit.setCompleter(completer)

    @QtCore.pyqtSlot(str)
    def validate_id(self, new_id=None):
        if not new_id:
            self.idLineEdit.setStyleSheet("border: 1px solid red;")
            self.labelIdStatus.setToolTip("Empty Id!")
            self.labelIdStatus.setVisible(True)
        elif self.reaction and new_id != self.reaction.id and new_id in self.model.reactions:
            self.idLineEdit.setStyleSheet("border: 1px solid red;")
            self.labelIdStatus.setToolTip("Id exists already in model!")
            self.labelIdStatus.setVisible(True)
        else:
            self.idLineEdit.setStyleSheet(self.default_id_border)
            self.labelIdStatus.setVisible(False)

    def valid_inputs(self):
        """ Check that all input elements that are required to have a valid input
        actually do so """

        if self.reaction and self.idLineEdit.text():
            return (self.idLineEdit.text() not in self.model.reactions or
                    self.idLineEdit.text() == self.reaction.id)
        else:
            return False

    @QtCore.pyqtSlot()
    def set_range_upper_bound(self):
        """ Dynamically adjust the minimum range of the upperbound input
         to match the lower bound set

         This slot is triggered by the valueChanged-signal of the
         lower_bound input widget
         """
        self.upperBoundInput.setMinimum(self.lowerBoundInput.value())

    @QtCore.pyqtSlot()
    def set_range_lower_bound(self):
        """ Dynamically adjust the maxmimum range of the lowerbound input
        to match the upper bound set

        This slot is triggered by the valueChanged-signal of the
        upper_bound input widget
        """
        self.lowerBoundInput.setMaximum(self.upperBoundInput.value())


class StoichiometryDisplayWidget(TableDisplayWidget, Ui_StoichiometryDisplayWidget):

    dataType = "Metabolite"
    msg_boundary = "The reaction appears to be a boundary reaction and therefore not balanced!"
    msg_standard = "The reaction is {status}.<br>Charge: {charge}<br>Elements: {elements}"

    def __init__(self, parent=None):
        TableDisplayWidget.__init__(self, parent)
        self.setupUi(self)
        self.reaction = None
        self.model = None
        self.charge_str = None
        self.element_str = None
        self.balanced = None

        # Set the table for the metabolites associated with the reaction
        self.dataTable = StoichiometryTable(self)
        self.dataView.setModel(self.dataTable)
        self.dataView.setItemDelegateForColumn(1, FloatInputDelegate(parent=self.dataView))

        # Set dataTable connections
        self.changed.connect(self.check_balancing_status)
        self.setup_signals()

    def set_item(self, reaction, model):
        """ Set the reaction and model for the widget in order to
        """
        self.reaction = reaction
        self.model = model

        if reaction:
            self.dataTable.populate_table(self.reaction.metabolites.items())
            self.dataView.setModel(self.dataTable)
            self.check_balancing_status()

    @QtCore.pyqtSlot()
    def add_item(self):
        dialog = MetaboliteSelectionDialog(self.model)
        status = dialog.exec_()
        if status:
            for metabolite in dialog.selected_items():
                # Check that the metabolite is not already in the metabolite list
                if not self.dataTable.findItems(metabolite.id):
                    self.dataTable.update_row_from_item((metabolite, 0.))

    @QtCore.pyqtSlot()
    def edit_item(self):
        raise NotImplementedError

    @QtCore.pyqtSlot()
    def check_balancing_status(self):
        """ Check the reaction balancing status """

        stoichiometry = self.get_stoichiometry()

        self.charge_str, self.element_str, self.balanced = reaction_balance(stoichiometry)

        # Set status to undefined if reaction is a boundary reaction
        if self.balanced is None:
            self.statusLabel.setPixmap(QtGui.QPixmap(":/status_undefined"))
            self.statusLabel.setToolTip(self.msg_boundary)

        # Set status okay if sum charge is 0 and there are no unbalanced Elements
        elif self.balanced is True:
            self.statusLabel.setPixmap(QtGui.QPixmap(":/status_okay"))
            self.statusLabel.setToolTip(self.msg_standard.format(status="balanced",
                                                                 charge=self.charge_str,
                                                                 elements=self.element_str))

        # If charge or elements are unbalanced set the status to error
        elif self.balanced is False:
            self.statusLabel.setPixmap(QtGui.QPixmap(":/status_error"))
            self.statusLabel.setToolTip(self.msg_standard.format(status="unbalanced",
                                                                 charge=self.charge_str,
                                                                 elements=self.element_str))

        # Set status to unknown otherwise
        else:
            self.statusLabel.setPixmap(QtGui.QPixmap(":/status_unknown"))
            self.statusLabel.setToolTip(self.msg_standard.format(status="unknown",
                                                                 charge=self.charge_str,
                                                                 elements=self.element_str))

    def get_stoichiometry(self):
        """ Return the stoichiometry of the reaction as displayed in the metabolite
        table """
        return self.dataTable.get_items()

    @property
    def content_changed(self):
        return self.get_stoichiometry() != self.reaction.metabolites

    @QtCore.pyqtSlot()
    def save_state(self):
        """ Save the annotations from the table to the reaction """
        self.reaction.subtract_metabolites(self.reaction.metabolites, combine=True, reversibly=False)
        self.reaction.add_metabolites(self.dataTable.get_items())

        self.reaction.balanced = self.balanced
        self.reaction.elements_balanced = self.element_str
        self.reaction.charge_balanced = self.charge_str

    def valid_inputs(self):
        return all([coeff != 0. for coeff in self.get_stoichiometry().values()])


class GenesDisplayWidget(QWidget, Ui_GenesDisplayWidget):

    changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.reaction = None
        self.model = None

        # Set the tables for the genes associated with the reaction
        self.geneTable = QtGui.QStandardItemModel(self)
        self.geneView.setModel(self.geneTable)
        self.geneView.setHeaderHidden(True)

        # Menu actions
        self.add_gene_action = QAction(self.tr("Add Gene"), self)
        self.add_gene_action.triggered.connect(self.add_item)

        self.add_genegroup_action = QAction(self.tr("Add Group"), self)
        self.add_genegroup_action.triggered.connect(self.add_genegroup)

        self.switch_type_action = QAction(self.tr("Switch type"), self)
        self.switch_type_action.triggered.connect(self.change_group_type)

        self.delete_action = QAction(self.tr("Delete Gene"), self)
        self.delete_action.triggered.connect(self.delete_item)

        self.delete_genegroup_action = QAction(self.tr("Delete Group"), self)
        self.delete_genegroup_action.triggered.connect(self.delete_item)

        self.cached_actions = []

    @QtCore.pyqtSlot()
    def add_item(self):
        dialog = GeneSelectionDialog(self.model)

        if dialog.exec_():
            for gene in dialog.selected_items():
                self.add_gene(gene)

    def set_item(self, reaction, model):
        """ Set the reaction for the gene widget """
        self.reaction = reaction
        self.model = model
        self.update_information()

    def update_information(self):
        """ Update the information displayed """
        self.clear_information()
        if self.reaction:
            self.populate_gene_tree()

    def populate_gene_tree(self):
        """ Populate the gene tree with the genes currently assigned to
        the reaction """
        if self.reaction._children:
            root = self.geneTable.invisibleRootItem()
            iterate_tree(root, self.reaction)

    def clear_information(self):
        """ Clear gene information """
        self.geneTable.setRowCount(0)
        del self.cached_actions[:]

    def get_selected_item(self):
        index = self.geneView.currentIndex()
        table_item = self.geneTable.itemFromIndex(index)

        if table_item is None:
            table_item = self.geneTable
            model_item = self.reaction
        else:
            model_item = table_item.link

        return table_item, model_item

    @QtCore.pyqtSlot(QtCore.QPoint)
    def show_gene_contextmenu(self, pos):
        menu = QMenu()
        _, model_item = self.get_selected_item()

        if isinstance(model_item, Reaction):
            menu.addAction(self.add_gene_action)
            menu.addAction(self.add_genegroup_action)

        elif isinstance(model_item, Gene):
            menu.addAction(self.delete_action)

        elif isinstance(model_item, GeneGroup):
            menu.addAction(self.add_gene_action)
            menu.addAction(self.add_genegroup_action)
            menu.addAction(self.switch_type_action)
            menu.addSeparator()
            menu.addAction(self.delete_genegroup_action)

        menu.exec_(self.geneView.viewport().mapToGlobal(pos))
        return menu

    def add_gene(self, gene):
        """ Buffer the addition of a gene to the genegroup and change the model"""
        table_item, model_item = self.get_selected_item()

        new_item = LinkedItem(text=gene.id,
                              link=gene)
        table_item.appendRow(new_item)
        self.cached_actions.append((model_item, "addition", gene))
        self.changed.emit()

    @QtCore.pyqtSlot()
    def add_genegroup(self):
        """ Buffer the addition of a genegroup to the genegroup and change the model"""
        # Get current item
        table_item, model_item = self.get_selected_item()

        new_group = GeneGroup()
        new_item = LinkedItem(text=str(new_group.type).upper(),
                              link=new_group)

        table_item.appendRow(new_item)

        # Buffer the function call for when user accepts dialog
        self.cached_actions.append((model_item, "addition", new_group))
        self.changed.emit()

    @QtCore.pyqtSlot()
    def delete_item(self):
        # Get current item
        table_item, model_item = self.get_selected_item()
        row = table_item.row()

        # Check if parent item is invisible root item
        parent = table_item.parent()
        if parent is None:
            target = self.reaction
            self.geneTable.removeRow(row)
        else:
            target = parent.link
            self.geneTable.removeRow(row, parent=parent.index())

        # Buffer the function call for when user accepts dialog
        self.cached_actions.append((target, "deletion", model_item))
        self.changed.emit()

    @QtCore.pyqtSlot()
    def change_group_type(self):
        """ Change the type of the genegroup"""
        # Get current item
        table_item, model_item = self.get_selected_item()

        self.cached_actions.append((model_item, "switch type", None))

        # Switch group type on table item
        table_item.setText("AND" if table_item.text() == "OR" else "OR")

        self.changed.emit()

    def execute_cache(self):
        for element in self.cached_actions:
            self.execute_action(element)
        self.clear_information()

    @staticmethod
    def execute_action(gene_action):
        target, function, input_object = gene_action

        if function == "addition":
            target.add_child(input_object)
        elif function == "deletion":
            if isinstance(input_object, GeneGroup) and len(input_object._parents) == 1:
                input_object.delete_children()
            target.remove_child(input_object)
        elif function == "switch type":
            if target.type == "and":
                target.type = "or"
            elif target.type == "or":
                target.type = "and"

    @property
    def content_changed(self):
        return self.cached_actions != []

    @QtCore.pyqtSlot()
    def save_state(self):
        self.execute_cache()


class MetaboliteDisplayWidget(QWidget, Ui_MetDisplayWidget):

    def __init__(self, parent=None, metabolite=None):
        super(MetaboliteDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        self.metabolite = None
        self.set_metabolite(metabolite)

    def set_metabolite(self, metabolite):
        self.metabolite = metabolite
        self.update_display()

    def update_display(self):
        """ Update labels with information from model item

        Returns
        -------
        None
        """

        # Clear all information
        self.clear_all()

        # Update labels
        if self.metabolite:
            self.label_id.setText(str(self.metabolite.id))
            self.label_names.setText(str(self.metabolite.name))
            self.label_formula.setText(str(self.metabolite.formula))
            self.label_charge.setText(str(self.metabolite.charge))
            self.label_compartment.setText(str(self.metabolite.compartment))

    def clear_all(self):
        """ Clear information from widget

        Returns
        -------
        None
        """
        self.label_id.clear()
        self.label_names.clear()
        self.label_formula.clear()
        self.label_charge.clear()
        self.label_compartment.clear()