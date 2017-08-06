# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ListDisplayDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ListDisplayDialog(object):
    def setupUi(self, ListDisplayDialog):
        ListDisplayDialog.setObjectName("ListDisplayDialog")
        ListDisplayDialog.resize(386, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(ListDisplayDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.infoLabel = QtWidgets.QLabel(ListDisplayDialog)
        self.infoLabel.setText("")
        self.infoLabel.setObjectName("infoLabel")
        self.verticalLayout.addWidget(self.infoLabel)
        self.listWidget = QtWidgets.QListWidget(ListDisplayDialog)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(ListDisplayDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ListDisplayDialog)
        self.buttonBox.accepted.connect(ListDisplayDialog.accept)
        self.buttonBox.rejected.connect(ListDisplayDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ListDisplayDialog)

    def retranslateUi(self, ListDisplayDialog):
        _translate = QtCore.QCoreApplication.translate
        ListDisplayDialog.setWindowTitle(_translate("ListDisplayDialog", "Dialog"))

