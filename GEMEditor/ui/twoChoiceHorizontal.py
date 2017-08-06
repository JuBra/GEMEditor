# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'twoChoiceHorizontal.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_twoChoiceDialog(object):
    def setupUi(self, twoChoiceDialog):
        twoChoiceDialog.setObjectName("twoChoiceDialog")
        twoChoiceDialog.resize(437, 246)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(twoChoiceDialog.sizePolicy().hasHeightForWidth())
        twoChoiceDialog.setSizePolicy(sizePolicy)
        self.horizontalLayout = QtWidgets.QHBoxLayout(twoChoiceDialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.buttonLeftOption = QtWidgets.QPushButton(twoChoiceDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonLeftOption.sizePolicy().hasHeightForWidth())
        self.buttonLeftOption.setSizePolicy(sizePolicy)
        self.buttonLeftOption.setText("")
        self.buttonLeftOption.setFlat(True)
        self.buttonLeftOption.setObjectName("buttonLeftOption")
        self.horizontalLayout.addWidget(self.buttonLeftOption)
        self.buttonRightOption = QtWidgets.QPushButton(twoChoiceDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonRightOption.sizePolicy().hasHeightForWidth())
        self.buttonRightOption.setSizePolicy(sizePolicy)
        self.buttonRightOption.setText("")
        self.buttonRightOption.setFlat(True)
        self.buttonRightOption.setObjectName("buttonRightOption")
        self.horizontalLayout.addWidget(self.buttonRightOption)

        self.retranslateUi(twoChoiceDialog)
        QtCore.QMetaObject.connectSlotsByName(twoChoiceDialog)

    def retranslateUi(self, twoChoiceDialog):
        _translate = QtCore.QCoreApplication.translate
        twoChoiceDialog.setWindowTitle(_translate("twoChoiceDialog", "Form"))

