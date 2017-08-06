# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AddAuthorName.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AddAuthorName(object):
    def setupUi(self, AddAuthorName):
        AddAuthorName.setObjectName("AddAuthorName")
        AddAuthorName.resize(205, 121)
        self.verticalLayout = QtWidgets.QVBoxLayout(AddAuthorName)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.firstnameLabel = QtWidgets.QLabel(AddAuthorName)
        self.firstnameLabel.setObjectName("firstnameLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.firstnameLabel)
        self.firstnameLineEdit = QtWidgets.QLineEdit(AddAuthorName)
        self.firstnameLineEdit.setObjectName("firstnameLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.firstnameLineEdit)
        self.initialsLabel = QtWidgets.QLabel(AddAuthorName)
        self.initialsLabel.setObjectName("initialsLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.initialsLabel)
        self.initialsLineEdit = QtWidgets.QLineEdit(AddAuthorName)
        self.initialsLineEdit.setObjectName("initialsLineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.initialsLineEdit)
        self.lastnameLabel = QtWidgets.QLabel(AddAuthorName)
        self.lastnameLabel.setObjectName("lastnameLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.lastnameLabel)
        self.lastnameLineEdit = QtWidgets.QLineEdit(AddAuthorName)
        self.lastnameLineEdit.setObjectName("lastnameLineEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lastnameLineEdit)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(AddAuthorName)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AddAuthorName)
        self.buttonBox.accepted.connect(AddAuthorName.accept)
        self.buttonBox.rejected.connect(AddAuthorName.reject)
        QtCore.QMetaObject.connectSlotsByName(AddAuthorName)

    def retranslateUi(self, AddAuthorName):
        _translate = QtCore.QCoreApplication.translate
        AddAuthorName.setWindowTitle(_translate("AddAuthorName", "Add Author"))
        self.firstnameLabel.setText(_translate("AddAuthorName", "Firstname"))
        self.initialsLabel.setText(_translate("AddAuthorName", "Initials:"))
        self.lastnameLabel.setText(_translate("AddAuthorName", "Lastname"))

