from GEMEditor.base.dialogs import CustomStandardDialog
from GEMEditor.model.selection import MetaboliteSelectionDialog, ReactionSelectionDialog, GeneSelectionDialog, \
    CompartmentSelectionDialog
from GEMEditor.evidence.eco_parser import all_ecos, EvidenceCode
from GEMEditor.model.classes.cobra import Reaction, Metabolite, Gene, LinkedItem
from GEMEditor.model.classes.evidence import Evidence
from GEMEditor.model.edit.ui.BatchEvidenceDialog import Ui_BatchEvidenceDialog
from GEMEditor.model.edit.ui.EcoSelectionDialog import Ui_EcoSelectionDialog as Ui_eco
from GEMEditor.model.edit.ui.EditEvidenceDialog import Ui_EditEvidenceDialog as Ui_new
from GEMEditor.widgets.proxymodels import RecursiveProxyFilter
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMenu, QAction, QDialogButtonBox, QMessageBox, QErrorMessage, QInputDialog


class EditEvidenceDialog(CustomStandardDialog, Ui_new):

    options = {Metabolite: ("Present",),
               Reaction: ("Present", "Absent", "Reversible", "Irreversible", "Active", "Passive"),
               Gene: ("Localization", "Catalyzing reaction", "Not catalyzing reaction"),
               None.__class__: ()}

    def __init__(self, parent, model=None, evidence=None, **kwargs):
        super(EditEvidenceDialog, self).__init__(parent, **kwargs)
        self.setupUi(self)
        self.evidence = None
        self.linked_item = None
        self.target_item = None
        self.eco = ""
        self.set_evidence(evidence)
        self.referenceWidget.set_item(evidence, model)
        self.model = model
        self.referenceWidget.model = model

        self.setup_connections()
        self.set_toolbutton_menu()
        self.set_toolbutton_target_menu()

        self.restore_dialog_geometry()

    # noinspection PyUnresolvedReferences
    def setup_connections(self):
        self.pushButton_select_eco.clicked.connect(self.select_eco)
        self.comboBox.currentIndexChanged.connect(self.stackedWidget.setCurrentIndex)
        self.accepted.connect(self.save_state)

    def set_toolbutton_menu(self):
        menu = QMenu()
        action1 = QAction("Metabolite", menu)
        action1.triggered.connect(lambda x: self.select_link(MetaboliteSelectionDialog))
        action2 = QAction("Reaction", menu)
        action2.triggered.connect(lambda x: self.select_link(ReactionSelectionDialog))
        action3 = QAction("Gene", menu)
        action3.triggered.connect(lambda x: self.select_link(GeneSelectionDialog))
        menu.addAction(action1)
        menu.addAction(action2)
        menu.addAction(action3)
        self.toolButton_select.setMenu(menu)

    def set_toolbutton_target_menu(self):
        menu = QMenu()
        action1 = QAction("Metabolite", menu)
        action1.triggered.connect(lambda x: self.select_target(MetaboliteSelectionDialog))
        action2 = QAction("Reaction", menu)
        action2.triggered.connect(lambda x: self.select_target(ReactionSelectionDialog))
        action3 = QAction("Gene", menu)
        action3.triggered.connect(lambda x: self.select_target(GeneSelectionDialog))
        menu.addActions([action1, action2, action3])
        if self.evidence and isinstance(self.evidence.entity, Gene):
            action4 = QAction("Compartment", menu)
            action4.triggered.connect(lambda x: self.select_target(CompartmentSelectionDialog))
            menu.addAction(action4)
        self.toolButton_select_targe.setMenu(menu)

    def select_link(self, dialog_class):
        dialog = dialog_class(self.model)
        if dialog.exec_():
            self.set_linked_item(dialog.selected_items()[0])

    def select_target(self, dialog_class):
        dialog = dialog_class(self.model)
        if dialog.exec_():
            self.set_target_item(dialog.selected_items()[0])

    def select_compartment(self):
        compartment_id, status = QInputDialog().getItem(self, "Select compartment", "Select compartment:",
                                                              sorted(self.model.gem_compartments.keys()), 0, False)
        if status:
            self.set_target_item(self.model.gem_compartments[compartment_id])

    def set_evidence(self, evidence):
        if evidence is None:
            return
        elif not isinstance(evidence, Evidence):
            QErrorMessage().showMessage("The instance passed to .set_evidence is not of type Evidence")
            return

        self.evidence = evidence
        self.populate_propertybox()
        self.set_assertion(evidence.assertion)
        self.set_linked_item(evidence.link)
        self.set_target_item(evidence.target)
        try:
            self.set_eco(all_ecos[evidence.eco])
        except KeyError:
            self.set_eco(None)
        self.textBox_comment.setPlainText(evidence.comment)
        self.lineEdit_term.setText(evidence.term)
        self.referenceWidget.dataTable.populate_table(evidence.references)

    def set_linked_item(self, item):
        if item:
            self.linked_item = item
            self.label_link.setText(item.id)
            self.comboBox.setCurrentIndex(1)
            self.stackedWidget.setCurrentIndex(1)
        else:
            self.linked_item = None
            self.label_link.clear()

    def set_target_item(self, item):
        if item:
            self.target_item = item
            self.label_target.setText(item.id)
        else:
            self.target_item = None
            self.label_target.clear()

    def set_assertion(self, assertion):
        self.comboBox_assertion.setCurrentIndex(self.comboBox_assertion.findText(assertion))

    def populate_propertybox(self):
        """ Populate the combobox with the appropriate options"""
        self.comboBox_assertion.clear()
        try:
            self.comboBox_assertion.addItems(self.options[self.evidence.entity.__class__])
        except KeyError:
            QErrorMessage().showMessage("Unexpected base item of type {}.".format(str(type(self.evidence.entity))))
            return

    @QtCore.pyqtSlot()
    def save_state(self):
        """ Save the state of the evidence when the user accepts the dialog

        Returns
        -------
        None
        """

        # Add new data to evidence
        self.evidence.set_assertion(self.comboBox_assertion.currentText())
        if self.eco:
            self.evidence.set_eco(self.eco)
        self.evidence.set_comment(self.textBox_comment.toPlainText())

        # Update references
        # Todo: Move to independent reference widget
        self.evidence.remove_all_references()
        for reference in self.referenceWidget.dataTable.get_items():
            self.evidence.add_reference(reference)

        # Set either a term or a linked object depending on the current
        # selection.
        if self.comboBox.currentIndex() == 0:
            self.evidence.set_term(self.lineEdit_term.text())
            self.evidence.set_linked_item(None, reciprocal=False)
        elif self.comboBox.currentIndex() == 1:
            self.evidence.set_linked_item(self.linked_item, reciprocal=False)
            self.evidence.set_term(None)

        self.evidence.set_target(self.target_item, reciprocal=False)

    @QtCore.pyqtSlot()
    def select_eco(self):
        dialog = EvidenceCodeSelectionDialog()
        status = dialog.exec_()
        if status:
            self.set_eco(dialog.get_selected())

    def set_eco(self, eco):
        if eco and isinstance(eco, str):
            try:
                label_text = "{} ({})".format(all_ecos[eco].name, eco)
            except KeyError:
                label_text = eco
            self.label_eco.setText(label_text)
            self.eco = eco
        elif eco and isinstance(eco, EvidenceCode):
            label_text = "{} ({})".format(eco.name, eco.id)
            self.label_eco.setText(label_text)
            self.eco = eco.id
        else:
            self.label_eco.setText("")
            self.eco = None


