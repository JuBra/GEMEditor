# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GeneEditDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_GeneEditDialog(object):
    def setupUi(self, GeneEditDialog):
        GeneEditDialog.setObjectName("GeneEditDialog")
        GeneEditDialog.resize(260, 182)
        self.verticalLayout = QtWidgets.QVBoxLayout(GeneEditDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.attributeWidget = GeneAttributesDisplayWidget(GeneEditDialog)
        self.attributeWidget.setObjectName("attributeWidget")
        self.verticalLayout.addWidget(self.attributeWidget)
        self.tabWidget = QtWidgets.QTabWidget(GeneEditDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.reactionTab = ReactionsDisplayWidget()
        self.reactionTab.setObjectName("reactionTab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.reactionTab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tabWidget.addTab(self.reactionTab, "")
        self.tab_annotations = AnnotationDisplayWidget()
        self.tab_annotations.setObjectName("tab_annotations")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_annotations)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.tabWidget.addTab(self.tab_annotations, "")
        self.evidenceTab = EvidenceDisplayWidget()
        self.evidenceTab.setObjectName("evidenceTab")
        self.tabWidget.addTab(self.evidenceTab, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(GeneEditDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(GeneEditDialog)
        self.tabWidget.setCurrentIndex(0)
        self.buttonBox.accepted.connect(GeneEditDialog.accept)
        self.buttonBox.rejected.connect(GeneEditDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(GeneEditDialog)

    def retranslateUi(self, GeneEditDialog):
        _translate = QtCore.QCoreApplication.translate
        GeneEditDialog.setWindowTitle(_translate("GeneEditDialog", "Edit Gene"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.reactionTab), _translate("GeneEditDialog", "Reactions"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_annotations), _translate("GeneEditDialog", "Annotation"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.evidenceTab), _translate("GeneEditDialog", "Evidence"))

from GEMEditor.widgets.model import AnnotationDisplayWidget, EvidenceDisplayWidget, GeneAttributesDisplayWidget, ReactionsDisplayWidget
