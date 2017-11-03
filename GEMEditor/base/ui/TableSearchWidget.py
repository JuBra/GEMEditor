# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\TableSearchWidget.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_StandardTab(object):
    def setupUi(self, StandardTab):
        StandardTab.setObjectName("StandardTab")
        StandardTab.resize(298, 40)
        self.verticalLayout = QtWidgets.QVBoxLayout(StandardTab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label_filter = QtWidgets.QLabel(StandardTab)
        self.label_filter.setObjectName("label_filter")
        self.horizontalLayout.addWidget(self.label_filter)
        self.filterComboBox = QtWidgets.QComboBox(StandardTab)
        self.filterComboBox.setObjectName("filterComboBox")
        self.horizontalLayout.addWidget(self.filterComboBox)
        self.line = QtWidgets.QFrame(StandardTab)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.label = QtWidgets.QLabel(StandardTab)
        self.label.setMinimumSize(QtCore.QSize(15, 15))
        self.label.setMaximumSize(QtCore.QSize(15, 15))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/search_icon"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.searchInput = QtWidgets.QLineEdit(StandardTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.searchInput.sizePolicy().hasHeightForWidth())
        self.searchInput.setSizePolicy(sizePolicy)
        self.searchInput.setClearButtonEnabled(True)
        self.searchInput.setObjectName("searchInput")
        self.horizontalLayout.addWidget(self.searchInput)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(StandardTab)
        QtCore.QMetaObject.connectSlotsByName(StandardTab)

    def retranslateUi(self, StandardTab):
        _translate = QtCore.QCoreApplication.translate
        StandardTab.setWindowTitle(_translate("StandardTab", "Form"))
        self.label_filter.setText(_translate("StandardTab", "Filter:"))
        self.searchInput.setPlaceholderText(_translate("StandardTab", "Search.."))