class EvidenceCodeSelectionDialog(CustomStandardDialog, Ui_eco):

    def __init__(self):
        super(EvidenceCodeSelectionDialog, self).__init__()
        self.setupUi(self)
        self.eco_tree = QtGui.QStandardItemModel(self)
        self.sortproxy = RecursiveProxyFilter(self)
        self.treeView.setModel(self.sortproxy)
        self.sortproxy.setSourceModel(self.eco_tree)
        self.sortproxy.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.eco = None
        self.populate_tree()
        self.connect_slots()

    def connect_slots(self):
        """ Connect slots to the corresponding signals

        Note: The order of the connections is critical as self.eco needs
        to be updated before the OK button is toggled and the info can
        be updated

        Returns
        -------
        None
        """
        self.treeView.selectionModel().selectionChanged.connect(self.selection_changed)
        self.treeView.selectionModel().selectionChanged.connect(self.toggle_ok_button)
        self.treeView.selectionModel().selectionChanged.connect(self.populate_info_box)
        self.searchInput.textChanged.connect(self.sortproxy.setFilterFixedString)

    def populate_tree(self):
        root_item = self.eco_tree.invisibleRootItem()

        # Get elements that dont have a parent
        top_level_elements = [x for x, y in all_ecos.items() if not y.parents]

        for i, name in enumerate(sorted(top_level_elements)):
            element = all_ecos[name]
            tree_item = LinkedItem(element.name, element)
            root_item.setChild(i, tree_item)
            iterate_tree(tree_item, element)

    def get_selected(self):
        selection = self.treeView.selectedIndexes()
        if selection:
            source_index = self.sortproxy.mapToSource(selection[0])
            return self.eco_tree.itemFromIndex(source_index).link.id

    @QtCore.pyqtSlot()
    def populate_info_box(self):
        if self.eco:
            eco_obj = all_ecos[self.eco]
            self.label_id.setText(eco_obj.id)
            self.label_name.setText(eco_obj.name)
            self.label_definition.setText(eco_obj.definition)
            self.label_synonyms.setText("\n".join(eco_obj.synonyms))
        else:
            self.label_id.clear()
            self.label_name.clear()
            self.label_definition.clear()
            self.label_synonyms.clear()

    @QtCore.pyqtSlot()
    def selection_changed(self):
        self.eco = self.get_selected()

    @QtCore.pyqtSlot()
    def toggle_ok_button(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self.eco is not None)


