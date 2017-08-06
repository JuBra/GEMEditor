# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AnalysesTab.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(651, 485)
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setGeometry(QtCore.QRect(70, 50, 211, 171))
        self.groupBox.setObjectName("groupBox")
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        self.comboBox.setGeometry(QtCore.QRect(120, 30, 69, 22))
        self.comboBox.setObjectName("comboBox")
        self.comboBox_2 = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_2.setGeometry(QtCore.QRect(120, 70, 69, 22))
        self.comboBox_2.setObjectName("comboBox_2")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(30, 30, 47, 13))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(30, 70, 47, 13))
        self.label_2.setObjectName("label_2")
        self.pushButton = QtWidgets.QPushButton(self.groupBox)
        self.pushButton.setGeometry(QtCore.QRect(110, 120, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.line = QtWidgets.QFrame(self.groupBox)
        self.line.setGeometry(QtCore.QRect(30, 110, 118, 3))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        self.groupBox_2.setGeometry(QtCore.QRect(70, 240, 211, 191))
        self.groupBox_2.setObjectName("groupBox_2")
        self.checkBox = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkBox.setGeometry(QtCore.QRect(20, 30, 161, 17))
        self.checkBox.setObjectName("checkBox")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupBox.setTitle(_translate("Form", "Analyses"))
        self.label.setText(_translate("Form", "Type:"))
        self.label_2.setText(_translate("Form", "Solver:"))
        self.pushButton.setText(_translate("Form", "Run"))
        self.groupBox_2.setTitle(_translate("Form", "Quality checks"))
        self.checkBox.setText(_translate("Form", "Metabolite production"))

