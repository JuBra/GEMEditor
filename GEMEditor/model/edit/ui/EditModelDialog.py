# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\src\EditModelDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_EditModelDialog(object):
    def setupUi(self, EditModelDialog):
        EditModelDialog.setObjectName("EditModelDialog")
        EditModelDialog.resize(359, 314)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(EditModelDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.IdLabel = QtWidgets.QLabel(EditModelDialog)
        self.IdLabel.setObjectName("IdLabel")
        self.gridLayout.addWidget(self.IdLabel, 0, 0, 1, 1)
        self.modelIdInput = QtWidgets.QLineEdit(EditModelDialog)
        self.modelIdInput.setObjectName("modelIdInput")
        self.gridLayout.addWidget(self.modelIdInput, 0, 1, 1, 1)
        self.NameLabel = QtWidgets.QLabel(EditModelDialog)
        self.NameLabel.setObjectName("NameLabel")
        self.gridLayout.addWidget(self.NameLabel, 1, 0, 1, 1)
        self.modelNameInput = QtWidgets.QLineEdit(EditModelDialog)
        self.modelNameInput.setObjectName("modelNameInput")
        self.gridLayout.addWidget(self.modelNameInput, 1, 1, 1, 1)
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
        self.addCompartmentButton = QtWidgets.QPushButton(EditModelDialog)
        self.addCompartmentButton.setObjectName("addCompartmentButton")
        self.verticalLayout.addWidget(self.addCompartmentButton)
        self.deleteCompartmentButton = QtWidgets.QPushButton(EditModelDialog)
        self.deleteCompartmentButton.setObjectName("deleteCompartmentButton")
        self.verticalLayout.addWidget(self.deleteCompartmentButton)
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
        self.modelIdInput.textChanged['QString'].connect(EditModelDialog.activateButton)
        self.modelNameInput.textChanged['QString'].connect(EditModelDialog.activateButton)
        self.addCompartmentButton.clicked.connect(EditModelDialog.add_compartment)
        self.deleteCompartmentButton.clicked.connect(EditModelDialog.delete_compartment)
        EditModelDialog.accepted.connect(EditModelDialog.save_changes)
        QtCore.QMetaObject.connectSlotsByName(EditModelDialog)

    def retranslateUi(self, EditModelDialog):
        _translate = QtCore.QCoreApplication.translate
        EditModelDialog.setWindowTitle(_translate("EditModelDialog", "Edit Model"))
        self.IdLabel.setText(_translate("EditModelDialog", "ID:"))
        self.NameLabel.setText(_translate("EditModelDialog", "Name:"))
        self.compartmentLabel.setText(_translate("EditModelDialog", "Compartments:"))
        self.addCompartmentButton.setText(_translate("EditModelDialog", "Add"))
        self.deleteCompartmentButton.setText(_translate("EditModelDialog", "Delete"))

from GEMEditor.widgets.views import ElementTableView
