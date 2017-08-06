# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\AnnotationSettingsDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AnnotationSettingsDialog(object):
    def setupUi(self, AnnotationSettingsDialog):
        AnnotationSettingsDialog.setObjectName("AnnotationSettingsDialog")
        AnnotationSettingsDialog.resize(176, 199)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(AnnotationSettingsDialog)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox_met_attributes = QtWidgets.QGroupBox(AnnotationSettingsDialog)
        self.groupBox_met_attributes.setObjectName("groupBox_met_attributes")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_met_attributes)
        self.verticalLayout.setObjectName("verticalLayout")
        self.checkBox_charge = QtWidgets.QCheckBox(self.groupBox_met_attributes)
        self.checkBox_charge.setObjectName("checkBox_charge")
        self.verticalLayout.addWidget(self.checkBox_charge)
        self.checkBox_formula = QtWidgets.QCheckBox(self.groupBox_met_attributes)
        self.checkBox_formula.setObjectName("checkBox_formula")
        self.verticalLayout.addWidget(self.checkBox_formula)
        self.verticalLayout_2.addWidget(self.groupBox_met_attributes)
        self.groupBox_met_annotation = QtWidgets.QGroupBox(AnnotationSettingsDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_met_annotation.sizePolicy().hasHeightForWidth())
        self.groupBox_met_annotation.setSizePolicy(sizePolicy)
        self.groupBox_met_annotation.setObjectName("groupBox_met_annotation")
        self.verticalLayout_2.addWidget(self.groupBox_met_annotation)
        self.groupBox_react_annotation = QtWidgets.QGroupBox(AnnotationSettingsDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_react_annotation.sizePolicy().hasHeightForWidth())
        self.groupBox_react_annotation.setSizePolicy(sizePolicy)
        self.groupBox_react_annotation.setObjectName("groupBox_react_annotation")
        self.verticalLayout_2.addWidget(self.groupBox_react_annotation)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(AnnotationSettingsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_3.addWidget(self.buttonBox)

        self.retranslateUi(AnnotationSettingsDialog)
        self.buttonBox.accepted.connect(AnnotationSettingsDialog.accept)
        self.buttonBox.rejected.connect(AnnotationSettingsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AnnotationSettingsDialog)

    def retranslateUi(self, AnnotationSettingsDialog):
        _translate = QtCore.QCoreApplication.translate
        AnnotationSettingsDialog.setWindowTitle(_translate("AnnotationSettingsDialog", "Choose settings"))
        self.groupBox_met_attributes.setTitle(_translate("AnnotationSettingsDialog", "Metabolite attributes"))
        self.checkBox_charge.setText(_translate("AnnotationSettingsDialog", "Charge"))
        self.checkBox_formula.setText(_translate("AnnotationSettingsDialog", "Formula"))
        self.groupBox_met_annotation.setTitle(_translate("AnnotationSettingsDialog", "Metabolite annotations"))
        self.groupBox_react_annotation.setTitle(_translate("AnnotationSettingsDialog", "Reaction annotations"))

