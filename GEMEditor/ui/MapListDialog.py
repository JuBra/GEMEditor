# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MapListDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MapListDialog(object):
    def setupUi(self, MapListDialog):
        MapListDialog.setObjectName("MapListDialog")
        MapListDialog.resize(432, 311)
        self.verticalLayout = QtWidgets.QVBoxLayout(MapListDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.listWidget = QtWidgets.QListWidget(MapListDialog)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.addButton = QtWidgets.QPushButton(MapListDialog)
        self.addButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/add_icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addButton.setIcon(icon)
        self.addButton.setObjectName("addButton")
        self.horizontalLayout.addWidget(self.addButton)
        self.delButton = QtWidgets.QPushButton(MapListDialog)
        self.delButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/remove_icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.delButton.setIcon(icon1)
        self.delButton.setObjectName("delButton")
        self.horizontalLayout.addWidget(self.delButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(MapListDialog)
        QtCore.QMetaObject.connectSlotsByName(MapListDialog)

    def retranslateUi(self, MapListDialog):
        _translate = QtCore.QCoreApplication.translate
        MapListDialog.setWindowTitle(_translate("MapListDialog", "Maps"))

from GEMEditor.icons_rc import *
