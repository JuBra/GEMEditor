# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SettingDisplayWiget.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SettingsDisplayWidget(object):
    def setupUi(self, SettingsDisplayWidget):
        SettingsDisplayWidget.setObjectName("SettingsDisplayWidget")
        SettingsDisplayWidget.resize(276, 241)
        self.verticalLayout = QtWidgets.QVBoxLayout(SettingsDisplayWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableView = ElementTableView(SettingsDisplayWidget)
        self.tableView.setObjectName("tableView")
        self.tableView.horizontalHeader().setStretchLastSection(False)
        self.verticalLayout.addWidget(self.tableView)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.button_add_current = QtWidgets.QPushButton(SettingsDisplayWidget)
        self.button_add_current.setObjectName("button_add_current")
        self.horizontalLayout.addWidget(self.button_add_current)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.button_add_item = QtWidgets.QPushButton(SettingsDisplayWidget)
        self.button_add_item.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/add_icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_add_item.setIcon(icon)
        self.button_add_item.setObjectName("button_add_item")
        self.horizontalLayout.addWidget(self.button_add_item)
        self.button_del_item = QtWidgets.QPushButton(SettingsDisplayWidget)
        self.button_del_item.setEnabled(False)
        self.button_del_item.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/remove_icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_del_item.setIcon(icon1)
        self.button_del_item.setObjectName("button_del_item")
        self.horizontalLayout.addWidget(self.button_del_item)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(SettingsDisplayWidget)
        QtCore.QMetaObject.connectSlotsByName(SettingsDisplayWidget)

    def retranslateUi(self, SettingsDisplayWidget):
        _translate = QtCore.QCoreApplication.translate
        SettingsDisplayWidget.setWindowTitle(_translate("SettingsDisplayWidget", "Form"))
        self.button_add_current.setText(_translate("SettingsDisplayWidget", "Add current"))

from GEMEditor.widgets.views import ElementTableView
from GEMEditor.icons_rc import *
