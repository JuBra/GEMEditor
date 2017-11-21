# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\SelectionDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SelectionDialog(object):
    def setupUi(self, SelectionDialog):
        SelectionDialog.setObjectName("SelectionDialog")
        SelectionDialog.resize(475, 382)
        self.verticalLayout = QtWidgets.QVBoxLayout(SelectionDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(SelectionDialog)
        self.label.setMinimumSize(QtCore.QSize(15, 15))
        self.label.setMaximumSize(QtCore.QSize(15, 15))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/search_icon"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.searchInput = QtWidgets.QLineEdit(SelectionDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.searchInput.sizePolicy().hasHeightForWidth())
        self.searchInput.setSizePolicy(sizePolicy)
        self.searchInput.setClearButtonEnabled(True)
        self.searchInput.setObjectName("searchInput")
        self.horizontalLayout.addWidget(self.searchInput)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.dataView = ProxyElementTableView(SelectionDialog)
        self.dataView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.dataView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.dataView.setSortingEnabled(True)
        self.dataView.setObjectName("dataView")
        self.dataView.horizontalHeader().setVisible(True)
        self.dataView.verticalHeader().setVisible(False)
        self.dataView.verticalHeader().setHighlightSections(False)
        self.verticalLayout.addWidget(self.dataView)
        self.buttonBox = QtWidgets.QDialogButtonBox(SelectionDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SelectionDialog)
        self.buttonBox.accepted.connect(SelectionDialog.accept)
        self.buttonBox.rejected.connect(SelectionDialog.reject)
        SelectionDialog.finished['int'].connect(SelectionDialog.save_dialog_geometry)
        self.searchInput.textChanged['QString'].connect(SelectionDialog.update_filter)
        QtCore.QMetaObject.connectSlotsByName(SelectionDialog)

    def retranslateUi(self, SelectionDialog):
        _translate = QtCore.QCoreApplication.translate
        SelectionDialog.setWindowTitle(_translate("SelectionDialog", "Dialog"))
        self.searchInput.setPlaceholderText(_translate("SelectionDialog", "Search.."))

from GEMEditor.base.views import ProxyElementTableView

