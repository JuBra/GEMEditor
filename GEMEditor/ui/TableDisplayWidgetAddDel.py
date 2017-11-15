# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TableDisplayWidgetAddDel.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TableDisplayWidgetAddDel(object):
    def setupUi(self, TableDisplayWidgetAddDel):
        TableDisplayWidgetAddDel.setObjectName("TableDisplayWidgetAddDel")
        TableDisplayWidgetAddDel.resize(251, 167)
        TableDisplayWidgetAddDel.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.horizontalLayout = QtWidgets.QHBoxLayout(TableDisplayWidgetAddDel)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.dataView = ElementTableView(TableDisplayWidgetAddDel)
        self.dataView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.dataView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.dataView.setObjectName("dataView")
        self.dataView.horizontalHeader().setStretchLastSection(True)
        self.dataView.verticalHeader().setVisible(False)
        self.horizontalLayout.addWidget(self.dataView)
        self.buttonLayout = QtWidgets.QVBoxLayout()
        self.buttonLayout.setObjectName("buttonLayout")
        self.add_button = QtWidgets.QPushButton(TableDisplayWidgetAddDel)
        self.add_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/add_icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_button.setIcon(icon)
        self.add_button.setObjectName("add_button")
        self.buttonLayout.addWidget(self.add_button)
        self.delete_button = QtWidgets.QPushButton(TableDisplayWidgetAddDel)
        self.delete_button.setEnabled(False)
        self.delete_button.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/remove_icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.delete_button.setIcon(icon1)
        self.delete_button.setObjectName("delete_button")
        self.buttonLayout.addWidget(self.delete_button)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.buttonLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.buttonLayout)

        self.retranslateUi(TableDisplayWidgetAddDel)
        self.add_button.clicked.connect(TableDisplayWidgetAddDel.add_item)
        self.dataView.doubleClicked['QModelIndex'].connect(TableDisplayWidgetAddDel.edit_item)
        self.dataView.customContextMenuRequested['QPoint'].connect(TableDisplayWidgetAddDel.showContextMenu)
        self.delete_button.clicked.connect(TableDisplayWidgetAddDel.delete_item)
        QtCore.QMetaObject.connectSlotsByName(TableDisplayWidgetAddDel)

    def retranslateUi(self, TableDisplayWidgetAddDel):
        _translate = QtCore.QCoreApplication.translate
        TableDisplayWidgetAddDel.setWindowTitle(_translate("TableDisplayWidgetAddDel", "Form"))

from GEMEditor.base.views import ElementTableView
