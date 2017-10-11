# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\EmptyDialogHorzButtons.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_EmptyDialogHorzButtons(object):
    def setupUi(self, EmptyDialogHorzButtons):
        EmptyDialogHorzButtons.setObjectName("EmptyDialogHorzButtons")
        EmptyDialogHorzButtons.resize(212, 70)
        self.buttonBox = QtWidgets.QDialogButtonBox(EmptyDialogHorzButtons)
        self.buttonBox.setGeometry(QtCore.QRect(20, 20, 171, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.retranslateUi(EmptyDialogHorzButtons)
        self.buttonBox.accepted.connect(EmptyDialogHorzButtons.accept)
        self.buttonBox.rejected.connect(EmptyDialogHorzButtons.reject)
        QtCore.QMetaObject.connectSlotsByName(EmptyDialogHorzButtons)

    def retranslateUi(self, EmptyDialogHorzButtons):
        _translate = QtCore.QCoreApplication.translate
        EmptyDialogHorzButtons.setWindowTitle(_translate("EmptyDialogHorzButtons", "Dialog"))

