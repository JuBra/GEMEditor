# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SetFluxvalueDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SetFluxValueDialog(object):
    def setupUi(self, SetFluxValueDialog):
        SetFluxValueDialog.setObjectName("SetFluxValueDialog")
        SetFluxValueDialog.resize(279, 97)
        self.verticalLayout = QtWidgets.QVBoxLayout(SetFluxValueDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.fluxValueLabel = QtWidgets.QLabel(SetFluxValueDialog)
        self.fluxValueLabel.setObjectName("fluxValueLabel")
        self.horizontalLayout_2.addWidget(self.fluxValueLabel)
        self.fluxValueDoubleSpinBox = QtWidgets.QDoubleSpinBox(SetFluxValueDialog)
        self.fluxValueDoubleSpinBox.setMinimum(-1000.0)
        self.fluxValueDoubleSpinBox.setMaximum(1000.0)
        self.fluxValueDoubleSpinBox.setObjectName("fluxValueDoubleSpinBox")
        self.horizontalLayout_2.addWidget(self.fluxValueDoubleSpinBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.checkBox = QtWidgets.QCheckBox(SetFluxValueDialog)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout.addWidget(self.checkBox)
        self.deviationInput = QtWidgets.QSpinBox(SetFluxValueDialog)
        self.deviationInput.setWhatsThis("")
        self.deviationInput.setPrefix("")
        self.deviationInput.setProperty("value", 1)
        self.deviationInput.setObjectName("deviationInput")
        self.horizontalLayout.addWidget(self.deviationInput)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(SetFluxValueDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SetFluxValueDialog)
        self.buttonBox.accepted.connect(SetFluxValueDialog.accept)
        self.buttonBox.rejected.connect(SetFluxValueDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SetFluxValueDialog)

    def retranslateUi(self, SetFluxValueDialog):
        _translate = QtCore.QCoreApplication.translate
        SetFluxValueDialog.setWindowTitle(_translate("SetFluxValueDialog", "Set flux value"))
        self.fluxValueLabel.setText(_translate("SetFluxValueDialog", "Flux value:"))
        self.checkBox.setText(_translate("SetFluxValueDialog", "Set flux to a range with a deviation of"))
        self.deviationInput.setSuffix(_translate("SetFluxValueDialog", "%"))

