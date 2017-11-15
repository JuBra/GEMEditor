# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\src\EditMetaboliteDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MetaboliteEditDialog(object):
    def setupUi(self, MetaboliteEditDialog):
        MetaboliteEditDialog.setObjectName("MetaboliteEditDialog")
        MetaboliteEditDialog.resize(240, 223)
        self.verticalLayout = QtWidgets.QVBoxLayout(MetaboliteEditDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.attributeWidget = MetaboliteAttributesDisplayWidget(MetaboliteEditDialog)
        self.attributeWidget.setObjectName("attributeWidget")
        self.verticalLayout.addWidget(self.attributeWidget)
        self.tabWidget = QtWidgets.QTabWidget(MetaboliteEditDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.reactionsTab = ReactionsDisplayWidget()
        self.reactionsTab.setObjectName("reactionsTab")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.reactionsTab)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tabWidget.addTab(self.reactionsTab, "")
        self.annotationTab = AnnotationDisplayWidget()
        self.annotationTab.setObjectName("annotationTab")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.annotationTab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.tabWidget.addTab(self.annotationTab, "")
        self.evidenceTab = EvidenceDisplayWidget()
        self.evidenceTab.setObjectName("evidenceTab")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.evidenceTab)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.tabWidget.addTab(self.evidenceTab, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(MetaboliteEditDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(MetaboliteEditDialog)
        self.tabWidget.setCurrentIndex(0)
        self.buttonBox.accepted.connect(MetaboliteEditDialog.accept)
        self.buttonBox.rejected.connect(MetaboliteEditDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(MetaboliteEditDialog)

    def retranslateUi(self, MetaboliteEditDialog):
        _translate = QtCore.QCoreApplication.translate
        MetaboliteEditDialog.setWindowTitle(_translate("MetaboliteEditDialog", "Edit metabolite"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.reactionsTab), _translate("MetaboliteEditDialog", "Reactions"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.annotationTab), _translate("MetaboliteEditDialog", "Annotation"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.evidenceTab), _translate("MetaboliteEditDialog", "Evidence"))

from GEMEditor.model.display.base import AnnotationDisplayWidget, EvidenceDisplayWidget
from GEMEditor.model.display.metabolite import MetaboliteAttributesDisplayWidget, ReactionsDisplayWidget
