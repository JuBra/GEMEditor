# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TreeViewDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Duplicates(object):
    def setupUi(self, Duplicates):
        Duplicates.setObjectName("Duplicates")
        Duplicates.resize(467, 362)
        self.verticalLayout = QtWidgets.QVBoxLayout(Duplicates)
        self.verticalLayout.setObjectName("verticalLayout")
        self.treeView = QtWidgets.QTreeView(Duplicates)
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.treeView.setHeaderHidden(False)
        self.treeView.setObjectName("treeView")
        self.treeView.header().setVisible(True)
        self.verticalLayout.addWidget(self.treeView)
        self.buttonBox = QtWidgets.QDialogButtonBox(Duplicates)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Duplicates)
        self.buttonBox.rejected.connect(Duplicates.reject)
        QtCore.QMetaObject.connectSlotsByName(Duplicates)

    def retranslateUi(self, Duplicates):
        _translate = QtCore.QCoreApplication.translate
        Duplicates.setWindowTitle(_translate("Duplicates", "Dialog"))

