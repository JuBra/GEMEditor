# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\src\ParserErrorDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ParserErrorDialog(object):
    def setupUi(self, ParserErrorDialog):
        ParserErrorDialog.setObjectName("ParserErrorDialog")
        ParserErrorDialog.resize(390, 380)
        self.verticalLayout = QtWidgets.QVBoxLayout(ParserErrorDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_icon = QtWidgets.QLabel(ParserErrorDialog)
        self.label_icon.setText("")
        self.label_icon.setObjectName("label_icon")
        self.horizontalLayout.addWidget(self.label_icon)
        self.label_message = QtWidgets.QLabel(ParserErrorDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_message.sizePolicy().hasHeightForWidth())
        self.label_message.setSizePolicy(sizePolicy)
        self.label_message.setText("")
        self.label_message.setTextFormat(QtCore.Qt.RichText)
        self.label_message.setWordWrap(True)
        self.label_message.setObjectName("label_message")
        self.horizontalLayout.addWidget(self.label_message)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tabWidget = QtWidgets.QTabWidget(ParserErrorDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_errors = QtWidgets.QWidget()
        self.tab_errors.setObjectName("tab_errors")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab_errors)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.list_errors = QtWidgets.QListWidget(self.tab_errors)
        self.list_errors.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.list_errors.setObjectName("list_errors")
        self.verticalLayout_2.addWidget(self.list_errors)
        self.tabWidget.addTab(self.tab_errors, "")
        self.tab_warnings = QtWidgets.QWidget()
        self.tab_warnings.setObjectName("tab_warnings")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_warnings)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.list_warnings = QtWidgets.QListWidget(self.tab_warnings)
        self.list_warnings.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.list_warnings.setObjectName("list_warnings")
        self.verticalLayout_3.addWidget(self.list_warnings)
        self.tabWidget.addTab(self.tab_warnings, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(ParserErrorDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ParserErrorDialog)
        self.tabWidget.setCurrentIndex(0)
        self.buttonBox.accepted.connect(ParserErrorDialog.accept)
        self.buttonBox.rejected.connect(ParserErrorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ParserErrorDialog)

    def retranslateUi(self, ParserErrorDialog):
        _translate = QtCore.QCoreApplication.translate
        ParserErrorDialog.setWindowTitle(_translate("ParserErrorDialog", "Dialog"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_errors), _translate("ParserErrorDialog", "Errors"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_warnings), _translate("ParserErrorDialog", "Warnings"))