class BatchEvidenceDialog(CustomStandardDialog, Ui_BatchEvidenceDialog):

    def __init__(self, model, parent=None):
        super(BatchEvidenceDialog, self).__init__(parent)
        self.setupUi(self)
        self.model = model
        self.evidence = Evidence(entity=Gene())

        self.accepted.connect(self.save_state)
        self.pushButton.clicked.connect(self.edit_evidence)

    @QtCore.pyqtSlot()
    def edit_evidence(self):
        dialog = EditEvidenceDialog(self.window(), self.model, evidence=self.evidence)
        if dialog.exec_():
            self.update_settings()

    @QtCore.pyqtSlot()
    def update_settings(self):
        self.label_assertion.setText(str(self.evidence.assertion))
        self.label_eco.setText(str(self.evidence.eco))
        self.label_target.setText(str(self.evidence.target))
        self.listWidget_referencees.clear()
        self.listWidget_referencees.addItems([x.reference_string() for x in self.evidence.references])
        self.textBrowser_comment.setText(self.evidence.comment)

    @QtCore.pyqtSlot()
    def save_state(self):
        genes_added = 0
        for gene_id in self.plainTextEdit.toPlainText().split("\n"):
            try:
                gene = self.model.genes.get_by_id(gene_id.strip())
            except KeyError:
                if self.comboBox_missing.currentText() == "Add":
                    gene = Gene(gene_id.strip())
                    self.model.add_gene(gene)
                    self.model.QtGeneTable.update_row_from_item(gene)
                    genes_added+=1
                else:
                    continue

            # Generate an evidence item for each gene
            evidence = Evidence(entity=gene,
                                eco=self.evidence.eco,
                                assertion=self.evidence.assertion,
                                comment=self.evidence.comment,
                                target=self.evidence.target)

            # Add reference
            for reference in self.evidence.references:
                evidence.add_reference(reference)

            # Add evidence to model
            self.model.all_evidences[evidence.internal_id] = evidence

        if genes_added:
            QMessageBox(self).information(self, "Genes added", "{} new genes added!".format(str(genes_added)))


def iterate_tree(standard_item, data_item):
    for n, element in enumerate(sorted(data_item.children, key=lambda x: x.name)):
            gene_item = LinkedItem(element.name, element)
            gene_item.setEditable(False)
            standard_item.setChild(n, gene_item)
            iterate_tree(gene_item, element)