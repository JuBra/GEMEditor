import logging
import os

import GEMEditor.rw.sbml3 as sbml3
import GEMEditor.rw.parsers as parsers
from GEMEditor.analysis.duplicates import group_duplicate_reactions, get_duplicated_metabolites, factory_duplicate_dialog
from GEMEditor.analysis.formula import update_formulae_iteratively
from GEMEditor.analysis.statistics import run_all_statistics, DisplayStatisticsDialog
from GEMEditor.base.classes import ProgressDialog
from GEMEditor.base.dialogs import ListDisplayDialog
from GEMEditor.base.functions import merge_groups_by_overlap
from GEMEditor.database.base import DatabaseWrapper
from GEMEditor.database.create import create_database_de_novo, database_exists
from GEMEditor.database.model import run_auto_annotation, run_check_consistency, load_mapping, store_mapping,\
    run_database_mapping
from GEMEditor.database.query import DialogDatabaseSelection
from GEMEditor.evidence.analysis import DialogEvidenceStatus
from GEMEditor.main.about import AboutDialog
from GEMEditor.main.model.tabs import *
from GEMEditor.main.settings import EditSettingsDialog
from GEMEditor.main.ui.MainWindow import Ui_MainWindow
from GEMEditor.main.update import UpdateAvailableDialog, UpdateCheck
from GEMEditor.map.dialog import MapListDialog
from GEMEditor.model.classes.cobra import Model, prune_gene_tree
from GEMEditor.model.edit.evidence import BatchEvidenceDialog
from GEMEditor.model.edit.model import EditModelDialog
from GEMEditor.model.edit.reference import PubmedBrowser
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QFileDialog, QMainWindow


