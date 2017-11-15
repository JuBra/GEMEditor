# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\DatabaseSearchWidget.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DatabaseSearchWidget(object):
    def setupUi(self, DatabaseSearchWidget):
        DatabaseSearchWidget.setObjectName("DatabaseSearchWidget")
        DatabaseSearchWidget.resize(393, 374)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(DatabaseSearchWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox_search = QtWidgets.QGroupBox(DatabaseSearchWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_search.sizePolicy().hasHeightForWidth())
        self.groupBox_search.setSizePolicy(sizePolicy)
        self.groupBox_search.setObjectName("groupBox_search")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_search)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.combo_search_options = QtWidgets.QComboBox(self.groupBox_search)
        self.combo_search_options.setObjectName("combo_search_options")
        self.horizontalLayout.addWidget(self.combo_search_options)
        self.lineEdit_search_input = QtWidgets.QLineEdit(self.groupBox_search)
        self.lineEdit_search_input.setObjectName("lineEdit_search_input")
        self.horizontalLayout.addWidget(self.lineEdit_search_input)
        self.pushButton_search = QtWidgets.QPushButton(self.groupBox_search)
        self.pushButton_search.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/search_icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_search.setIcon(icon)
        self.pushButton_search.setObjectName("pushButton_search")
        self.horizontalLayout.addWidget(self.pushButton_search)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.dataView_search_results = ElementTableView(self.groupBox_search)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dataView_search_results.sizePolicy().hasHeightForWidth())
        self.dataView_search_results.setSizePolicy(sizePolicy)
        self.dataView_search_results.setObjectName("dataView_search_results")
        self.dataView_search_results.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.dataView_search_results)
        self.verticalLayout_2.addWidget(self.groupBox_search)

        self.retranslateUi(DatabaseSearchWidget)
        QtCore.QMetaObject.connectSlotsByName(DatabaseSearchWidget)

    def retranslateUi(self, DatabaseSearchWidget):
        _translate = QtCore.QCoreApplication.translate
        DatabaseSearchWidget.setWindowTitle(_translate("DatabaseSearchWidget", "Form"))
        self.groupBox_search.setTitle(_translate("DatabaseSearchWidget", "Search"))

from GEMEditor.base.views import ElementTableView
