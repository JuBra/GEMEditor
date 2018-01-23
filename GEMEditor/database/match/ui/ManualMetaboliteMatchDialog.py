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
        ManualMatchDialog.resize(537, 466)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(ManualMatchDialog)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.splitter = QtWidgets.QSplitter(ManualMatchDialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.groupBox_model = QtWidgets.QGroupBox(self.splitter)
        self.groupBox_model.setObjectName("groupBox_model")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_model)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.display_model_metabolite = MetaboliteDisplayWidget(self.groupBox_model)
        self.display_model_metabolite.setObjectName("display_model_metabolite")
        self.verticalLayout_3.addWidget(self.display_model_metabolite)
        self.widget = QtWidgets.QWidget(self.splitter)
        self.widget.setObjectName("widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox_database = QtWidgets.QGroupBox(self.widget)
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
        self.button_previous_entry = QtWidgets.QPushButton(self.widget)
        self.button_previous_entry.setObjectName("button_previous_entry")
        self.horizontalLayout.addWidget(self.button_previous_entry)
        self.button_select = QtWidgets.QPushButton(self.widget)
        self.button_select.setObjectName("button_select")
        self.horizontalLayout.addWidget(self.button_select)
        self.button_next_entry = QtWidgets.QPushButton(self.widget)
        self.button_next_entry.setObjectName("button_next_entry")
        self.horizontalLayout.addWidget(self.button_next_entry)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout_4.addWidget(self.splitter)
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
