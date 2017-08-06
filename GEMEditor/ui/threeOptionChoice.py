# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'threeOptionChoice.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_three_option_choice(object):
    def setupUi(self, three_option_choice):
        three_option_choice.setObjectName("three_option_choice")
        three_option_choice.setWindowModality(QtCore.Qt.NonModal)
        three_option_choice.resize(441, 234)
        three_option_choice.setModal(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(three_option_choice)
        self.verticalLayout.setObjectName("verticalLayout")
        self.buttonOption1 = QtWidgets.QPushButton(three_option_choice)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonOption1.sizePolicy().hasHeightForWidth())
        self.buttonOption1.setSizePolicy(sizePolicy)
        self.buttonOption1.setText("")
        self.buttonOption1.setObjectName("buttonOption1")
        self.verticalLayout.addWidget(self.buttonOption1)
        self.buttonOption2 = QtWidgets.QPushButton(three_option_choice)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonOption2.sizePolicy().hasHeightForWidth())
        self.buttonOption2.setSizePolicy(sizePolicy)
        self.buttonOption2.setText("")
        self.buttonOption2.setObjectName("buttonOption2")
        self.verticalLayout.addWidget(self.buttonOption2)
        self.buttonOption3 = QtWidgets.QPushButton(three_option_choice)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonOption3.sizePolicy().hasHeightForWidth())
        self.buttonOption3.setSizePolicy(sizePolicy)
        self.buttonOption3.setText("")
        self.buttonOption3.setObjectName("buttonOption3")
        self.verticalLayout.addWidget(self.buttonOption3)

        self.retranslateUi(three_option_choice)
        QtCore.QMetaObject.connectSlotsByName(three_option_choice)

    def retranslateUi(self, three_option_choice):
        _translate = QtCore.QCoreApplication.translate
        three_option_choice.setWindowTitle(_translate("three_option_choice", "Choose:"))

