# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\EditSettingsDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_EditSettingsDialog(object):
    def setupUi(self, EditSettingsDialog):
        EditSettingsDialog.setObjectName("EditSettingsDialog")
        EditSettingsDialog.resize(432, 107)
        self.verticalLayout = QtWidgets.QVBoxLayout(EditSettingsDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.eMailLabel = QtWidgets.QLabel(EditSettingsDialog)
        self.eMailLabel.setObjectName("eMailLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.eMailLabel)
        self.eMailLineEdit = QtWidgets.QLineEdit(EditSettingsDialog)
        self.eMailLineEdit.setObjectName("eMailLineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.eMailLineEdit)
        self.debugModeLabel = QtWidgets.QLabel(EditSettingsDialog)
        self.debugModeLabel.setObjectName("debugModeLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.debugModeLabel)
        self.debugModeCheckBox = QtWidgets.QCheckBox(EditSettingsDialog)
        self.debugModeCheckBox.setObjectName("debugModeCheckBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.debugModeCheckBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.label = QtWidgets.QLabel(EditSettingsDialog)
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.buttonBox = QtWidgets.QDialogButtonBox(EditSettingsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(EditSettingsDialog)
        self.buttonBox.accepted.connect(EditSettingsDialog.accept)
        self.buttonBox.rejected.connect(EditSettingsDialog.reject)
        self.eMailLineEdit.textEdited['QString'].connect(EditSettingsDialog.toggle_ok_button)
        EditSettingsDialog.accepted.connect(EditSettingsDialog.save_settings)
        QtCore.QMetaObject.connectSlotsByName(EditSettingsDialog)

    def retranslateUi(self, EditSettingsDialog):
        _translate = QtCore.QCoreApplication.translate
        EditSettingsDialog.setWindowTitle(_translate("EditSettingsDialog", "Edit settings"))
        self.eMailLabel.setText(_translate("EditSettingsDialog", "E-mail:"))
        self.debugModeLabel.setText(_translate("EditSettingsDialog", "Debug mode:"))
        self.label.setText(_translate("EditSettingsDialog", "<html><head/><body><p><span style=\" font-style:italic;\">Note: Your E-mail addresse is only used to download reference information from NCBI.</span></p></body></html>"))

