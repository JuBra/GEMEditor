import logging
from PyQt5.QtWidgets import QFileDialog, QDialogButtonBox, QMainWindow
from PyQt5.QtCore import QStandardPaths
from GEMEditor.tabs import *
from GEMEditor.dialogs.program import EditSettingsDialog, AboutDialog, ListDisplayDialog
from GEMEditor.dialogs.model import EditModelDialog
from GEMEditor.dialogs.reference import PubmedBrowser
from GEMEditor.dialogs.standard import MetaboliteSelectionDialog
from GEMEditor.dialogs.qualitychecks import DuplicateDialog, LocalizationCheck, FailingEvidencesDialog
from GEMEditor.dialogs.map import MapDialog, MapListDialog
from GEMEditor.dialogs import UpdateAvailableDialog, BatchEvidenceDialog
from GEMEditor import __projectpage__
import GEMEditor.rw.sbml3 as sbml3
from GEMEditor.ui.MainWindow import Ui_MainWindow
from GEMEditor.cobraClasses import Model, prune_gene_tree
from GEMEditor.analysis import group_duplicate_reactions
from GEMEditor.analysis.statistics import run_all_statistics, DisplayStatisticsDialog
from GEMEditor.connect.checkversion import UpdateCheck
from GEMEditor.database.create import create_database_de_novo
from GEMEditor.database.model import run_auto_annotation, run_check_consistency
from GEMEditor.database.query import DatabaseSelectionDialog
import os
import GEMEditor.icons_rc


