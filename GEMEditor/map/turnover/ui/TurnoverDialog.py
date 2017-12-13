# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\TurnoverDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TurnoverDialog(object):
    def setupUi(self, TurnoverDialog):
        TurnoverDialog.setObjectName("TurnoverDialog")
        TurnoverDialog.resize(149, 146)
        self.verticalLayout = QtWidgets.QVBoxLayout(TurnoverDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtWidgets.QSplitter(TurnoverDialog)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.mapView = QtWebEngineWidgets.QWebEngineView(self.splitter)
        self.mapView.setObjectName("mapView")
        self.dataView = QtWidgets.QTreeView(self.splitter)
        self.dataView.setObjectName("dataView")
        self.verticalLayout.addWidget(self.splitter)
        self.buttonBox = QtWidgets.QDialogButtonBox(TurnoverDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(TurnoverDialog)
        self.buttonBox.accepted.connect(TurnoverDialog.accept)
        self.buttonBox.rejected.connect(TurnoverDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(TurnoverDialog)

    def retranslateUi(self, TurnoverDialog):
        _translate = QtCore.QCoreApplication.translate
        TurnoverDialog.setWindowTitle(_translate("TurnoverDialog", "Dialog"))

from PyQt5 import QtWebEngineWidgets
