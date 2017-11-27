# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\DataFrameDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DataFrameDialog(object):
    def setupUi(self, DataFrameDialog):
        DataFrameDialog.setObjectName("DataFrameDialog")
        DataFrameDialog.resize(346, 250)
        self.verticalLayout = QtWidgets.QVBoxLayout(DataFrameDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableView = QtWidgets.QTableView(DataFrameDialog)
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableView.setSortingEnabled(True)
        self.tableView.setObjectName("tableView")
        self.verticalLayout.addWidget(self.tableView)
        self.buttonBox = QtWidgets.QDialogButtonBox(DataFrameDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DataFrameDialog)
        self.buttonBox.accepted.connect(DataFrameDialog.accept)
        self.buttonBox.rejected.connect(DataFrameDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(DataFrameDialog)

    def retranslateUi(self, DataFrameDialog):
        _translate = QtCore.QCoreApplication.translate
        DataFrameDialog.setWindowTitle(_translate("DataFrameDialog", "Dialog"))

