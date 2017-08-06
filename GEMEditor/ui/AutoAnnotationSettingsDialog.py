# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AutoAnnotationSettingsDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AutoAnnotationDialog(object):
    def setupUi(self, AutoAnnotationDialog):
        AutoAnnotationDialog.setObjectName("AutoAnnotationDialog")
        AutoAnnotationDialog.resize(237, 110)
        self.verticalLayout = QtWidgets.QVBoxLayout(AutoAnnotationDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.checkBox_charge = QtWidgets.QCheckBox(AutoAnnotationDialog)
        self.checkBox_charge.setObjectName("checkBox_charge")
        self.verticalLayout.addWidget(self.checkBox_charge)
        self.checkBox_name = QtWidgets.QCheckBox(AutoAnnotationDialog)
        self.checkBox_name.setObjectName("checkBox_name")
        self.verticalLayout.addWidget(self.checkBox_name)
        self.checkBox_annotations = QtWidgets.QCheckBox(AutoAnnotationDialog)
        self.checkBox_annotations.setChecked(True)
        self.checkBox_annotations.setObjectName("checkBox_annotations")
        self.verticalLayout.addWidget(self.checkBox_annotations)
        self.buttonBox = QtWidgets.QDialogButtonBox(AutoAnnotationDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AutoAnnotationDialog)
        self.buttonBox.accepted.connect(AutoAnnotationDialog.accept)
        self.buttonBox.rejected.connect(AutoAnnotationDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AutoAnnotationDialog)

    def retranslateUi(self, AutoAnnotationDialog):
        _translate = QtCore.QCoreApplication.translate
        AutoAnnotationDialog.setWindowTitle(_translate("AutoAnnotationDialog", "Select settings"))
        self.checkBox_charge.setText(_translate("AutoAnnotationDialog", "Update metabolite charge"))
        self.checkBox_name.setText(_translate("AutoAnnotationDialog", "Update metabolite name"))
        self.checkBox_annotations.setText(_translate("AutoAnnotationDialog", "Update annotations"))

