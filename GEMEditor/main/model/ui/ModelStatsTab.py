# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\model_stats_tab.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_model_stats_tab(object):
    def setupUi(self, model_stats_tab):
        model_stats_tab.setObjectName("model_stats_tab")
        model_stats_tab.resize(565, 280)
        self.horizontalLayout = QtWidgets.QHBoxLayout(model_stats_tab)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.modelInfoWidget = ModelDisplayWidget(model_stats_tab)
        self.modelInfoWidget.setObjectName("modelInfoWidget")
        self.verticalLayout.addWidget(self.modelInfoWidget)
        self.modelAnnotationWidget = ModelAnnotationDisplayWidget(model_stats_tab)
        self.modelAnnotationWidget.setObjectName("modelAnnotationWidget")
        self.verticalLayout.addWidget(self.modelAnnotationWidget)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.editModelSettingButton = QtWidgets.QPushButton(model_stats_tab)
        self.editModelSettingButton.setObjectName("editModelSettingButton")
        self.verticalLayout_2.addWidget(self.editModelSettingButton)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)

        self.retranslateUi(model_stats_tab)
        QtCore.QMetaObject.connectSlotsByName(model_stats_tab)

    def retranslateUi(self, model_stats_tab):
        _translate = QtCore.QCoreApplication.translate
        model_stats_tab.setWindowTitle(_translate("model_stats_tab", "Form"))
        self.editModelSettingButton.setText(_translate("model_stats_tab", "Edit Model"))

from GEMEditor.widgets.model import ModelAnnotationDisplayWidget, ModelDisplayWidget