LOGGER = logging.getLogger(__name__)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.model = None
        self.model_path = None

        # Thread pool for concurrent actions
        self.thread_pool = QtCore.QThreadPool()

        # Time regular update checks
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.check_updates)
        self.update_timer.start(900000)  # Check every 15 min

        # Run update check
        self.check_updates()

        # Create all widgets, layouts and connects
        self._create_connections()
        # Set initial state of editor
        self._set_model_loaded(False)

        # Debugging class
        LOGGER.debug("MainWindow initialized.")

    def _create_connections(self):
        # Model Tab
        self.modelTab.editModelSettingButton.clicked.connect(self.edit_model)
        self.actionRun_all_tests.triggered.connect(self.testsTab.run_tests)

        # File menu
        self.actionNewModel.triggered.connect(self.new_model)
        self.actionNewModel.setShortcut(QKeySequence.New)
        self.actionOpenModel.triggered.connect(self.open_model)
        self.actionOpenModel.setShortcut(QKeySequence.Open)
        self.actionLoadTestModel.triggered.connect(self.open_test_model)
        self.actionSaveModel.triggered.connect(self.save_model)
        self.actionSaveModel.setShortcut(QKeySequence.Save)
        self.actionCloseModel.triggered.connect(self.close_model)
        self.actionCloseModel.setShortcut(QKeySequence.Close)
        self.actionCloseEditor.triggered.connect(self.close)
        self.actionCloseEditor.setShortcut(QKeySequence.Quit)

        # Edit menu
        self.actionEditSettings.triggered.connect(self.edit_settings)
        self.actionEditSettings.setShortcut(QKeySequence.Preferences)

        # Model menu
        self.actionMaps.triggered.connect(self.map_show_list)

        self.actionFind_duplicated_reactions.triggered.connect(self.model_find_duplicate_reactions)
        self.actionFin_duplicated_metabolites.triggered.connect(self.model_find_duplicate_metabolites)
        self.actionCheck_evidences.triggered.connect(self.check_all_evidences)
        self.actionPrune_Gene_Trees.triggered.connect(self.prune_gene_trees)
        self.actionAdd_batch.triggered.connect(self.add_batch_evidences)
        self.actionBrowsePubmed.triggered.connect(self.browsePubmedSlot)
        self.actionStatistics.triggered.connect(self.model_show_statistics)
        self.actionUpdate_formulas.triggered.connect(self.quality_update_formulae_from_context)

        # MetaNetX menu
        self.actionAdd_Metabolite.triggered.connect(self.database_add_metabolite)
        self.actionAdd_Reactions.triggered.connect(self.database_add_reaction)

        ### Mapping
        self.action_mapping_load.triggered.connect(self.database_load_mapping)
        self.action_mapping_save.triggered.connect(self.database_save_mapping)
        self.actionAuto_annotate.triggered.connect(self.database_auto_annotate)
        self.actionCheck_consistency.triggered.connect(self.database_check_consistency)
        self.actionUpdate_mapping.triggered.connect(self.database_update_mapping)

        self.actionUpdate_database.triggered.connect(self.database_update_database)

        # About menu
        self.actionAbout.triggered.connect(self.show_about)
        self.actionAbout.setShortcut(QKeySequence.HelpContents)

        # Debugging class
        LOGGER.debug("MainWindow menu signals connected.")

    def check_updates(self):
        """ Check for updates of GEMEditor """
        worker = UpdateCheck()
        worker.signals.new_version.connect(self.show_new_version_dialog)
        self.thread_pool.start(worker)

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
        self._set_model_loaded(model is not None)

    def _set_model_loaded(self, bool):
        # Set the accessibility of different elements of the GUI depending on if a model is loaded or not
        self.actionCloseModel.setEnabled(bool)
        self.actionSaveModel.setEnabled(bool)
        self.menuMetaNetX.setEnabled(bool)
        self.menuModel.setEnabled(bool)
        self.modelTab.editModelSettingButton.setEnabled(bool)
        for i in range(1, self.tabWidget.count()):
            self.tabWidget.setTabEnabled(i, bool)

        self.tabWidget.setCurrentWidget(self.modelTab)
        self.update_window_title()

    @QtCore.pyqtSlot()
    def open_test_model(self):
        try:
            from cobra.test import data_dir
        except ImportError:
            LOGGER.debug("Cobra path to test model not found.")
            QMessageBox().warning(None, "Error", "Path to test model not found!")
            return
        else:
            full_path = os.path.join(data_dir, "iJO1366.xml")
            LOGGER.debug("Opening Testmodel at '{}'".format(full_path))
            self.open_model(full_path)

    @QtCore.pyqtSlot()
    def show_about(self):
        AboutDialog(self).exec_()

    @QtCore.pyqtSlot()
    def open_model(self, filename=None):
        """ Open model from file

        Parameters
        ----------
        filename: str,
            Path to model file

        """
        # Close existing model
        if not self.close_model():
            return

        # No path provided. Ask user.
        if not filename:
            last_path = Settings().value("LastPath", None)
            filename, filters = QFileDialog.getOpenFileName(self, "Open Model", last_path,
                                                            "Sbml files (*.xml *.sbml);;Json files (*.json)")

        # Setup file parser
        if not filename or not isinstance(filename, str):
            return
        elif filename.endswith((".xml", ".sbml")):
            parser = parsers.SBMLParser(filename)
        else:
            # Todo: Implement JSON parser
            QMessageBox().critical(None, "Not implemented",
                                   "Unknown file type: '{0!s}'".format(os.path.splitext(filename)))
            return

        # Parse model
        model = parser.parse()
        if parser.errors or parser.warnings:
            parsers.ParserErrorDialog(parser).exec_()

        if model:
            self.set_model(model, filename)
            Settings().setValue("LastPath", os.path.dirname(filename))

    @QtCore.pyqtSlot()
    def database_load_mapping(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open mapping", "",
                                                  "Json files (*.json)")
        load_mapping(self.model, filename)

    @QtCore.pyqtSlot()
    def database_save_mapping(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save mapping", "",
                                                  "Json files (*.json)")
        store_mapping(self.model, filename)

    @QtCore.pyqtSlot()
    def save_model(self):
        settings = Settings()
        last_path = settings.value("LastPath")
        filename, filter = QFileDialog.getSaveFileName(None, "Save Model", last_path,
                                                       "Sbml files (*.xml *.sbml)")
        if filename:
            sbml3.write_sbml3_model(filename, self.model)
            settings.setValue("LastPath", os.path.dirname(filename))
            # Set path to saved path
            self.model_path = filename
            self.modelTab.set_path(filename)

    @QtCore.pyqtSlot()
    def close_model(self):
        if self.model is None:
            return True
        elif self.check_model_closing():
            LOGGER.debug("Closing model..")
            self.save_table_headers()
            self.model.close()
            self.set_model(None, None)
            self._set_model_loaded(False)
            return True
        else:
            return False

    @QtCore.pyqtSlot()
    def new_model(self):
        if self.close_model():
            model = Model()
            dialog = EditModelDialog(model)
            status = dialog.exec_()
            if status:
                self.set_model(model, None)
                self._set_model_loaded(True)

    @QtCore.pyqtSlot()
    def edit_model(self):
        dialog = EditModelDialog(self.model)
        status = dialog.exec_()
        if status:
            self.set_model(self.model, self.model_path)
            self.update_window_title()

    @QtCore.pyqtSlot()
    def model_find_duplicate_reactions(self):
        if self.model:
            duplicates = group_duplicate_reactions(self.model.reactions)
            self.duplicate_dialog = factory_duplicate_dialog("reaction", duplicates)
            self.duplicate_dialog.show()

    @QtCore.pyqtSlot()
    def model_find_duplicate_metabolites(self):
        if self.model:
            duplicates = get_duplicated_metabolites(self.model.metabolites,
                                                    self.model.database_mapping)
            groups = merge_groups_by_overlap(duplicates)
            self.duplicate_dialog = factory_duplicate_dialog("metabolite", groups)
            self.duplicate_dialog.show()

    @QtCore.pyqtSlot()
    def edit_settings(self):
        EditSettingsDialog(self).exec_()

    @QtCore.pyqtSlot()
    def update_window_title(self):
        app_name = Settings().applicationName()
        if self.model is not None:
            self.setWindowTitle(" - ".join([app_name, str(self.model.id)]))
        else:
            self.setWindowTitle(app_name)

    @QtCore.pyqtSlot()
    def show_new_version_dialog(self, new_version):
        dialog = UpdateAvailableDialog(new_version)
        if not dialog.version_is_ignored():
            dialog.exec_()

    def save_table_headers(self):
        settings = Settings()
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
    def model_show_statistics(self):
        with ProgressDialog(self, "Statistics", "Running stats..") as progress:
            model_stats = run_all_statistics(self.model, progress)

        # Display results
        DisplayStatisticsDialog(model_stats).exec_()

    @QtCore.pyqtSlot()
    def database_update_mapping(self):
        """ Update the mapping of the metabolites to the database

        Returns
        -------

        """
        # Check that model and database exist
        if not self.model or not database_exists(self):
            return

        # Run update
        with ProgressDialog(self, title="Update mapping..") as progress, DatabaseWrapper() as database:
            run_database_mapping(database, self.model, progress)

        # Success
        QMessageBox().information(None, "Success", "Metabolites have been mapped to the database.")

    @QtCore.pyqtSlot()
    def database_auto_annotate(self):
        """ Automatically annotate model items from database

        Returns
        -------

        """

        # Check that model and database exists
        if not self.model or not database_exists(self):
            return

        # Update annotations
        with ProgressDialog(self, title="Updating annotations") as progress, DatabaseWrapper() as database:
            updated_items = run_auto_annotation(database, self.model, progress, self)

        # Update
        if updated_items:
            QMessageBox().information(None, "Items changed",
                                      "Annotations updated of:\n"
                                      "{0!s} metabolites\n"
                                      "{1!s} reactions\n\n"
                                      "Attributes updated of:\n"
                                      "{2!s} metabolites\n"
                                      "{3!s} reactions".format(len(updated_items["metabolite_annotations"]),
                                                               len(updated_items["reaction_annotations"]),
                                                               len(updated_items["metabolite_attributes"]),
                                                               len(updated_items["reaction_attributes"])))
        else:
            QMessageBox().information(None, "No change", "No items have been changed.")

    @QtCore.pyqtSlot()
    def database_check_consistency(self):

        # Check that model and database exists
        if not self.model or not database_exists(self):
            return

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
    def database_add_metabolite(self):
        # Check that model and database exists
        if not self.model or not database_exists(self):
            return

        dialog = DialogDatabaseSelection(model=self.model, data_type="metabolite", parent=self)
        dialog.show()

    @QtCore.pyqtSlot()
    def database_add_reaction(self):
        # Check that model and database exists
        if not self.model or not database_exists(self):
            return

        dialog = DialogDatabaseSelection(model=self.model, data_type="reaction", parent=self)
        dialog.show()

    @QtCore.pyqtSlot()
    def database_update_database(self):
        """ Update the local MetaNetX database

        Returns
        -------
        None
        """

        result = create_database_de_novo(parent=self,
                                         database_path=DatabaseWrapper.get_database_path())
        if result:
            QMessageBox().information(None, "Success!", "The database has successfully been setup.")
        else:
            QMessageBox().information(None, "Aborted", "Database has not been created.")

    @QtCore.pyqtSlot()
    def quality_update_formulae_from_context(self):
        if not self.model:
            return

        # Warn user about underlying assumptions
        answer = QMessageBox().question(None, "Warning",
                                        "This method assumes that the stoichiometries of the reactions are correct.\n"
                                        "Erroneous formulas will be added to the metabolites if this is not the case.\n"
                                        "Do you want to run this update anyway?")
        if answer != QMessageBox.Yes:
            return

        updated_metabolites = update_formulae_iteratively(self.model)
        if updated_metabolites:
            self.model.gem_update_metabolites(updated_metabolites)
            QMessageBox().information(None, "Metabolites updated",
                                      "{0!s} metabolites updated.".format(len(updated_metabolites)))
        else:
            QMessageBox().information(None, "No change", "No metabolites updated.")

    @QtCore.pyqtSlot()
    def map_show_list(self):
        if self.model:
            MapListDialog(None, self.model).exec_()

    @QtCore.pyqtSlot()
    def check_all_evidences(self):
        if self.model:
            DialogEvidenceStatus(self.model).exec_()

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
            BatchEvidenceDialog(self.model, self).exec_()

    def check_model_closing(self):
        close_msg = "Are you sure you want to close the model and discard changes?"
        reply = QMessageBox.question(self, 'Message',
                         close_msg, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            return True
        else:
            return False

    def closeEvent(self, event):
        if self.close_model():
            self.update_timer.stop()
            LOGGER.debug("Update timer stopped.")
            event.accept()
        else:
            event.ignore()