LOGGER = logging.getLogger(__name__)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args):
        QMainWindow.__init__(self, *args)
        self.setupUi(self)
        self.thread = None
        self.worker = None
        self.model = None
        self.maps = []
        self.model_path = None

        # Check if there is a new version of the software
        self.check_updates()
        self.check_email()
        # Create all widgets, layouts and connects
        self.createConnects()
        # Set initial state of editor
        self.modelLoaded(False)

        # Debugging class
        LOGGER.debug("MainWindow initialized.")

    def createConnects(self):
        # Model Tab
        self.modelTab.editModelSettingButton.clicked.connect(self.editModelsettings)
        self.actionRun_all_tests.triggered.connect(self.testsTab.run_tests)

        # File menu
        self.actionNewModel.triggered.connect(self.createModel)
        self.actionOpenModel.triggered.connect(self.openModel)
        self.actionLoadTestModel.triggered.connect(self.loadTestModel)
        self.actionSaveModel.triggered.connect(self.saveModel)
        self.actionCloseModel.triggered.connect(self.closeModel)
        self.actionCloseEditor.triggered.connect(self.close)

        # Edit menu
        self.actionEditSettings.triggered.connect(self.editSettings)

        # Model menu
        self.actionMaps.triggered.connect(self.show_map_list)

        self.actionFind_duplicated_reactions.triggered.connect(self.find_duplicate_reactions)
        self.actionCheck_evidences.triggered.connect(self.check_all_evidences)
        self.actionPrune_Gene_Trees.triggered.connect(self.prune_gene_trees)
        self.actionAdd_batch.triggered.connect(self.add_batch_evidences)
        self.actionBrowsePubmed.triggered.connect(self.browsePubmedSlot)
        self.actionStatistics.triggered.connect(self.show_statistics)

        # MetaNetX menu
        self.actionAdd_Metabolite.triggered.connect(self.add_metabolite_from_database)
        self.actionAuto_annotate.triggered.connect(self.auto_annotate)
        self.actionCheck_consistency.triggered.connect(self.check_consistency)

        self.actionUpdate_database.triggered.connect(self.update_metanetx_database)

        # About menu
        self.actionAbout.triggered.connect(self.showAbout)

        # Debugging class
        LOGGER.debug("MainWindow menu signals connected.")

    def check_email(self):
        settings = QtCore.QSettings()
        email = settings.value("Email")
        if email is None:
            dialog = EditSettingsDialog(self)
            dialog.exec_()

        # Debugging class
        LOGGER.debug("E-mail checked.")

    def check_updates(self):
        self.thread = QtCore.QThread()
        self.worker = UpdateCheck()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.check_for_updates)
        self.worker.new_version.connect(self.show_newversion_dialog)
        self.worker.finished.connect(self.thread.quit)
        self.thread.start()

    @QtCore.pyqtSlot()
    def loadTestModel(self):
        pass

    @QtCore.pyqtSlot()
    def showAbout(self):
        AboutDialog(self).exec_()

    @QtCore.pyqtSlot()
    def openModel(self, filename=None):
        if self.closeModel():
            settings = QtCore.QSettings()
            last_path = settings.value("LastPath") or QStandardPaths.DesktopLocation or None

            if filename is None:
                filename, filters = QFileDialog.getOpenFileName(self,
                                                                self.tr("Open Model"),
                                                                last_path,
                                                                self.tr("Sbml files (*.xml *.sbml);;Json files (*.json)"))
                if filename:
                    settings.setValue("LastPath", os.path.dirname(filename))

            if filename.endswith((".xml", ".sbml")):
                try:
                    model = sbml3.read_sbml3_model(filename)
                except:
                    import traceback
                    QErrorMessage(self).showMessage("There has been an error parsing the model:\n{}".format(traceback.format_exc()),
                                                          "Parsing error")
                    return
                else:
                    if model is not None:
                        model.setup_tables()
                        self.set_model(model, filename)
                        self.modelLoaded(True)
            elif filename.endswith(".json"):
                model = cobra.io.load_json_model(filename)
                self.set_model(model, filename)
                self.modelLoaded(True)

    @QtCore.pyqtSlot()
    def saveModel(self):
        settings = QtCore.QSettings()
        last_path = settings.value("LastPath") or QStandardPaths.DesktopLocation or None
        filename, filter = QFileDialog.getSaveFileName(self, self.tr("Save Model"), last_path,
                                                       self.tr("Sbml files (*.xml *.sbml)"))
        if filename.endswith(".xml"):
            sbml3.write_sbml3_model(filename, self.model)
            settings.setValue("LastPath", os.path.dirname(filename))
            # Set path to saved path
            self.model_path = filename
            self.modelTab.set_path(filename)

    @QtCore.pyqtSlot()
    def closeModel(self):
        if self.model is None:
            return True
        elif self.check_model_closing():
            self.save_table_headers()
            self.model.close()
            self.set_model(None, None)
            self.modelLoaded(False)
            return True
        else:
            return False

    @QtCore.pyqtSlot()
    def createModel(self):
        if self.closeModel():
            model = Model()
            dialog = EditModelDialog(self, model)
            status = dialog.exec_()
            if status:
                self.set_model(model, None)
                self.modelLoaded(True)

    @QtCore.pyqtSlot()
    def editModelsettings(self):
        dialog = EditModelDialog(self, self.model)
        status = dialog.exec_()
        if status:
            self.set_model(self.model, self.model_path)
            self.set_window_title()

    @QtCore.pyqtSlot()
    def find_duplicate_reactions(self):
        if self.model:
            duplicates = group_duplicate_reactions(self.model.reactions)
            self.duplicate_dialog = DuplicateDialog(duplicates)
            self.duplicate_dialog.show()

    @QtCore.pyqtSlot()
    def editSettings(self):
        EditSettingsDialog(self).exec_()

    def modelLoaded(self, bool):
        # Set the accessibility of different elements of the GUI depending on if a model is loaded or not
        self.actionCloseModel.setEnabled(bool)
        self.actionSaveModel.setEnabled(bool)
        self.menuMetaNetX.setEnabled(bool)
        self.menuModel.setEnabled(bool)
        self.menuSimulation.setEnabled(bool)
        self.modelTab.editModelSettingButton.setEnabled(bool)
        for i in range(1, self.tabWidget.count()):
            self.tabWidget.setTabEnabled(i, bool)

        self.tabWidget.setCurrentWidget(self.modelTab)
        self.set_window_title()

    @QtCore.pyqtSlot()
    def set_window_title(self):
        app_name = QtCore.QSettings().applicationName()
        if self.model is not None:
            self.setWindowTitle(" - ".join([app_name, str(self.model.id)]))
        else:
            self.setWindowTitle(app_name)

    @QtCore.pyqtSlot()
    def show_newversion_dialog(self):
        settings = QtCore.QSettings()

        # Get the current version from the CheckUpdate Thread
        try:
            current_version = self.sender().current_version
        except AttributeError:
            current_version = None

        # Do not show a dialog if the current version is set to be ignored
        if settings.value("IgnoreVersion", None) == current_version:
            return

        # Show update dialog
        dialog = UpdateAvailableDialog(self)
        dialog.exec_()

        # Go to project page if update requested
        if dialog.status is QDialogButtonBox.Yes:
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(__projectpage__))
        elif dialog.status is QDialogButtonBox.No and not dialog.show_again():
            settings.setValue("IgnoreVersion", current_version)
            settings.sync()

    def save_table_headers(self):
        settings = QtCore.QSettings()
        settings.setValue("ReactionTableViewState", self.reactionTab.dataView.horizontalHeader().saveState())
        settings.setValue("MetaboliteTableViewState", self.metaboliteTab.dataView.horizontalHeader().saveState())
        settings.setValue("GenesTableViewState", self.geneTab.dataView.horizontalHeader().saveState())
        settings.setValue("TestsTableViewState", self.testsTab.dataView.horizontalHeader().saveState())
        settings.setValue("ReferenceTableViewState", self.referenceTab.dataView.horizontalHeader().saveState())
        settings.sync()

    @QtCore.pyqtSlot()
    def browsePubmedSlot(self):
        self.pmidBrowser = PubmedBrowser(self)
        self.pmidBrowser.setModal(False)
        self.pmidBrowser.show()

    @QtCore.pyqtSlot()
    def openNotImplementedDialog(self):
        QErrorMessage().showMessage("Not implemented!")

    @QtCore.pyqtSlot()
    def show_statistics(self):
        # Run the statistics
        progress = QProgressDialog()
        progress.setWindowTitle("Statistics")
        progress.setLabelText("Running stats..")
        QApplication.processEvents()
        model_stats = run_all_statistics(self.model, progress)
        progress.close()

        # Display results
        dialog = DisplayStatisticsDialog(model_stats)
        dialog.exec_()

    @QtCore.pyqtSlot()
    def auto_annotate(self):
        if not self.model:
            return
        updated_items = run_auto_annotation(self.model, self)
        if updated_items:
            QMessageBox().information(None, "Items changed",
                                      "{} items have been updated!".format(len(updated_items)))

    @QtCore.pyqtSlot()
    def check_consistency(self):
        errors = run_check_consistency(self.model, self)
        if errors:
            dialog = ListDisplayDialog(errors, parent=self)
            dialog.setWindowTitle("Potential errors found!")
            dialog.infoLabel.setText("The annotations in these items seem inconsistent:")
            dialog.show()
        else:
            QMessageBox.information(None, self.tr("Annotations seem to be correct!"),
                                          self.tr("There have been no conflicts found between annotations!"),
                                          QMessageBox.Ok)

    @QtCore.pyqtSlot()
    def add_metabolite_from_database(self):
        try:
            dialog = DatabaseSelectionDialog(self, self.model)
        except ConnectionError:
            return
        else:
            dialog.show()

    def set_model(self, model, path):
        self.model = model
        self.model_path = path
        if model is not None:
            self.model.modelChanged.connect(self.modelTab.modelInfoWidget.update_information)
            self.model.modelChanged.connect(self.modelTab.modelAnnotationWidget.update_information)
        self.modelTab.set_model(model, path)
        self.reactionTab.set_model(model)
        self.metaboliteTab.set_model(model)
        self.geneTab.set_model(model)
        self.testsTab.set_model(model)
        self.referenceTab.set_model(model)
        self.analysesTab.set_model(model)

    @QtCore.pyqtSlot()
    def generate_map(self):
        if self.model:
            reactions = self.reactionTab.dataView.get_selected_items()
            self.mapdialog = MapDialog(self, reactions)
            self.mapdialog.setWindowFlags(QtCore.Qt.Window)
            self.mapdialog.setModal(False)
            self.mapdialog.show()

    @QtCore.pyqtSlot()
    def show_map_list(self):
        dialog = MapListDialog(self, self.maps, self.model)
        self.model.dialogs.add(dialog)
        dialog.show()

    @QtCore.pyqtSlot()
    def check_all_evidences(self):
        if not self.model:
            return

        failing_evidences = {}
        for evidence in self.model.all_evidences.values():
            if not evidence.is_valid():
                failing_evidences[evidence] = ""

        if failing_evidences:
            dialog = FailingEvidencesDialog(failing_evidences, self.model)
            self.model.dialogs.add(dialog)
            dialog.show()

    @QtCore.pyqtSlot()
    def prune_gene_trees(self):
        if self.model:
            for reaction in self.model.reactions:
                # Prune tree as long as there is no further change
                while True:
                    before_pruning = reaction.gene_reaction_rule
                    prune_gene_tree(reaction)
                    if reaction.gene_reaction_rule == before_pruning:
                        break

    @QtCore.pyqtSlot()
    def add_batch_evidences(self):
        if self.model:
            dialog = BatchEvidenceDialog(self.model, self)
            dialog.exec_()

    @QtCore.pyqtSlot()
    def update_metanetx_database(self):
        result = create_database_de_novo(self)
        if result:
            QMessageBox().information(None, "Success!", "The database has successfully been setup.")

    def check_model_closing(self):
        close_msg = "Are you sure you want to close the model and discard changes?"
        reply = QMessageBox.question(self, 'Message',
                         close_msg, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            return True
        else:
            return False

    def closeEvent(self, event):
        # Save the column width of the individual tabs
        if self.closeModel():
            event.accept()
        else:
            event.ignore()