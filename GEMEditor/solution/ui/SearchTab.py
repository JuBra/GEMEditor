# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\SearchTab.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SearchTab(object):
    def setupUi(self, SearchTab):
        SearchTab.setObjectName("SearchTab")
        SearchTab.resize(448, 366)
        self.verticalLayout = QtWidgets.QVBoxLayout(SearchTab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label_filter = QtWidgets.QLabel(SearchTab)
        self.label_filter.setObjectName("label_filter")
        self.horizontalLayout.addWidget(self.label_filter)
        self.filterComboBox = QtWidgets.QComboBox(SearchTab)
        self.filterComboBox.setObjectName("filterComboBox")
        self.horizontalLayout.addWidget(self.filterComboBox)
        self.line = QtWidgets.QFrame(SearchTab)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.label = QtWidgets.QLabel(SearchTab)
        self.label.setMinimumSize(QtCore.QSize(15, 15))
        self.label.setMaximumSize(QtCore.QSize(15, 15))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/search_icon"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.searchInput = QtWidgets.QLineEdit(SearchTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.searchInput.sizePolicy().hasHeightForWidth())
        self.searchInput.setSizePolicy(sizePolicy)
        self.searchInput.setClearButtonEnabled(True)
        self.searchInput.setObjectName("searchInput")
        self.horizontalLayout.addWidget(self.searchInput)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.dataView = QtWidgets.QTableView(SearchTab)
        self.dataView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.dataView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.dataView.setSortingEnabled(True)
        self.dataView.setObjectName("dataView")
        self.dataView.horizontalHeader().setVisible(True)
        self.dataView.verticalHeader().setVisible(False)
        self.dataView.verticalHeader().setHighlightSections(False)
        self.verticalLayout.addWidget(self.dataView)

        self.retranslateUi(SearchTab)
        QtCore.QMetaObject.connectSlotsByName(SearchTab)

    def retranslateUi(self, SearchTab):
        _translate = QtCore.QCoreApplication.translate
        SearchTab.setWindowTitle(_translate("SearchTab", "Form"))
        self.label_filter.setText(_translate("SearchTab", "Filter:"))
        self.searchInput.setPlaceholderText(_translate("SearchTab", "Search.."))
