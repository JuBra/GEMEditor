# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ModelTestTab.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ModelTestTab(object):
    def setupUi(self, ModelTestTab):
        ModelTestTab.setObjectName("ModelTestTab")
        ModelTestTab.resize(448, 366)
        self.verticalLayout = QtWidgets.QVBoxLayout(ModelTestTab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_status_description = QtWidgets.QLabel(ModelTestTab)
        self.label_status_description.setObjectName("label_status_description")
        self.horizontalLayout.addWidget(self.label_status_description)
        self.label_status = QtWidgets.QLabel(ModelTestTab)
        font = QtGui.QFont()
        font.setItalic(True)
        self.label_status.setFont(font)
        self.label_status.setObjectName("label_status")
        self.horizontalLayout.addWidget(self.label_status)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(ModelTestTab)
        self.label.setMinimumSize(QtCore.QSize(15, 15))
        self.label.setMaximumSize(QtCore.QSize(15, 15))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/search_icon"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.searchInput = ButtonLineEdit(ModelTestTab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.searchInput.sizePolicy().hasHeightForWidth())
        self.searchInput.setSizePolicy(sizePolicy)
        self.searchInput.setObjectName("searchInput")
        self.horizontalLayout.addWidget(self.searchInput)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.dataView = GeneTreeView(ModelTestTab)
        self.dataView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.dataView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.dataView.setObjectName("dataView")
        self.verticalLayout.addWidget(self.dataView)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.addItemButton = QtWidgets.QPushButton(ModelTestTab)
        self.addItemButton.setObjectName("addItemButton")
        self.horizontalLayout_2.addWidget(self.addItemButton)
        self.editItemButton = QtWidgets.QPushButton(ModelTestTab)
        self.editItemButton.setObjectName("editItemButton")
        self.horizontalLayout_2.addWidget(self.editItemButton)
        self.deleteItemButton = QtWidgets.QPushButton(ModelTestTab)
        self.deleteItemButton.setObjectName("deleteItemButton")
        self.horizontalLayout_2.addWidget(self.deleteItemButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(ModelTestTab)
        self.addItemButton.clicked.connect(ModelTestTab.addItemSlot)
        self.editItemButton.clicked.connect(ModelTestTab.editItemSlot)
        self.deleteItemButton.clicked.connect(ModelTestTab.deleteItemSlot)
        QtCore.QMetaObject.connectSlotsByName(ModelTestTab)

    def retranslateUi(self, ModelTestTab):
        _translate = QtCore.QCoreApplication.translate
        ModelTestTab.setWindowTitle(_translate("ModelTestTab", "Form"))
        self.label_status_description.setText(_translate("ModelTestTab", "Status:"))
        self.label_status.setText(_translate("ModelTestTab", "Unknown"))
        self.addItemButton.setText(_translate("ModelTestTab", "Add Test"))
        self.editItemButton.setText(_translate("ModelTestTab", "Edit Test"))
        self.deleteItemButton.setText(_translate("ModelTestTab", "Delete Test"))

from GEMEditor.widgets.gui import ButtonLineEdit
from GEMEditor.widgets.views import GeneTreeView
from GEMEditor.icons_rc import *
