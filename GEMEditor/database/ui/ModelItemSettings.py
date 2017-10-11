# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ModelItemSettings.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ItemSettingWidget(object):
    def setupUi(self, ItemSettingWidget):
        ItemSettingWidget.setObjectName("ItemSettingWidget")
        ItemSettingWidget.resize(194, 226)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(ItemSettingWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox_attributes = QtWidgets.QGroupBox(ItemSettingWidget)
        self.groupBox_attributes.setObjectName("groupBox_attributes")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_attributes)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.groupBox_attributes)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit_prefix = QtWidgets.QLineEdit(self.groupBox_attributes)
        self.lineEdit_prefix.setObjectName("lineEdit_prefix")
        self.horizontalLayout.addWidget(self.lineEdit_prefix)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.checkBox_use_name = QtWidgets.QCheckBox(self.groupBox_attributes)
        self.checkBox_use_name.setChecked(True)
        self.checkBox_use_name.setObjectName("checkBox_use_name")
        self.verticalLayout.addWidget(self.checkBox_use_name)
        self.checkBox_use_formula = QtWidgets.QCheckBox(self.groupBox_attributes)
        self.checkBox_use_formula.setChecked(True)
        self.checkBox_use_formula.setObjectName("checkBox_use_formula")
        self.verticalLayout.addWidget(self.checkBox_use_formula)
        self.verticalLayout_2.addWidget(self.groupBox_attributes)
        self.groupBox_annotation = QtWidgets.QGroupBox(ItemSettingWidget)
        self.groupBox_annotation.setObjectName("groupBox_annotation")
        self.verticalLayout_2.addWidget(self.groupBox_annotation)

        self.retranslateUi(ItemSettingWidget)
        QtCore.QMetaObject.connectSlotsByName(ItemSettingWidget)

    def retranslateUi(self, ItemSettingWidget):
        _translate = QtCore.QCoreApplication.translate
        ItemSettingWidget.setWindowTitle(_translate("ItemSettingWidget", "Form"))
        self.groupBox_attributes.setTitle(_translate("ItemSettingWidget", "Attributes"))
        self.label.setText(_translate("ItemSettingWidget", "Prefix:"))
        self.checkBox_use_name.setText(_translate("ItemSettingWidget", "Use name"))
        self.checkBox_use_formula.setText(_translate("ItemSettingWidget", "Use formula and charge"))
        self.groupBox_annotation.setTitle(_translate("ItemSettingWidget", "Annotations"))

