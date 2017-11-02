# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\AnalysesTab.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AnalysisTab(object):
    def setupUi(self, AnalysisTab):
        AnalysisTab.setObjectName("AnalysisTab")
        AnalysisTab.resize(269, 481)
        self.horizontalLayout = QtWidgets.QHBoxLayout(AnalysisTab)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(AnalysisTab)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(AnalysisTab)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.combo_analysis = QtWidgets.QComboBox(AnalysisTab)
        self.combo_analysis.setObjectName("combo_analysis")
        self.combo_analysis.addItem("")
        self.gridLayout.addWidget(self.combo_analysis, 0, 1, 1, 1)
        self.combo_solver = QtWidgets.QComboBox(AnalysisTab)
        self.combo_solver.setObjectName("combo_solver")
        self.combo_solver.addItem("")
        self.gridLayout.addWidget(self.combo_solver, 1, 1, 1, 1)
        self.button_run = QtWidgets.QPushButton(AnalysisTab)
        self.button_run.setObjectName("button_run")
        self.gridLayout.addWidget(self.button_run, 2, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 30, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem1, 3, 1, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(AnalysisTab)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.list_solutions = QtWidgets.QListWidget(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_solutions.sizePolicy().hasHeightForWidth())
        self.list_solutions.setSizePolicy(sizePolicy)
        self.list_solutions.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.list_solutions.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.list_solutions.setObjectName("list_solutions")
        self.verticalLayout.addWidget(self.list_solutions)
        self.gridLayout.addWidget(self.groupBox, 4, 0, 1, 2)
        self.horizontalLayout.addLayout(self.gridLayout)
        spacerItem2 = QtWidgets.QSpacerItem(152, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)

        self.retranslateUi(AnalysisTab)
        QtCore.QMetaObject.connectSlotsByName(AnalysisTab)

    def retranslateUi(self, AnalysisTab):
        _translate = QtCore.QCoreApplication.translate
        AnalysisTab.setWindowTitle(_translate("AnalysisTab", "Form"))
        self.label.setText(_translate("AnalysisTab", "Analysis:"))
        self.label_2.setText(_translate("AnalysisTab", "Solver:"))
        self.combo_analysis.setItemText(0, _translate("AnalysisTab", "-- Select Analysis --"))
        self.combo_solver.setItemText(0, _translate("AnalysisTab", "-- Select Solver --"))
        self.button_run.setText(_translate("AnalysisTab", "Run"))
        self.groupBox.setTitle(_translate("AnalysisTab", "Solutions"))

