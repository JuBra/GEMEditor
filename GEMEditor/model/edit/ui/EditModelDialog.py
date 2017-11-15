# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\src\EditModelDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets

class Ui_EditModelDialog(object):
    def setupUi(self, EditModelDialog):
        EditModelDialog.setObjectName("EditModelDialog")
        EditModelDialog.resize(359, 314)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(EditModelDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_id = QtWidgets.QLabel(EditModelDialog)
        self.label_id.setObjectName("label_id")
        self.gridLayout.addWidget(self.label_id, 0, 0, 1, 1)
        self.input_id = QtWidgets.QLineEdit(EditModelDialog)
        self.input_id.setObjectName("input_id")
        self.gridLayout.addWidget(self.input_id, 0, 1, 1, 1)
        self.label_name = QtWidgets.QLabel(EditModelDialog)
        self.label_name.setObjectName("label_name")
        self.gridLayout.addWidget(self.label_name, 1, 0, 1, 1)
        self.input_name = QtWidgets.QLineEdit(EditModelDialog)
        self.input_name.setObjectName("input_name")
        self.gridLayout.addWidget(self.input_name, 1, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.compartmentLabel = QtWidgets.QLabel(EditModelDialog)
        self.compartmentLabel.setObjectName("compartmentLabel")
        self.verticalLayout_2.addWidget(self.compartmentLabel)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.compartmentTableView = ElementTableView(EditModelDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.compartmentTableView.sizePolicy().hasHeightForWidth())
        self.compartmentTableView.setSizePolicy(sizePolicy)
        self.compartmentTableView.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.compartmentTableView.setObjectName("compartmentTableView")
        self.compartmentTableView.horizontalHeader().setStretchLastSection(True)
        self.compartmentTableView.verticalHeader().setVisible(False)
        self.horizontalLayout.addWidget(self.compartmentTableView)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.button_add_compartment = QtWidgets.QPushButton(EditModelDialog)
        self.button_add_compartment.setObjectName("button_add_compartment")
        self.verticalLayout.addWidget(self.button_add_compartment)
        self.button_del_compartment = QtWidgets.QPushButton(EditModelDialog)
        self.button_del_compartment.setObjectName("button_del_compartment")
        self.verticalLayout.addWidget(self.button_del_compartment)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(EditModelDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(EditModelDialog)
        self.buttonBox.accepted.connect(EditModelDialog.accept)
        self.buttonBox.rejected.connect(EditModelDialog.reject)
        EditModelDialog.accepted.connect(EditModelDialog.save_changes)
        QtCore.QMetaObject.connectSlotsByName(EditModelDialog)

    def retranslateUi(self, EditModelDialog):
        _translate = QtCore.QCoreApplication.translate
        EditModelDialog.setWindowTitle(_translate("EditModelDialog", "Edit Model"))
        self.label_id.setText(_translate("EditModelDialog", "ID:"))
        self.label_name.setText(_translate("EditModelDialog", "Name:"))
        self.compartmentLabel.setText(_translate("EditModelDialog", "Compartments:"))
        self.button_add_compartment.setText(_translate("EditModelDialog", "Add"))
        self.button_del_compartment.setText(_translate("EditModelDialog", "Delete"))

from GEMEditor.base.views import ElementTableView
