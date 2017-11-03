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
        EditSettingsDialog.resize(432, 144)
        self.verticalLayout = QtWidgets.QVBoxLayout(EditSettingsDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(EditSettingsDialog)
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
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
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.debugModeLabel)
        self.debugModeCheckBox = QtWidgets.QCheckBox(EditSettingsDialog)
        self.debugModeCheckBox.setObjectName("debugModeCheckBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.debugModeCheckBox)
        self.label_2 = QtWidgets.QLabel(EditSettingsDialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_database_path = QtWidgets.QLabel(EditSettingsDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_database_path.sizePolicy().hasHeightForWidth())
        self.label_database_path.setSizePolicy(sizePolicy)
        self.label_database_path.setText("")
        self.label_database_path.setObjectName("label_database_path")
        self.horizontalLayout.addWidget(self.label_database_path)
        self.pushButton_change_path = QtWidgets.QPushButton(EditSettingsDialog)
        self.pushButton_change_path.setObjectName("pushButton_change_path")
        self.horizontalLayout.addWidget(self.pushButton_change_path)
        self.formLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.verticalLayout.addLayout(self.formLayout)
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
        self.label.setText(_translate("EditSettingsDialog", "<html><head/><body><p><span style=\" font-style:italic;\">Note: Your E-mail addresse is only used to download reference information from NCBI.</span></p></body></html>"))
        self.eMailLabel.setText(_translate("EditSettingsDialog", "E-mail:"))
        self.debugModeLabel.setText(_translate("EditSettingsDialog", "Debug mode:"))
        self.label_2.setText(_translate("EditSettingsDialog", "Database path:"))
        self.pushButton_change_path.setText(_translate("EditSettingsDialog", "change"))

