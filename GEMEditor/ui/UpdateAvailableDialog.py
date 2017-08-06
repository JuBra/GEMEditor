# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UpdateAvailableDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_UpdateAvailableDialog(object):
    def setupUi(self, UpdateAvailableDialog):
        UpdateAvailableDialog.setObjectName("UpdateAvailableDialog")
        UpdateAvailableDialog.resize(411, 83)
        self.verticalLayout = QtWidgets.QVBoxLayout(UpdateAvailableDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(UpdateAvailableDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.checkBox = QtWidgets.QCheckBox(UpdateAvailableDialog)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout.addWidget(self.checkBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(UpdateAvailableDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.No|QtWidgets.QDialogButtonBox.Yes)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(UpdateAvailableDialog)
        self.buttonBox.accepted.connect(UpdateAvailableDialog.accept)
        self.buttonBox.rejected.connect(UpdateAvailableDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(UpdateAvailableDialog)

    def retranslateUi(self, UpdateAvailableDialog):
        _translate = QtCore.QCoreApplication.translate
        UpdateAvailableDialog.setWindowTitle(_translate("UpdateAvailableDialog", "Update available"))
        self.label.setText(_translate("UpdateAvailableDialog", "<html><head/><body><p><span style=\" font-weight:600;\">A new version of this software is available. Would you like to update?</span></p></body></html>"))
        self.checkBox.setText(_translate("UpdateAvailableDialog", "Don\'t ask again for this version"))

