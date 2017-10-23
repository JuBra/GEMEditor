import string
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QWidget, QAction, QMenu, QApplication, QCompleter
from PyQt5.QtGui import QRegularExpressionValidator
from PyQt5.QtCore import QRegularExpression
from GEMEditor.ui.modelDisplayWidget import Ui_modelDisaplayWidget
from GEMEditor.ui.StoichiometryDisplayWidget import Ui_StoichiometryDisplayWidget
from GEMEditor.ui.GenesDisplayWidget import Ui_GenesDisplayWidget
from GEMEditor.ui.ModelAnnotationDisplayWidget import Ui_AnnotationDisplayWidget
from GEMEditor.widgets.tables import AnnotationTable, LinkedItem, StoichiometryTable, EvidenceTable, ReactionSettingsTable, GeneSettingsTable, OutcomesTable, LinkedReferenceTable
from GEMEditor.dialogs.standard import MetaboliteSelectionDialog, GeneSelectionDialog, ReactionSelectionDialog, ReferenceSelectionDialog
from GEMEditor.widgets.delegates import FloatInputDelegate, ComboBoxDelegate
from GEMEditor.cobraClasses import Gene, GeneGroup, iterate_tree, Reaction
from GEMEditor.base.functions import reaction_balance
from GEMEditor.evidence_class import Evidence
from GEMEditor.data_classes import Outcome, ReactionSetting, GeneSetting
from GEMEditor.ui.TableDisplayWidgetAddDel import Ui_TableDisplayWidgetAddDel
from GEMEditor.ui.CommentDisplayWidget import Ui_CommentDisplayWidget
from GEMEditor.ui.MetaboliteAttributeDisplayWidget import Ui_MetaboliteAttributeDisplayWidget as Ui_MetAttribs
from GEMEditor.ui.ReactionsDisplayWidget import Ui_ReactionsDisplayWidget
from GEMEditor.ui.GeneAttributesDisplayWidget import Ui_Form as Ui_GeneAttribs
from GEMEditor.ui.ReactionAttributeDisplayWidget import Ui_Form as Ui_ReactionAttribs
from GEMEditor import use_progress
from GEMEditor.dialogs.annotation import EditAnnotationDialog
from GEMEditor.dialogs.evidence import EditEvidenceDialog
from GEMEditor.widgets.baseWidgets import TableDisplayWidget
from GEMEditor.ui.SettingDisplayWiget import Ui_SettingsDisplayWidget
from GEMEditor.ui.MetaboliteDisplayWidget import Ui_Form as Ui_MetDisplayWidget
from GEMEditor.widgets.ui.SolutionTableWidget import Ui_SolutionTableWidget


class ModelDisplayWidget(QWidget, Ui_modelDisaplayWidget):

    model_changed = QtCore.pyqtSignal()

    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.model = None
        self.compartment_table = QtGui.QStandardItemModel(self)
        self.tableView.setModel(self.compartment_table)
        self.compartment_table.setHorizontalHeaderLabels(["ID", "Name"])
        self.tableView.setFixedHeight(125)
        self.tableView.setFixedWidth(200)

    def set_model(self, model, path=None):
        """  Set a new model to be displayed """

        self.model = model
        # Clear existing model data
        self.clear_information()
        self.label_model_path.setText(path)
        self.update_information()
        self.model_changed.emit()

    def set_path(self, path):
        self.label_model_path.setText(path)

    def clear_information(self):
        self.label_model_id.clear()
        self.label_model_name.clear()
        self.label_number_metabolites.clear()
        self.label_number_reactions.clear()
        self.label_number_genes.clear()
        self.compartment_table.setRowCount(0)

    @QtCore.pyqtSlot()
    def update_information(self):
        if self.model is not None:
            self.label_model_id.setText(self.model.id)
            self.label_model_name.setText(self.model.name)
            self.label_number_metabolites.setText(str(len(self.model.metabolites)))
            self.label_number_reactions.setText(str(len(self.model.reactions)))
            self.label_number_genes.setText(str(len(self.model.genes)))

            self.compartment_table.setRowCount(0)
            for key, compartment in self.model.gem_compartments.items():
                self.compartment_table.appendRow([QtGui.QStandardItem(key), QtGui.QStandardItem(compartment.name)])


