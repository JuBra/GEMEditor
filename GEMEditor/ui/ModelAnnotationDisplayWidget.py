# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ModelAnnotationDisplayWidget.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AnnotationDisplayWidget(object):
    def setupUi(self, AnnotationDisplayWidget):
        AnnotationDisplayWidget.setObjectName("AnnotationDisplayWidget")
        AnnotationDisplayWidget.resize(180, 102)
        self.verticalLayout = QtWidgets.QVBoxLayout(AnnotationDisplayWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(AnnotationDisplayWidget)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_num_evidences = QtWidgets.QLabel(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_num_evidences.sizePolicy().hasHeightForWidth())
        self.label_num_evidences.setSizePolicy(sizePolicy)
        self.label_num_evidences.setText("")
        self.label_num_evidences.setObjectName("label_num_evidences")
        self.gridLayout.addWidget(self.label_num_evidences, 0, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.label_num_tests = QtWidgets.QLabel(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_num_tests.sizePolicy().hasHeightForWidth())
        self.label_num_tests.setSizePolicy(sizePolicy)
        self.label_num_tests.setText("")
        self.label_num_tests.setObjectName("label_num_tests")
        self.gridLayout.addWidget(self.label_num_tests, 1, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 2, 0, 1, 1)
        self.label_num_references = QtWidgets.QLabel(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_num_references.sizePolicy().hasHeightForWidth())
        self.label_num_references.setSizePolicy(sizePolicy)
        self.label_num_references.setText("")
        self.label_num_references.setObjectName("label_num_references")
        self.gridLayout.addWidget(self.label_num_references, 2, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(AnnotationDisplayWidget)
        QtCore.QMetaObject.connectSlotsByName(AnnotationDisplayWidget)

    def retranslateUi(self, AnnotationDisplayWidget):
        _translate = QtCore.QCoreApplication.translate
        AnnotationDisplayWidget.setWindowTitle(_translate("AnnotationDisplayWidget", "Form"))
        self.groupBox.setTitle(_translate("AnnotationDisplayWidget", "Annotation Information"))
        self.label.setText(_translate("AnnotationDisplayWidget", "Evidences:"))
        self.label_3.setText(_translate("AnnotationDisplayWidget", "Test cases:"))
        self.label_5.setText(_translate("AnnotationDisplayWidget", "References:"))

