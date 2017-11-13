# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AddCompartmentDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AddCompartmentDialog(object):
    def setupUi(self, AddCompartmentDialog):
        AddCompartmentDialog.setObjectName("AddCompartmentDialog")
        AddCompartmentDialog.resize(174, 95)
        self.verticalLayout = QtWidgets.QVBoxLayout(AddCompartmentDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.abbreviationLabel = QtWidgets.QLabel(AddCompartmentDialog)
        self.abbreviationLabel.setObjectName("abbreviationLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.abbreviationLabel)
        self.abbreviationInput = QtWidgets.QLineEdit(AddCompartmentDialog)
        self.abbreviationInput.setObjectName("abbreviationInput")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.abbreviationInput)
        self.nameLabel = QtWidgets.QLabel(AddCompartmentDialog)
        self.nameLabel.setObjectName("nameLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.nameLabel)
        self.nameInput = QtWidgets.QLineEdit(AddCompartmentDialog)
        self.nameInput.setObjectName("nameInput")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.nameInput)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(AddCompartmentDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AddCompartmentDialog)
        self.buttonBox.accepted.connect(AddCompartmentDialog.accept)
        self.buttonBox.rejected.connect(AddCompartmentDialog.reject)
        self.abbreviationInput.textChanged['QString'].connect(AddCompartmentDialog.activateButton)
        self.nameInput.textChanged['QString'].connect(AddCompartmentDialog.activateButton)
        QtCore.QMetaObject.connectSlotsByName(AddCompartmentDialog)

    def retranslateUi(self, AddCompartmentDialog):
        _translate = QtCore.QCoreApplication.translate
        AddCompartmentDialog.setWindowTitle(_translate("AddCompartmentDialog", "Dialog"))
        self.abbreviationLabel.setText(_translate("AddCompartmentDialog", "Abbreviation:"))
        self.nameLabel.setText(_translate("AddCompartmentDialog", "Name:"))