class ModelAnnotationDisplayWidget(QWidget, Ui_AnnotationDisplayWidget):

    def __init__(self, parent):
        super(ModelAnnotationDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        self.model = None

    def set_model(self, model):
        self.model = model
        self.update_information()

    @QtCore.pyqtSlot()
    def update_information(self):

        # Add new stats
        if self.model is not None:
            self.label_num_evidences.setText(str(len(self.model.all_evidences)))
            self.label_num_references.setText(str(len(self.model.references)))
            self.label_num_tests.setText(str(len(self.model.tests)))
        else:
            self.label_num_tests.clear()
            self.label_num_references.clear()
            self.label_num_evidences.clear()


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


class AnnotationDisplayWidget(TableDisplayWidget, Ui_TableDisplayWidgetAddDel):

    dataType = "Annotation"

    def __init__(self, parent=None):
        TableDisplayWidget.__init__(self, parent)
        self.dataTable = AnnotationTable(self)
        self.setupUi(self)

        self.model = None
        self.display_item = None

        self.dataView.setModel(self.dataTable)
        self.setup_signals()

    @QtCore.pyqtSlot()
    def add_item(self):
        dialog = EditAnnotationDialog(self, None, self.display_item)
        if dialog.exec_():
            new_annotation = dialog.get_annotation()
            if new_annotation not in self.get_annotation():
                self.dataTable.update_row_from_item(dialog.get_annotation())

    @QtCore.pyqtSlot()
    def edit_item(self):
        row = self.dataView.get_selected_rows(get_first_only=True)[0]
        annotation = self.dataTable.item_from_row(row)
        dialog = EditAnnotationDialog(self, annotation, self.display_item)
        if dialog.exec_():
            self.dataTable.update_row_from_item(dialog.get_annotation(), row)

    def set_item(self, item, model):
        self.model = model
        self.display_item = item
        if item:
            self.dataTable.populate_table(item.annotation)

    def get_annotation(self):
        """ Get the current annotation from the table """
        return self.dataTable.get_items()

    @QtCore.pyqtSlot(QtCore.QPoint)
    def showContextMenu(self, pos):
        menu = QMenu()

        if self.dataView.get_selected_rows():
            open_browser_action = QAction(self.tr("Open in browser"), menu)
            open_browser_action.triggered.connect(self.open_browser)
            menu.addAction(open_browser_action)
            menu.addSeparator()
        self.add_standard_menu_actions(menu)

        menu.exec_(self.dataView.viewport().mapToGlobal(pos))

    def open_browser(self):
        selected_rows = self.dataView.get_selected_rows()
        for row in selected_rows:
            item = self.dataTable.item(row).link
            QtGui.QDesktopServices.openUrl(QtCore.QUrl("http://identifiers.org/{0}/{1}".format(item.collection, item.identifier)))

    @property
    def content_changed(self):
        return self.display_item.annotation != set(self.get_annotation())

    @QtCore.pyqtSlot()
    def save_state(self):
        """ Save the annotations from the table to the reaction """
        self.display_item.annotation.clear()
        self.display_item.annotation.update(self.dataTable.get_items())


class EvidenceDisplayWidget(TableDisplayWidget, Ui_TableDisplayWidgetAddDel):

    # DataType is used to display the correct names in the context menu
    dataType = "Evidence"

    def __init__(self, parent=None):
        TableDisplayWidget.__init__(self, parent)
        self.dataTable = EvidenceTable(self)
        self.setupUi(self)

        self.model = None
        self.item = None

        self.dataView.setModel(self.dataTable)

        self.setup_signals()

    def set_item(self, item, model):
        self.item = item
        self.model = model
        # Populate the datatable with one-way linked copies i.e. the evidence only points
        # to the items, reference etc. but not vice versa
        if item:
            self.dataTable.populate_table([x.copy() for x in item.evidences])

    @QtCore.pyqtSlot()
    def add_item(self):
        new_evidence = Evidence()
        # Set base_item externally in order to avoid linkage from base_item to
        # evidence
        new_evidence.entity = self.item
        dialog = EditEvidenceDialog(self.window(), self.model, evidence=new_evidence)
        if dialog.exec_():
            self.dataTable.update_row_from_item(new_evidence)

    @QtCore.pyqtSlot()
    def edit_item(self):
        row = self.dataView.get_selected_rows(get_first_only=True)[0]
        evidence = self.dataTable.item_from_row(row)
        dialog = EditEvidenceDialog(self.window(), self.model, evidence=evidence)
        if dialog.exec_():
            self.dataTable.update_row_from_link(row)

    @property
    def content_changed(self):
        if not self.item:
            return False
        else:
            dict1 = dict((x.internal_id, x) for x in self.item.evidences)
            dict2 = dict((x.internal_id, x) for x in self.dataTable.get_items())
            if dict1.keys() != dict2.keys():
                return True

            for x in dict1:
                if dict1[x] != dict2[x]:
                    return True
            return False

    @QtCore.pyqtSlot()
    def save_state(self):
        """ Save the annotations from the table to the reaction """

        # Remove all existing evidences
        for evidence in list(self.item.evidences):
            evidence.delete_links()

        # Setup modified evidences
        for evidence in self.dataTable.get_items():
            evidence.setup_links()
            self.model.all_evidences[evidence.internal_id] = evidence


class CommentDisplayWidget(QWidget, Ui_CommentDisplayWidget):

    changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.commentInput.textChanged.connect(self.changed.emit)
        self.display_item = None

    def set_item(self, item, *args, **kwargs):
        self.display_item = item
        self.commentInput.clear()
        if item:
            self.commentInput.setText(item.comment)

    @property
    def content_changed(self):
        if self.display_item is None:
            return False
        return self.commentInput.toPlainText() != self.display_item.comment

    @QtCore.pyqtSlot()
    def save_state(self):
        self.display_item.comment = self.commentInput.toPlainText()


class MetaboliteAttributesDisplayWidget(QWidget, Ui_MetAttribs):

    changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(MetaboliteAttributesDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        self.model = None
        self.metabolite = None
        self.default_id_border = self.iDLineEdit.styleSheet()

        # Setup validator for SBML compliant ids
        self.validator = QRegularExpressionValidator()
        self.validator.setRegularExpression(QRegularExpression(r"^[a-zA-Z0-9_]*$"))
        self.iDLineEdit.setValidator(self.validator)

        # Toggle the warning signs
        self.validate_id()
        self.validate_compartment()
        self.validate_formula()

        self.setup_connections()

    def setup_connections(self):
        # Connect validators
        self.iDLineEdit.textChanged.connect(self.validate_id)
        self.formulaLineEdit.textChanged.connect(self.validate_formula)
        self.compartmentComboBox.currentTextChanged.connect(self.validate_compartment)

        # Connect inputs to changed
        self.iDLineEdit.textChanged.connect(self.changed.emit)
        self.nameLineEdit.textChanged.connect(self.changed.emit)
        self.formulaLineEdit.textChanged.connect(self.changed.emit)
        self.chargeSpinBox.valueChanged.connect(self.changed.emit)
        self.compartmentComboBox.currentIndexChanged.connect(self.changed.emit)

    def set_item(self, item, model):
        self.model = model
        self.metabolite = item
        self.populate_widgets()

    @use_progress
    def save_state(self, progress):
        """ Save the current state of the inputs to the metabolite that is currently
        edited"""
        update_reactions = False
        update_balance = False
        self.metabolite.name = self.nameLineEdit.text()
        self.metabolite.compartment = self.compartmentComboBox.currentText()

        if self.metabolite.id != self.iDLineEdit.text():
            self.metabolite.id = self.iDLineEdit.text()
            self.model.repair(rebuild_relationships=False)
            update_reactions = True

        if self.metabolite.charge != self.chargeSpinBox.value():
            self.metabolite.charge = self.chargeSpinBox.value()
            update_reactions = True
            update_balance = True

        if self.metabolite.formula != self.formulaLineEdit.text():
            self.metabolite.formula = self.formulaLineEdit.text()
            update_reactions = True
            update_balance = True

        if update_reactions is True:
            progress.setRange(0, len(self.metabolite.reactions))
            progress.setLabelText("Saving metabolite..")

            # Update reaction rows that contain this metabolite
            self.model.QtReactionTable.blockSignals(True)
            for i, reaction in enumerate(self.metabolite.reactions):
                progress.setValue(i)
                QApplication.processEvents()
                if update_balance:
                    reaction.update_balancing_status()
                self.model.QtReactionTable.update_row_from_id(reaction.id)
            self.model.QtReactionTable.blockSignals(False)
            self.model.QtReactionTable.all_data_changed()

    @property
    def content_changed(self):
        """ Check if there has been a change in the metabolite inputs """

        if self.metabolite:
            return (self.iDLineEdit.text() != self.metabolite.id or
                    self.nameLineEdit.text() != self.metabolite.name or
                    self.formulaLineEdit.text() != self.metabolite.formula or
                    self.chargeSpinBox.value() != self.metabolite.charge or
                    self.compartmentComboBox.currentText() != self.metabolite.compartment)
        else:
            return False

    def clear_information(self):
        """ Clear all information present in the input widgets """
        self.iDLineEdit.clear()
        self.nameLineEdit.clear()
        self.formulaLineEdit.clear()
        self.chargeSpinBox.clear()
        self.chargeSpinBox.setValue(0)
        self.compartmentComboBox.clear()

    def populate_widgets(self):
        """ Update the information displayed in the individual input elements """
        self.clear_information()

        if self.metabolite is not None:

            # Populate the compartment combobox
            self.compartmentComboBox.addItems(sorted(self.model.gem_compartments.keys()))

            self.iDLineEdit.setText(self.metabolite.id)
            self.iDLineEdit.setCursorPosition(0)
            self.nameLineEdit.setText(self.metabolite.name)
            self.nameLineEdit.setCursorPosition(0)
            self.formulaLineEdit.setText(self.metabolite.formula)
            self.formulaLineEdit.setCursorPosition(0)
            self.chargeSpinBox.setValue(self.metabolite.charge or 0)

            # Add the compartment in case it is not in the model compartment
            # dictionary. Only if compartment is set.
            current_index = self.compartmentComboBox.findText(self.metabolite.compartment)
            if current_index == -1 and self.metabolite.compartment:
                self.compartmentComboBox.addItem(self.metabolite.compartment)
                self.compartmentComboBox.setCurrentIndex(self.compartmentComboBox.count()-1)
            else:
                self.compartmentComboBox.setCurrentIndex(current_index)

    @QtCore.pyqtSlot(str)
    def validate_id(self, new_id=None):
        if not new_id:
            self.iDLineEdit.setStyleSheet("border: 1px solid red;")
            self.labelIdStatus.setToolTip("Empty Id!")
            self.labelIdStatus.setVisible(True)
        elif self.metabolite and new_id != self.metabolite.id and new_id in self.model.metabolites:
            self.iDLineEdit.setStyleSheet("border: 1px solid red;")
            self.labelIdStatus.setToolTip("Id exists already in model!")
            self.labelIdStatus.setVisible(True)
        else:
            self.iDLineEdit.setStyleSheet(self.default_id_border)
            self.labelIdStatus.setVisible(False)

    @QtCore.pyqtSlot(str)
    def validate_formula(self, new_formula=None):
        if not new_formula:
            return

        chars = string.digits+string.ascii_letters
        invalid_chars = set([x for x in new_formula if x not in chars])
        if invalid_chars:
            self.labelFormulaStatus.setVisible(True)
            quoted = ['"{}"'.format(x) for x in invalid_chars]
            self.labelFormulaStatus.setToolTip('Invalid characters: {}'.format(", ".join(quoted)))
            self.formulaLineEdit.setStyleSheet("border: 1px solid red;")
        else:
            self.labelFormulaStatus.setVisible(False)
            self.formulaLineEdit.setStyleSheet(self.default_id_border)

    @QtCore.pyqtSlot(str)
    def validate_compartment(self, new_compartment=None):
        if not new_compartment:
            self.labelCompartmentStatus.setVisible(True)
            self.labelCompartmentStatus.setToolTip("Select compartment!")
        else:
            self.labelCompartmentStatus.setVisible(False)

    def valid_inputs(self):
        """ Check that all input elements that are required to have a valid input
        actually do so """

        if self.metabolite and self.iDLineEdit.text():
            return ((self.iDLineEdit.text() not in self.model.metabolites or
                     self.iDLineEdit.text() == self.metabolite.id) and
                    self.compartmentComboBox.currentText() != "")
        else:
            return False


class ReactionsDisplayWidget(QWidget, Ui_ReactionsDisplayWidget):

    changed = QtCore.pyqtSignal()

    def __init__(self):
        super(ReactionsDisplayWidget, self).__init__()
        self.setupUi(self)
        self.model = None
        self.item = None
        self.reactionTable = QtGui.QStandardItemModel(self)
        self.tableViewReactions.setModel(self.reactionTable)
        self.reactionTable.setHorizontalHeaderLabels(["ID", "Subsystem", "Formula"])

    def set_item(self, item, model):
        self.model = model
        self.item = item

        if item:
            self.reactionTable.setRowCount(0)
            for reaction in item.reactions:
                self.reactionTable.appendRow([QtGui.QStandardItem(reaction.id),
                                              QtGui.QStandardItem(reaction.subsystem),
                                              QtGui.QStandardItem(reaction.reaction)])

    def save_state(self):
        # Read only widget
        pass

    @property
    def content_changed(self):
        # Read only
        return False


class GeneAttributesDisplayWidget(QWidget, Ui_GeneAttribs):

    changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(GeneAttributesDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        self.model = None
        self.gene = None
        self.default_id_border = self.iDLineEdit.styleSheet()

        # Hide status icons before initialization
        self.labelIdStatus.setVisible(False)

        # Setup validator for SBML compliant ids
        self.validator = QRegularExpressionValidator()
        self.validator.setRegularExpression(QRegularExpression(r"^[a-zA-Z0-9_]*$"))
        self.iDLineEdit.setValidator(self.validator)

        self.validate_id()

        self.setup_connections()

    def setup_connections(self):
        # Connect validators
        self.iDLineEdit.textChanged.connect(self.validate_id)

        # Connect inputs to changed
        self.iDLineEdit.textChanged.connect(self.changed.emit)
        self.nameLineEdit.textChanged.connect(self.changed.emit)
        self.genomeLineEdit.textChanged.connect(self.changed.emit)

    def set_item(self, item, model):
        self.model = model
        self.gene = item
        self.populate_widgets()

    def save_state(self):
        """ Save the current state of the inputs to the gene that is currently
        edited"""

        self.gene.name = self.nameLineEdit.text()
        self.gene.genome = self.genomeLineEdit.text()

        if self.gene.id != self.iDLineEdit.text():
            self.gene.id = self.iDLineEdit.text()
            self.model.repair(rebuild_relationships=False)

    @property
    def content_changed(self):
        """ Check if there has been a change in the gene inputs """

        if self.gene:
            return (self.iDLineEdit.text() != self.gene.id or
                    self.nameLineEdit.text() != self.gene.name or
                    self.genomeLineEdit.text() != self.gene.genome)
        else:
            return False

    def clear_information(self):
        """ Clear all information present in the input widgets """
        self.iDLineEdit.clear()
        self.nameLineEdit.clear()
        self.genomeLineEdit.clear()

    def populate_widgets(self):
        """ Update the information displayed in the individual input elements """
        self.clear_information()

        if self.gene is not None:
            self.iDLineEdit.setText(self.gene.id)
            self.iDLineEdit.setCursorPosition(0)
            self.nameLineEdit.setText(self.gene.name)
            self.nameLineEdit.setCursorPosition(0)
            self.genomeLineEdit.setText(self.gene.genome)
            self.genomeLineEdit.setCursorPosition(0)

    @QtCore.pyqtSlot(str)
    def validate_id(self, new_id=None):
        if not new_id:
            self.iDLineEdit.setStyleSheet("border: 1px solid red;")
            self.labelIdStatus.setToolTip("Empty Id!")
            self.labelIdStatus.setVisible(True)
        elif self.gene and new_id != self.gene.id and new_id in self.model.genes:
            self.iDLineEdit.setStyleSheet("border: 1px solid red;")
            self.labelIdStatus.setToolTip("Id exists already in model!")
            self.labelIdStatus.setVisible(True)
        else:
            self.iDLineEdit.setStyleSheet(self.default_id_border)
            self.labelIdStatus.setVisible(False)

    def valid_inputs(self):
        """ Check that all input elements that are required to have a valid input
        actually do so """

        if self.gene and self.iDLineEdit.text():
            return (self.iDLineEdit.text() not in self.model.genes or
                    self.iDLineEdit.text() == self.gene.id)
        else:
            return False


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
        model : GEMEditor.cobraClasses.Model

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
                                                                    choices=["active", "inactive"]))

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
        model : GEMEditor.cobraClasses.Model

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
                    self.dataTable.update_row_from_item(GeneSetting(gene=gene,
                                                                    activity=gene.functional))

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


class ReferenceDisplayWidget(QWidget, Ui_SettingsDisplayWidget):

    changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(ReferenceDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        self.dataTable = LinkedReferenceTable(self)
        self.tableView.setModel(self.dataTable)

        self.button_add_current.setVisible(False)

        self.model = None
        self.item = None

        self.setup_signals()

    def setup_signals(self):
        self.button_add_item.clicked.connect(self.add_reference)
        self.button_del_item.clicked.connect(self.tableView.delete_selected_rows)
        self.tableView.selectionModel().selectionChanged.connect(self.toggle_condition_del_button)

        self.dataTable.rowsRemoved.connect(self.changed.emit)
        self.dataTable.rowsInserted.connect(self.changed.emit)
        self.dataTable.dataChanged.connect(self.changed.emit)

    def set_item(self, item, model, *args):
        """ Set the item to the current widget

        Parameters
        ----------
        item : GEMEditor.data_classes.ModelTest
        model : GEMEditor.cobraClasses.Model

        Returns
        -------
        None
        """
        self.item = item
        self.model = model

        self.dataTable.setRowCount(0)
        if self.item:
            self.dataTable.populate_table(item.references)

    @QtCore.pyqtSlot()
    def add_reference(self):
        dialog = ReferenceSelectionDialog(self.model)

        if dialog.exec_():
            for reference in dialog.selected_items():
                if reference not in set([self.dataTable.item(i).link for i in range(self.dataTable.rowCount())]):
                    self.dataTable.update_row_from_item(reference)

    @QtCore.pyqtSlot()
    def toggle_condition_del_button(self):
        status = len(self.tableView.get_selected_indexes()) > 0
        self.button_del_item.setEnabled(status)

    @property
    def content_changed(self):
        if self.item:
            return self.item.references != self.dataTable.get_items()

        return False

    def valid_input(self):
        return True

    def save_state(self):
        # Delete old references
        for x in list(self.item.references):
            self.item.remove_reference(x)

        # Set new references
        for x in self.dataTable.get_items():
            self.item.add_reference(x)


class OutcomeDisplayWidget(QWidget, Ui_SettingsDisplayWidget):

    changed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(OutcomeDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        self.dataTable = OutcomesTable(self)
        self.tableView.setModel(self.dataTable)

        self.tableView.setItemDelegateForColumn(1, ComboBoxDelegate(parent=self.tableView, choices=["greater than", "less than"]))
        self.tableView.setItemDelegateForColumn(2, FloatInputDelegate(parent=self.tableView, precision=2))

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

    def set_item(self, model_test, model, solution):
        """ Set the item to the current widget

        Parameters
        ----------
        model_test : GEMEditor.data_classes.ModelTest
        model : GEMEditor.cobraClasses.Model
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
                for i, outcome in enumerate(model_test.outcomes):
                    new_item = QtGui.QStandardItem()
                    if outcome.check_solution(solution):
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


class SolutionDisplayWidget(QWidget, Ui_SolutionTableWidget):

    def __init__(self, parent=None):
        super(SolutionDisplayWidget, self).__init__(parent)
        self.setupUi(self)
        self.solution = None

        self.button_open_map.clicked.connect(self.open_map)
        self.button_open_solution.clicked.connect(self.open_solution)

    def set_solution(self, solution):
        self.solution = solution
        self.label_status.setText(str(solution.status))
        self.label_objective.setText(str(solution.objective))

    @QtCore.pyqtSlot()
    def open_solution(self):
        pass

    @QtCore.pyqtSlot()
    def open_map(self):
        pass