# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 637)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.modelTab = ModelInfoTab()
        self.modelTab.setObjectName("modelTab")
        self.tabWidget.addTab(self.modelTab, "")
        self.reactionTab = ReactionTab()
        self.reactionTab.setObjectName("reactionTab")
        self.tabWidget.addTab(self.reactionTab, "")
        self.metaboliteTab = MetaboliteTab()
        self.metaboliteTab.setObjectName("metaboliteTab")
        self.tabWidget.addTab(self.metaboliteTab, "")
        self.geneTab = GeneTab()
        self.geneTab.setObjectName("geneTab")
        self.tabWidget.addTab(self.geneTab, "")
        self.testsTab = ModelTestsTab()
        self.testsTab.setObjectName("testsTab")
        self.tabWidget.addTab(self.testsTab, "")
        self.referenceTab = ReferenceTab()
        self.referenceTab.setObjectName("referenceTab")
        self.tabWidget.addTab(self.referenceTab, "")
        self.analysesTab = AnalysesTab()
        self.analysesTab.setObjectName("analysesTab")
        self.tabWidget.addTab(self.analysesTab, "")
        self.verticalLayout.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuModel = QtWidgets.QMenu(self.menubar)
        self.menuModel.setObjectName("menuModel")
        self.menuQuality_Control = QtWidgets.QMenu(self.menuModel)
        self.menuQuality_Control.setObjectName("menuQuality_Control")
        self.menuEvidences = QtWidgets.QMenu(self.menuModel)
        self.menuEvidences.setObjectName("menuEvidences")
        self.menuReferences = QtWidgets.QMenu(self.menuModel)
        self.menuReferences.setObjectName("menuReferences")
        self.menuSimulation = QtWidgets.QMenu(self.menubar)
        self.menuSimulation.setObjectName("menuSimulation")
        self.menuRun = QtWidgets.QMenu(self.menuSimulation)
        self.menuRun.setObjectName("menuRun")
        self.menuMetaNetX = QtWidgets.QMenu(self.menubar)
        self.menuMetaNetX.setObjectName("menuMetaNetX")
        self.menuMapping = QtWidgets.QMenu(self.menuMetaNetX)
        self.menuMapping.setObjectName("menuMapping")
        MainWindow.setMenuBar(self.menubar)
        self.actionNewModel = QtWidgets.QAction(MainWindow)
        self.actionNewModel.setObjectName("actionNewModel")
        self.actionOpenModel = QtWidgets.QAction(MainWindow)
        self.actionOpenModel.setObjectName("actionOpenModel")
        self.actionLoadTestModel = QtWidgets.QAction(MainWindow)
        self.actionLoadTestModel.setObjectName("actionLoadTestModel")
        self.actionSaveModel = QtWidgets.QAction(MainWindow)
        self.actionSaveModel.setObjectName("actionSaveModel")
        self.actionCloseModel = QtWidgets.QAction(MainWindow)
        self.actionCloseModel.setObjectName("actionCloseModel")
        self.actionCloseEditor = QtWidgets.QAction(MainWindow)
        self.actionCloseEditor.setMenuRole(QtWidgets.QAction.QuitRole)
        self.actionCloseEditor.setObjectName("actionCloseEditor")
        self.actionEditSettings = QtWidgets.QAction(MainWindow)
        self.actionEditSettings.setMenuRole(QtWidgets.QAction.PreferencesRole)
        self.actionEditSettings.setObjectName("actionEditSettings")
        self.actionBrowsePubmed = QtWidgets.QAction(MainWindow)
        self.actionBrowsePubmed.setObjectName("actionBrowsePubmed")
        self.actionOpenTestdialog = QtWidgets.QAction(MainWindow)
        self.actionOpenTestdialog.setObjectName("actionOpenTestdialog")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/information_icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAbout.setIcon(icon)
        self.actionAbout.setMenuRole(QtWidgets.QAction.AboutRole)
        self.actionAbout.setObjectName("actionAbout")
        self.actionStatistics = QtWidgets.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/statistics_icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionStatistics.setIcon(icon1)
        self.actionStatistics.setObjectName("actionStatistics")
        self.actionAuto_annotate = QtWidgets.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/add_from_database"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAuto_annotate.setIcon(icon2)
        self.actionAuto_annotate.setObjectName("actionAuto_annotate")
        self.actionCheck_consistency = QtWidgets.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/check_consistency_icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCheck_consistency.setIcon(icon3)
        self.actionCheck_consistency.setObjectName("actionCheck_consistency")
        self.actionAdd_Metabolite = QtWidgets.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/add_metabolite"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAdd_Metabolite.setIcon(icon4)
        self.actionAdd_Metabolite.setObjectName("actionAdd_Metabolite")
        self.actionGenerate_map = QtWidgets.QAction(MainWindow)
        self.actionGenerate_map.setObjectName("actionGenerate_map")
        self.actionAdd_cofactors = QtWidgets.QAction(MainWindow)
        self.actionAdd_cofactors.setObjectName("actionAdd_cofactors")
        self.actionShow_maps = QtWidgets.QAction(MainWindow)
        self.actionShow_maps.setObjectName("actionShow_maps")
        self.actionHistory = QtWidgets.QAction(MainWindow)
        self.actionHistory.setObjectName("actionHistory")
        self.actionFind_duplicated_reactions = QtWidgets.QAction(MainWindow)
        self.actionFind_duplicated_reactions.setObjectName("actionFind_duplicated_reactions")
        self.actionLoad_maps = QtWidgets.QAction(MainWindow)
        self.actionLoad_maps.setObjectName("actionLoad_maps")
        self.actionMaps = QtWidgets.QAction(MainWindow)
        self.actionMaps.setObjectName("actionMaps")
        self.actionCheck_gene_location = QtWidgets.QAction(MainWindow)
        self.actionCheck_gene_location.setObjectName("actionCheck_gene_location")
        self.actionCheck_evidences = QtWidgets.QAction(MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/check_evidence"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCheck_evidences.setIcon(icon5)
        self.actionCheck_evidences.setObjectName("actionCheck_evidences")
        self.actionRun_all_tests = QtWidgets.QAction(MainWindow)
        self.actionRun_all_tests.setObjectName("actionRun_all_tests")
        self.actionPrune_Gene_Trees = QtWidgets.QAction(MainWindow)
        self.actionPrune_Gene_Trees.setObjectName("actionPrune_Gene_Trees")
        self.actionAdd_batch = QtWidgets.QAction(MainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/batch_evidence"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAdd_batch.setIcon(icon6)
        self.actionAdd_batch.setObjectName("actionAdd_batch")
        self.actionAdd_Metabolites = QtWidgets.QAction(MainWindow)
        self.actionAdd_Metabolites.setObjectName("actionAdd_Metabolites")
        self.actionAdd_Reactions = QtWidgets.QAction(MainWindow)
        self.actionAdd_Reactions.setObjectName("actionAdd_Reactions")
        self.actionUpdate_database = QtWidgets.QAction(MainWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/update_database"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionUpdate_database.setIcon(icon7)
        self.actionUpdate_database.setObjectName("actionUpdate_database")
        self.actionAuto_annotation = QtWidgets.QAction(MainWindow)
        self.actionAuto_annotation.setObjectName("actionAuto_annotation")
        self.actionCheck_consistency_2 = QtWidgets.QAction(MainWindow)
        self.actionCheck_consistency_2.setObjectName("actionCheck_consistency_2")
        self.actionFin_duplicated_metabolites = QtWidgets.QAction(MainWindow)
        self.actionFin_duplicated_metabolites.setObjectName("actionFin_duplicated_metabolites")
        self.actionFBA = QtWidgets.QAction(MainWindow)
        self.actionFBA.setObjectName("actionFBA")
        self.actionPFBA = QtWidgets.QAction(MainWindow)
        self.actionPFBA.setObjectName("actionPFBA")
        self.actionUpdate_formulas = QtWidgets.QAction(MainWindow)
        self.actionUpdate_formulas.setObjectName("actionUpdate_formulas")
        self.actionUpdate_mapping = QtWidgets.QAction(MainWindow)
        self.actionUpdate_mapping.setObjectName("actionUpdate_mapping")
        self.action_mapping_load = QtWidgets.QAction(MainWindow)
        self.action_mapping_load.setObjectName("action_mapping_load")
        self.action_mapping_save = QtWidgets.QAction(MainWindow)
        self.action_mapping_save.setObjectName("action_mapping_save")
        self.menuFile.addAction(self.actionNewModel)
        self.menuFile.addAction(self.actionOpenModel)
        self.menuFile.addAction(self.actionLoadTestModel)
        self.menuFile.addAction(self.actionSaveModel)
        self.menuFile.addAction(self.actionCloseModel)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionCloseEditor)
        self.menuEdit.addAction(self.actionEditSettings)
        self.menuHelp.addAction(self.actionAbout)
        self.menuQuality_Control.addAction(self.actionFin_duplicated_metabolites)
        self.menuQuality_Control.addAction(self.actionFind_duplicated_reactions)
        self.menuQuality_Control.addSeparator()
        self.menuQuality_Control.addAction(self.actionUpdate_formulas)
        self.menuQuality_Control.addAction(self.actionPrune_Gene_Trees)
        self.menuQuality_Control.addSeparator()
        self.menuQuality_Control.addAction(self.actionRun_all_tests)
        self.menuEvidences.addAction(self.actionAdd_batch)
        self.menuEvidences.addSeparator()
        self.menuEvidences.addAction(self.actionCheck_evidences)
        self.menuReferences.addAction(self.actionBrowsePubmed)
        self.menuModel.addAction(self.actionMaps)
        self.menuModel.addAction(self.menuQuality_Control.menuAction())
        self.menuModel.addAction(self.menuEvidences.menuAction())
        self.menuModel.addAction(self.menuReferences.menuAction())
        self.menuModel.addSeparator()
        self.menuModel.addAction(self.actionStatistics)
        self.menuRun.addAction(self.actionFBA)
        self.menuRun.addAction(self.actionPFBA)
        self.menuSimulation.addAction(self.menuRun.menuAction())
        self.menuSimulation.addSeparator()
        self.menuSimulation.addAction(self.actionHistory)
        self.menuMapping.addAction(self.action_mapping_load)
        self.menuMapping.addAction(self.action_mapping_save)
        self.menuMapping.addSeparator()
        self.menuMapping.addAction(self.actionAuto_annotate)
        self.menuMapping.addAction(self.actionCheck_consistency)
        self.menuMapping.addSeparator()
        self.menuMapping.addAction(self.actionUpdate_mapping)
        self.menuMetaNetX.addAction(self.actionAdd_Metabolite)
        self.menuMetaNetX.addAction(self.actionAdd_Reactions)
        self.menuMetaNetX.addSeparator()
        self.menuMetaNetX.addAction(self.menuMapping.menuAction())
        self.menuMetaNetX.addSeparator()
        self.menuMetaNetX.addAction(self.actionUpdate_database)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuModel.menuAction())
        self.menubar.addAction(self.menuMetaNetX.menuAction())
        self.menubar.addAction(self.menuSimulation.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.modelTab), _translate("MainWindow", "Model"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.reactionTab), _translate("MainWindow", "Reactions"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.metaboliteTab), _translate("MainWindow", "Metabolites"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.geneTab), _translate("MainWindow", "Genes"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.testsTab), _translate("MainWindow", "Tests"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.referenceTab), _translate("MainWindow", "References"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.analysesTab), _translate("MainWindow", "Analyses"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.menuModel.setTitle(_translate("MainWindow", "Model"))
        self.menuQuality_Control.setTitle(_translate("MainWindow", "Quality Control"))
        self.menuEvidences.setTitle(_translate("MainWindow", "Evidences"))
        self.menuReferences.setTitle(_translate("MainWindow", "References"))
        self.menuSimulation.setTitle(_translate("MainWindow", "Simulation"))
        self.menuRun.setTitle(_translate("MainWindow", "Run"))
        self.menuMetaNetX.setTitle(_translate("MainWindow", "MetaNetX"))
        self.menuMapping.setTitle(_translate("MainWindow", "Mapping"))
        self.actionNewModel.setText(_translate("MainWindow", "New model"))
        self.actionOpenModel.setText(_translate("MainWindow", "Open model"))
        self.actionLoadTestModel.setText(_translate("MainWindow", "Load Test model"))
        self.actionSaveModel.setText(_translate("MainWindow", "Save Model"))
        self.actionCloseModel.setText(_translate("MainWindow", "Close Model"))
        self.actionCloseEditor.setText(_translate("MainWindow", "Close Editor"))
        self.actionEditSettings.setText(_translate("MainWindow", "Settings"))
        self.actionBrowsePubmed.setText(_translate("MainWindow", "Browse Pubmed"))
        self.actionOpenTestdialog.setText(_translate("MainWindow", "Open testdialog"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionStatistics.setText(_translate("MainWindow", "Statistics"))
        self.actionAuto_annotate.setText(_translate("MainWindow", "Auto annotate"))
        self.actionCheck_consistency.setText(_translate("MainWindow", "Check consistency"))
        self.actionAdd_Metabolite.setText(_translate("MainWindow", "Add Metabolite"))
        self.actionGenerate_map.setText(_translate("MainWindow", "Generate map"))
        self.actionAdd_cofactors.setText(_translate("MainWindow", "Add cofactors"))
        self.actionShow_maps.setText(_translate("MainWindow", "Show maps"))
        self.actionHistory.setText(_translate("MainWindow", "History"))
        self.actionFind_duplicated_reactions.setText(_translate("MainWindow", "Find duplicated reactions"))
        self.actionLoad_maps.setText(_translate("MainWindow", "Load maps"))
        self.actionMaps.setText(_translate("MainWindow", "Maps"))
        self.actionCheck_gene_location.setText(_translate("MainWindow", "Check gene location"))
        self.actionCheck_evidences.setText(_translate("MainWindow", "Check evidences"))
        self.actionRun_all_tests.setText(_translate("MainWindow", "Run all tests"))
        self.actionPrune_Gene_Trees.setText(_translate("MainWindow", "Simplify gene trees"))
        self.actionAdd_batch.setText(_translate("MainWindow", "Add batch"))
        self.actionAdd_Metabolites.setText(_translate("MainWindow", "Add Metabolites"))
        self.actionAdd_Reactions.setText(_translate("MainWindow", "Add Reactions"))
        self.actionUpdate_database.setText(_translate("MainWindow", "Update database"))
        self.actionAuto_annotation.setText(_translate("MainWindow", "Auto annotation"))
        self.actionCheck_consistency_2.setText(_translate("MainWindow", "Check consistency"))
        self.actionFin_duplicated_metabolites.setText(_translate("MainWindow", "Find duplicated metabolites"))
        self.actionFBA.setText(_translate("MainWindow", "FBA"))
        self.actionPFBA.setText(_translate("MainWindow", "pFBA"))
        self.actionUpdate_formulas.setText(_translate("MainWindow", "Update formulas"))
        self.actionUpdate_mapping.setText(_translate("MainWindow", "Update mapping"))
        self.action_mapping_load.setText(_translate("MainWindow", "Load from file"))
        self.action_mapping_save.setText(_translate("MainWindow", "Save to file"))

from GEMEditor.tabs import AnalysesTab, GeneTab, MetaboliteTab, ModelInfoTab, ModelTestsTab, ReactionTab, ReferenceTab
