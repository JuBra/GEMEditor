# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\SolutionTableWidget.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SolutionTableWidget(object):
    def setupUi(self, SolutionTableWidget):
        SolutionTableWidget.setObjectName("SolutionTableWidget")
        SolutionTableWidget.resize(248, 78)
        self.horizontalLayout = QtWidgets.QHBoxLayout(SolutionTableWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(SolutionTableWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_status = QtWidgets.QLabel(SolutionTableWidget)
        self.label_status.setText("")
        self.label_status.setObjectName("label_status")
        self.gridLayout.addWidget(self.label_status, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(SolutionTableWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_objective = QtWidgets.QLabel(SolutionTableWidget)
        self.label_objective.setText("")
        self.label_objective.setObjectName("label_objective")
        self.gridLayout.addWidget(self.label_objective, 1, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setRowStretch(2, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.button_open_solution = QtWidgets.QPushButton(SolutionTableWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_open_solution.sizePolicy().hasHeightForWidth())
        self.button_open_solution.setSizePolicy(sizePolicy)
        self.button_open_solution.setObjectName("button_open_solution")
        self.verticalLayout.addWidget(self.button_open_solution)
        self.button_open_map = QtWidgets.QPushButton(SolutionTableWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_open_map.sizePolicy().hasHeightForWidth())
        self.button_open_map.setSizePolicy(sizePolicy)
        self.button_open_map.setObjectName("button_open_map")
        self.verticalLayout.addWidget(self.button_open_map)
        spacerItem1 = QtWidgets.QSpacerItem(0, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(SolutionTableWidget)
        QtCore.QMetaObject.connectSlotsByName(SolutionTableWidget)

    def retranslateUi(self, SolutionTableWidget):
        _translate = QtCore.QCoreApplication.translate
        SolutionTableWidget.setWindowTitle(_translate("SolutionTableWidget", "Form"))
        self.label.setText(_translate("SolutionTableWidget", "Status:"))
        self.label_2.setText(_translate("SolutionTableWidget", "Objective value:"))
        self.button_open_solution.setText(_translate("SolutionTableWidget", "Open"))
        self.button_open_map.setText(_translate("SolutionTableWidget", "Map"))

