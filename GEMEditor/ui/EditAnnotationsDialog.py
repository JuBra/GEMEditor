# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'EditAnnotationsDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_EditAnnotationDialog(object):
    def setupUi(self, EditAnnotationDialog):
        EditAnnotationDialog.setObjectName("EditAnnotationDialog")
        EditAnnotationDialog.resize(185, 95)
        self.verticalLayout = QtWidgets.QVBoxLayout(EditAnnotationDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.typeLabel = QtWidgets.QLabel(EditAnnotationDialog)
        self.typeLabel.setObjectName("typeLabel")
        self.gridLayout.addWidget(self.typeLabel, 0, 0, 1, 1)
        self.typeComboBox = QtWidgets.QComboBox(EditAnnotationDialog)
        self.typeComboBox.setObjectName("typeComboBox")
        self.gridLayout.addWidget(self.typeComboBox, 0, 1, 1, 1)
        self.annotationLabel = QtWidgets.QLabel(EditAnnotationDialog)
        self.annotationLabel.setObjectName("annotationLabel")
        self.gridLayout.addWidget(self.annotationLabel, 1, 0, 1, 1)
        self.annotationLineEdit = QtWidgets.QLineEdit(EditAnnotationDialog)
        self.annotationLineEdit.setObjectName("annotationLineEdit")
        self.gridLayout.addWidget(self.annotationLineEdit, 1, 1, 1, 1)
        self.statusLabel = QtWidgets.QLabel(EditAnnotationDialog)
        self.statusLabel.setMaximumSize(QtCore.QSize(18, 18))
        self.statusLabel.setText("")
        self.statusLabel.setPixmap(QtGui.QPixmap(":/status_undefined"))
        self.statusLabel.setScaledContents(True)
        self.statusLabel.setObjectName("statusLabel")
        self.gridLayout.addWidget(self.statusLabel, 1, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(EditAnnotationDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(EditAnnotationDialog)
        self.buttonBox.accepted.connect(EditAnnotationDialog.accept)
        self.buttonBox.rejected.connect(EditAnnotationDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EditAnnotationDialog)

    def retranslateUi(self, EditAnnotationDialog):
        _translate = QtCore.QCoreApplication.translate
        EditAnnotationDialog.setWindowTitle(_translate("EditAnnotationDialog", "Edit annotation"))
        self.typeLabel.setText(_translate("EditAnnotationDialog", "Type:"))
        self.annotationLabel.setText(_translate("EditAnnotationDialog", "Annotation:"))

from GEMEditor.icons_rc import *
