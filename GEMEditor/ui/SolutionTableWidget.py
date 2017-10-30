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
        SolutionTableWidget.resize(242, 52)
        self.horizontalLayout = QtWidgets.QHBoxLayout(SolutionTableWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.button_open_solution_table = QtWidgets.QPushButton(SolutionTableWidget)
        self.button_open_solution_table.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/solution_table_icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_open_solution_table.setIcon(icon)
        self.button_open_solution_table.setIconSize(QtCore.QSize(18, 18))
        self.button_open_solution_table.setObjectName("button_open_solution_table")
        self.gridLayout.addWidget(self.button_open_solution_table, 0, 2, 2, 1)
        self.label = QtWidgets.QLabel(SolutionTableWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_status = QtWidgets.QLabel(SolutionTableWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_status.sizePolicy().hasHeightForWidth())
        self.label_status.setSizePolicy(sizePolicy)
        self.label_status.setText("")
        self.label_status.setObjectName("label_status")
        self.gridLayout.addWidget(self.label_status, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(SolutionTableWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_value = QtWidgets.QLabel(SolutionTableWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_value.sizePolicy().hasHeightForWidth())
        self.label_value.setSizePolicy(sizePolicy)
        self.label_value.setText("")
        self.label_value.setObjectName("label_value")
        self.gridLayout.addWidget(self.label_value, 1, 1, 1, 1)
        self.button_open_solution_map = QtWidgets.QPushButton(SolutionTableWidget)
        self.button_open_solution_map.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/solution_map_icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_open_solution_map.setIcon(icon1)
        self.button_open_solution_map.setIconSize(QtCore.QSize(18, 18))
        self.button_open_solution_map.setObjectName("button_open_solution_map")
        self.gridLayout.addWidget(self.button_open_solution_map, 0, 3, 2, 1)
        self.horizontalLayout.addLayout(self.gridLayout)

        self.retranslateUi(SolutionTableWidget)
        QtCore.QMetaObject.connectSlotsByName(SolutionTableWidget)

    def retranslateUi(self, SolutionTableWidget):
        _translate = QtCore.QCoreApplication.translate
        SolutionTableWidget.setWindowTitle(_translate("SolutionTableWidget", "Form"))
        self.button_open_solution_table.setStatusTip(_translate("SolutionTableWidget", "Open solution table"))
        self.button_open_solution_table.setWhatsThis(_translate("SolutionTableWidget", "Open solution table"))
        self.label.setText(_translate("SolutionTableWidget", "Status:"))
        self.label_2.setText(_translate("SolutionTableWidget", "Value:"))
        self.button_open_solution_map.setStatusTip(_translate("SolutionTableWidget", "Show solution on map"))
        self.button_open_solution_map.setWhatsThis(_translate("SolutionTableWidget", "Show solution on map"))

