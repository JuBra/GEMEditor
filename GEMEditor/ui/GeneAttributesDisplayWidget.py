# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GeneAttributesDisplayWidget.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(232, 97)
        self.formLayout = QtWidgets.QFormLayout(Form)
        self.formLayout.setObjectName("formLayout")
        self.iDLabel = QtWidgets.QLabel(Form)
        self.iDLabel.setObjectName("iDLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.iDLabel)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.iDLineEdit = QtWidgets.QLineEdit(Form)
        self.iDLineEdit.setObjectName("iDLineEdit")
        self.horizontalLayout.addWidget(self.iDLineEdit)
        self.labelIdStatus = QtWidgets.QLabel(Form)
        self.labelIdStatus.setMaximumSize(QtCore.QSize(20, 20))
        self.labelIdStatus.setStyleSheet("padding: 1;")
        self.labelIdStatus.setText("")
        self.labelIdStatus.setPixmap(QtGui.QPixmap(":/status_error"))
        self.labelIdStatus.setScaledContents(True)
        self.labelIdStatus.setObjectName("labelIdStatus")
        self.horizontalLayout.addWidget(self.labelIdStatus)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.nameLabel = QtWidgets.QLabel(Form)
        self.nameLabel.setObjectName("nameLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(Form)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.nameLineEdit)
        self.genomeLabel = QtWidgets.QLabel(Form)
        self.genomeLabel.setObjectName("genomeLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.genomeLabel)
        self.genomeLineEdit = QtWidgets.QLineEdit(Form)
        self.genomeLineEdit.setObjectName("genomeLineEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.genomeLineEdit)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.iDLabel.setText(_translate("Form", "ID:"))
        self.nameLabel.setText(_translate("Form", "Name:"))
        self.genomeLabel.setText(_translate("Form", "Genome:"))

from GEMEditor.icons_rc import *
