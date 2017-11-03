# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\SolutionDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SolutionDialog(object):
    def setupUi(self, SolutionDialog):
        SolutionDialog.setObjectName("SolutionDialog")
        SolutionDialog.resize(356, 296)
        self.verticalLayout = QtWidgets.QVBoxLayout(SolutionDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(SolutionDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_status = QtWidgets.QLabel(SolutionDialog)
        self.label_status.setText("")
        self.label_status.setObjectName("label_status")
        self.gridLayout.addWidget(self.label_status, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 2, 1)
        self.label_3 = QtWidgets.QLabel(SolutionDialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.label_label_objective = QtWidgets.QLabel(SolutionDialog)
        self.label_label_objective.setText("")
        self.label_label_objective.setObjectName("label_label_objective")
        self.gridLayout.addWidget(self.label_label_objective, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.tabWidget = QtWidgets.QTabWidget(SolutionDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(SolutionDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SolutionDialog)
        self.buttonBox.accepted.connect(SolutionDialog.accept)
        self.buttonBox.rejected.connect(SolutionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SolutionDialog)

    def retranslateUi(self, SolutionDialog):
        _translate = QtCore.QCoreApplication.translate
        SolutionDialog.setWindowTitle(_translate("SolutionDialog", "Dialog"))
        self.label.setText(_translate("SolutionDialog", "Status"))
        self.label_3.setText(_translate("SolutionDialog", "Objective value:"))

