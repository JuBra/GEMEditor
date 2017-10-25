# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\MetaboliteDisplayWidget.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(168, 107)
        self.formLayout = QtWidgets.QFormLayout(Form)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_id = QtWidgets.QLabel(Form)
        self.label_id.setText("")
        self.label_id.setObjectName("label_id")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.label_id)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.label_names = QtWidgets.QLabel(Form)
        self.label_names.setText("")
        self.label_names.setWordWrap(True)
        self.label_names.setObjectName("label_names")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.label_names)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.label_formula = QtWidgets.QLabel(Form)
        self.label_formula.setText("")
        self.label_formula.setObjectName("label_formula")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.label_formula)
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.label_charge = QtWidgets.QLabel(Form)
        self.label_charge.setText("")
        self.label_charge.setObjectName("label_charge")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.label_charge)
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.label_compartment = QtWidgets.QLabel(Form)
        self.label_compartment.setText("")
        self.label_compartment.setObjectName("label_compartment")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.label_compartment)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "ID:"))
        self.label_2.setText(_translate("Form", "Names:"))
        self.label_3.setText(_translate("Form", "Formula:"))
        self.label_4.setText(_translate("Form", "Charge:"))
        self.label_5.setText(_translate("Form", "Compartment:"))

