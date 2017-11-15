# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ManualMetaboliteMatchDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ManualMatchDialog(object):
    def setupUi(self, ManualMatchDialog):
        ManualMatchDialog.setObjectName("ManualMatchDialog")
        ManualMatchDialog.resize(487, 428)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(ManualMatchDialog)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupBox_model = QtWidgets.QGroupBox(ManualMatchDialog)
        self.groupBox_model.setObjectName("groupBox_model")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_model)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.display_model_metabolite = MetaboliteDisplayWidget(self.groupBox_model)
        self.display_model_metabolite.setObjectName("display_model_metabolite")
        self.verticalLayout_3.addWidget(self.display_model_metabolite)
        self.horizontalLayout_2.addWidget(self.groupBox_model)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox_database = QtWidgets.QGroupBox(ManualMatchDialog)
        self.groupBox_database.setObjectName("groupBox_database")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_database)
        self.verticalLayout.setObjectName("verticalLayout")
        self.stackedWidget_database = QtWidgets.QStackedWidget(self.groupBox_database)
        self.stackedWidget_database.setObjectName("stackedWidget_database")
        self.verticalLayout.addWidget(self.stackedWidget_database)
        self.label = QtWidgets.QLabel(self.groupBox_database)
        self.label.setText("")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.verticalLayout_2.addWidget(self.groupBox_database)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.button_previous_entry = QtWidgets.QPushButton(ManualMatchDialog)
        self.button_previous_entry.setObjectName("button_previous_entry")
        self.horizontalLayout.addWidget(self.button_previous_entry)
        self.button_select = QtWidgets.QPushButton(ManualMatchDialog)
        self.button_select.setObjectName("button_select")
        self.horizontalLayout.addWidget(self.button_select)
        self.button_next_entry = QtWidgets.QPushButton(ManualMatchDialog)
        self.button_next_entry.setObjectName("button_next_entry")
        self.horizontalLayout.addWidget(self.button_next_entry)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(ManualMatchDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_4.addWidget(self.buttonBox)

        self.retranslateUi(ManualMatchDialog)
        self.stackedWidget_database.setCurrentIndex(-1)
        self.buttonBox.accepted.connect(ManualMatchDialog.accept)
        self.buttonBox.rejected.connect(ManualMatchDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ManualMatchDialog)

    def retranslateUi(self, ManualMatchDialog):
        _translate = QtCore.QCoreApplication.translate
        ManualMatchDialog.setWindowTitle(_translate("ManualMatchDialog", "Match metabolite"))
        self.groupBox_model.setTitle(_translate("ManualMatchDialog", "Model metabolite"))
        self.groupBox_database.setTitle(_translate("ManualMatchDialog", "Database entry"))
        self.button_previous_entry.setText(_translate("ManualMatchDialog", "previous"))
        self.button_select.setText(_translate("ManualMatchDialog", "select"))
        self.button_next_entry.setText(_translate("ManualMatchDialog", "next"))


from GEMEditor.model.display.reaction import MetaboliteDisplayWidget
