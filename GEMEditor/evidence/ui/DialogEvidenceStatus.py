# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\DialogEvidenceStatus.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DialogEvidenceStatus(object):
    def setupUi(self, DialogEvidenceStatus):
        DialogEvidenceStatus.setObjectName("DialogEvidenceStatus")
        DialogEvidenceStatus.resize(302, 255)
        self.verticalLayout = QtWidgets.QVBoxLayout(DialogEvidenceStatus)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(DialogEvidenceStatus)
        self.tabWidget.setObjectName("tabWidget")
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(DialogEvidenceStatus)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DialogEvidenceStatus)
        self.tabWidget.setCurrentIndex(-1)
        self.buttonBox.accepted.connect(DialogEvidenceStatus.accept)
        self.buttonBox.rejected.connect(DialogEvidenceStatus.reject)
        QtCore.QMetaObject.connectSlotsByName(DialogEvidenceStatus)

    def retranslateUi(self, DialogEvidenceStatus):
        _translate = QtCore.QCoreApplication.translate
        DialogEvidenceStatus.setWindowTitle(_translate("DialogEvidenceStatus", "Evidences"))
