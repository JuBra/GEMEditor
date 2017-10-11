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
        AnnotationSettingsDialog.resize(315, 100)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(AnnotationSettingsDialog)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_metabolites = QtWidgets.QVBoxLayout()
        self.verticalLayout_metabolites.setObjectName("verticalLayout_metabolites")
        self.label_metabolites = QtWidgets.QLabel(AnnotationSettingsDialog)
        self.label_metabolites.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.label_metabolites.setObjectName("label_metabolites")
        self.verticalLayout_metabolites.addWidget(self.label_metabolites)
        self.horizontalLayout.addLayout(self.verticalLayout_metabolites)
        self.verticalLayout_reactions = QtWidgets.QVBoxLayout()
        self.verticalLayout_reactions.setObjectName("verticalLayout_reactions")
        self.label_reactions = QtWidgets.QLabel(AnnotationSettingsDialog)
        self.label_reactions.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.label_reactions.setObjectName("label_reactions")
        self.verticalLayout_reactions.addWidget(self.label_reactions)
        self.horizontalLayout.addLayout(self.verticalLayout_reactions)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
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
        self.label_metabolites.setText(_translate("AnnotationSettingsDialog", "Metabolites"))
        self.label_reactions.setText(_translate("AnnotationSettingsDialog", "Reactions"))

