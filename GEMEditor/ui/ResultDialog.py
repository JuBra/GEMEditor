# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ResultDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(432, 330)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label_filter = QtWidgets.QLabel(Dialog)
        self.label_filter.setObjectName("label_filter")
        self.horizontalLayout.addWidget(self.label_filter)
        self.filterComboBox = QtWidgets.QComboBox(Dialog)
        self.filterComboBox.setObjectName("filterComboBox")
        self.horizontalLayout.addWidget(self.filterComboBox)
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setMinimumSize(QtCore.QSize(15, 15))
        self.label.setMaximumSize(QtCore.QSize(15, 15))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/search_icon"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.searchInput = ButtonLineEdit(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.searchInput.sizePolicy().hasHeightForWidth())
        self.searchInput.setSizePolicy(sizePolicy)
        self.searchInput.setObjectName("searchInput")
        self.horizontalLayout.addWidget(self.searchInput)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.dataView = ProxyElementTableView(Dialog)
        self.dataView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.dataView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.dataView.setSortingEnabled(True)
        self.dataView.setObjectName("dataView")
        self.dataView.horizontalHeader().setVisible(True)
        self.dataView.verticalHeader().setVisible(False)
        self.dataView.verticalHeader().setHighlightSections(False)
        self.verticalLayout.addWidget(self.dataView)

        self.retranslateUi(Dialog)
        Dialog.finished['int'].connect(Dialog.save_dialog_geometry)
        Dialog.finished['int'].connect(Dialog.save_header_state)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_filter.setText(_translate("Dialog", "Filter:"))

from GEMEditor.widgets.gui import ButtonLineEdit
from GEMEditor.widgets.views import ProxyElementTableView
from GEMEditor.icons_rc import *
