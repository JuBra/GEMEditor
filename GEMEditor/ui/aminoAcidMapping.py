# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'aminoAcidMapping.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_aminoAcidMapping(object):
    def setupUi(self, aminoAcidMapping):
        aminoAcidMapping.setObjectName("aminoAcidMapping")
        aminoAcidMapping.resize(580, 461)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(aminoAcidMapping)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.dataView = QtWidgets.QTableView(aminoAcidMapping)
        self.dataView.setObjectName("dataView")
        self.horizontalLayout.addWidget(self.dataView)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.buttonAdd = QtWidgets.QPushButton(aminoAcidMapping)
        self.buttonAdd.setEnabled(False)
        self.buttonAdd.setText("")
        self.buttonAdd.setObjectName("buttonAdd")
        self.verticalLayout.addWidget(self.buttonAdd)
        self.buttonRemove = QtWidgets.QPushButton(aminoAcidMapping)
        self.buttonRemove.setEnabled(False)
        self.buttonRemove.setText("")
        self.buttonRemove.setObjectName("buttonRemove")
        self.verticalLayout.addWidget(self.buttonRemove)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(aminoAcidMapping)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(aminoAcidMapping)
        self.buttonBox.accepted.connect(aminoAcidMapping.accept)
        self.buttonBox.rejected.connect(aminoAcidMapping.reject)
        QtCore.QMetaObject.connectSlotsByName(aminoAcidMapping)

    def retranslateUi(self, aminoAcidMapping):
        _translate = QtCore.QCoreApplication.translate
        aminoAcidMapping.setWindowTitle(_translate("aminoAcidMapping", "Dialog"))

