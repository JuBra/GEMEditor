# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReactionAttributeDisplayWidget.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(302, 176)
        self.formLayout = QtWidgets.QFormLayout(Form)
        self.formLayout.setObjectName("formLayout")
        self.idLabel = QtWidgets.QLabel(Form)
        self.idLabel.setObjectName("idLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.idLabel)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.idLineEdit = QtWidgets.QLineEdit(Form)
        self.idLineEdit.setReadOnly(False)
        self.idLineEdit.setObjectName("idLineEdit")
        self.horizontalLayout.addWidget(self.idLineEdit)
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
        self.nameLineEdit.setReadOnly(False)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.nameLineEdit)
        self.subsystemLabel = QtWidgets.QLabel(Form)
        self.subsystemLabel.setObjectName("subsystemLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.subsystemLabel)
        self.subsystemLineEdit = QtWidgets.QLineEdit(Form)
        self.subsystemLineEdit.setReadOnly(False)
        self.subsystemLineEdit.setObjectName("subsystemLineEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.subsystemLineEdit)
        self.upperBoundLabel = QtWidgets.QLabel(Form)
        self.upperBoundLabel.setObjectName("upperBoundLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.upperBoundLabel)
        self.upperBoundInput = QtWidgets.QDoubleSpinBox(Form)
        self.upperBoundInput.setDecimals(2)
        self.upperBoundInput.setMinimum(-1000.0)
        self.upperBoundInput.setMaximum(1000.0)
        self.upperBoundInput.setObjectName("upperBoundInput")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.upperBoundInput)
        self.lowerBoundLabel = QtWidgets.QLabel(Form)
        self.lowerBoundLabel.setObjectName("lowerBoundLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.lowerBoundLabel)
        self.lowerBoundInput = QtWidgets.QDoubleSpinBox(Form)
        self.lowerBoundInput.setMinimum(-1000.0)
        self.lowerBoundInput.setMaximum(1000.0)
        self.lowerBoundInput.setObjectName("lowerBoundInput")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.lowerBoundInput)
        self.objectiveCoefficientLabel = QtWidgets.QLabel(Form)
        self.objectiveCoefficientLabel.setObjectName("objectiveCoefficientLabel")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.objectiveCoefficientLabel)
        self.objectiveCoefficientInput = QtWidgets.QDoubleSpinBox(Form)
        self.objectiveCoefficientInput.setMinimum(-100.0)
        self.objectiveCoefficientInput.setMaximum(100.0)
        self.objectiveCoefficientInput.setObjectName("objectiveCoefficientInput")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.objectiveCoefficientInput)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.idLabel.setText(_translate("Form", "ID:"))
        self.nameLabel.setText(_translate("Form", "Name:"))
        self.subsystemLabel.setText(_translate("Form", "Subsystem:"))
        self.upperBoundLabel.setText(_translate("Form", "Upper Bound:"))
        self.lowerBoundLabel.setText(_translate("Form", "Lower Bound:"))
        self.objectiveCoefficientLabel.setText(_translate("Form", "Objective coefficient"))

from GEMEditor.icons_rc import *
