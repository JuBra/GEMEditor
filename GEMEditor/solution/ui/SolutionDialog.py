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
        SolutionDialog.resize(410, 366)
        self.verticalLayout = QtWidgets.QVBoxLayout(SolutionDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(SolutionDialog)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.label_objective_value = QtWidgets.QLabel(self.groupBox)
        self.label_objective_value.setText("")
        self.label_objective_value.setObjectName("label_objective_value")
        self.gridLayout.addWidget(self.label_objective_value, 1, 1, 1, 1)
        self.label_status_value = QtWidgets.QLabel(self.groupBox)
        self.label_status_value.setText("")
        self.label_status_value.setObjectName("label_status_value")
        self.gridLayout.addWidget(self.label_status_value, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.tabWidget = QtWidgets.QTabWidget(SolutionDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(SolutionDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SolutionDialog)
        self.tabWidget.setCurrentIndex(1)
        self.buttonBox.accepted.connect(SolutionDialog.accept)
        self.buttonBox.rejected.connect(SolutionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SolutionDialog)

    def retranslateUi(self, SolutionDialog):
        _translate = QtCore.QCoreApplication.translate
        SolutionDialog.setWindowTitle(_translate("SolutionDialog", "Solution"))
        self.groupBox.setTitle(_translate("SolutionDialog", "Info"))
        self.label_2.setText(_translate("SolutionDialog", "Objective value:"))
        self.label.setText(_translate("SolutionDialog", "Status:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("SolutionDialog", "Reactions"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("SolutionDialog", "Metabolites"))

