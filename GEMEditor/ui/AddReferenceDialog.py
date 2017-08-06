# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AddReferenceDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(282, 193)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.referenceLabel = QtWidgets.QLabel(Dialog)
        self.referenceLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.referenceLabel.setObjectName("referenceLabel")
        self.gridLayout.addWidget(self.referenceLabel, 2, 0, 1, 1)
        self.partLabel = QtWidgets.QLabel(Dialog)
        self.partLabel.setObjectName("partLabel")
        self.gridLayout.addWidget(self.partLabel, 0, 0, 1, 1)
        self.partComboBox = QtWidgets.QComboBox(Dialog)
        self.partComboBox.setObjectName("partComboBox")
        self.gridLayout.addWidget(self.partComboBox, 0, 1, 1, 1)
        self.statusLabel = QtWidgets.QLabel(Dialog)
        self.statusLabel.setObjectName("statusLabel")
        self.gridLayout.addWidget(self.statusLabel, 1, 0, 1, 1)
        self.statusComboBox = QtWidgets.QComboBox(Dialog)
        self.statusComboBox.setObjectName("statusComboBox")
        self.gridLayout.addWidget(self.statusComboBox, 1, 1, 1, 1)
        self.tableWidget = QtWidgets.QTableWidget(Dialog)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.gridLayout.addWidget(self.tableWidget, 2, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.referenceLabel.setText(_translate("Dialog", "References:"))
        self.partLabel.setText(_translate("Dialog", "Part:"))
        self.statusLabel.setText(_translate("Dialog", "Status:"))

