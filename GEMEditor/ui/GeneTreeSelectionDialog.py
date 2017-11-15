# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GeneTreeSelectionDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets

class Ui_GeneTreeSelection(object):
    def setupUi(self, GeneTreeSelection):
        GeneTreeSelection.setObjectName("GeneTreeSelection")
        GeneTreeSelection.resize(344, 281)
        self.verticalLayout = QtWidgets.QVBoxLayout(GeneTreeSelection)
        self.verticalLayout.setObjectName("verticalLayout")
        self.treeView = GeneTreeView(GeneTreeSelection)
        self.treeView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.treeView.setProperty("showDropIndicator", False)
        self.treeView.setHeaderHidden(True)
        self.treeView.setObjectName("treeView")
        self.treeView.header().setVisible(False)
        self.verticalLayout.addWidget(self.treeView)
        self.buttonBox = QtWidgets.QDialogButtonBox(GeneTreeSelection)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(GeneTreeSelection)
        self.buttonBox.accepted.connect(GeneTreeSelection.accept)
        self.buttonBox.rejected.connect(GeneTreeSelection.reject)
        QtCore.QMetaObject.connectSlotsByName(GeneTreeSelection)

    def retranslateUi(self, GeneTreeSelection):
        _translate = QtCore.QCoreApplication.translate
        GeneTreeSelection.setWindowTitle(_translate("GeneTreeSelection", "Dialog"))

from GEMEditor.base.views import GeneTreeView
