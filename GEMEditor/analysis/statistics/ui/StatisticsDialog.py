# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\src\StatisticsDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_StatisticsDialog(object):
    def setupUi(self, StatisticsDialog):
        StatisticsDialog.setObjectName("StatisticsDialog")
        StatisticsDialog.resize(400, 83)
        self.verticalLayout = QtWidgets.QVBoxLayout(StatisticsDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mainLayout = QtWidgets.QGridLayout()
        self.mainLayout.setObjectName("mainLayout")
        self.verticalLayout.addLayout(self.mainLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(StatisticsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(StatisticsDialog)
        self.buttonBox.accepted.connect(StatisticsDialog.accept)
        self.buttonBox.rejected.connect(StatisticsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(StatisticsDialog)

    def retranslateUi(self, StatisticsDialog):
        _translate = QtCore.QCoreApplication.translate
        StatisticsDialog.setWindowTitle(_translate("StatisticsDialog", "Dialog"))

