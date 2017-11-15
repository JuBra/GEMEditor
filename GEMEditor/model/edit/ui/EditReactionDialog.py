# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\src\EditReactionDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ReactionEditDialog(object):
    def setupUi(self, ReactionEditDialog):
        ReactionEditDialog.setObjectName("ReactionEditDialog")
        ReactionEditDialog.resize(383, 200)
        self.verticalLayout = QtWidgets.QVBoxLayout(ReactionEditDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.attributeWidget = ReactionAttributesDisplayWidget(ReactionEditDialog)
        self.attributeWidget.setObjectName("attributeWidget")
        self.verticalLayout.addWidget(self.attributeWidget)
        self.tabWidget = QtWidgets.QTabWidget(ReactionEditDialog)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setObjectName("tabWidget")
        self.metaboliteTab = StoichiometryDisplayWidget()
        self.metaboliteTab.setObjectName("metaboliteTab")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.metaboliteTab)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.tabWidget.addTab(self.metaboliteTab, "")
        self.geneTab = GenesDisplayWidget()
        self.geneTab.setObjectName("geneTab")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.geneTab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.tabWidget.addTab(self.geneTab, "")
        self.annotationTab = AnnotationDisplayWidget()
        self.annotationTab.setObjectName("annotationTab")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.annotationTab)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.tabWidget.addTab(self.annotationTab, "")
        self.evidenceTab = EvidenceDisplayWidget()
        self.evidenceTab.setObjectName("evidenceTab")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.evidenceTab)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.tabWidget.addTab(self.evidenceTab, "")
        self.commentTab = CommentDisplayWidget()
        self.commentTab.setObjectName("commentTab")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.commentTab)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.tabWidget.addTab(self.commentTab, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(ReactionEditDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ReactionEditDialog)
        self.tabWidget.setCurrentIndex(0)
        self.buttonBox.accepted.connect(ReactionEditDialog.accept)
        self.buttonBox.rejected.connect(ReactionEditDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ReactionEditDialog)

    def retranslateUi(self, ReactionEditDialog):
        _translate = QtCore.QCoreApplication.translate
        ReactionEditDialog.setWindowTitle(_translate("ReactionEditDialog", "Edit reaction"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.metaboliteTab), _translate("ReactionEditDialog", "Metabolites"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.geneTab), _translate("ReactionEditDialog", "Genes"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.annotationTab), _translate("ReactionEditDialog", "Annotations"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.evidenceTab), _translate("ReactionEditDialog", "Evidence"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.commentTab), _translate("ReactionEditDialog", "Comment"))

from GEMEditor.model.display.base import AnnotationDisplayWidget, CommentDisplayWidget, EvidenceDisplayWidget
from GEMEditor.model.display.reaction import GenesDisplayWidget, ReactionAttributesDisplayWidget, StoichiometryDisplayWidget
