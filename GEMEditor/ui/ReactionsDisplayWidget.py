# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReactionsDisplayWidget.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ReactionsDisplayWidget(object):
    def setupUi(self, ReactionsDisplayWidget):
        ReactionsDisplayWidget.setObjectName("ReactionsDisplayWidget")
        ReactionsDisplayWidget.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(ReactionsDisplayWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableViewReactions = QtWidgets.QTableView(ReactionsDisplayWidget)
        self.tableViewReactions.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableViewReactions.setObjectName("tableViewReactions")
        self.verticalLayout.addWidget(self.tableViewReactions)

        self.retranslateUi(ReactionsDisplayWidget)
        QtCore.QMetaObject.connectSlotsByName(ReactionsDisplayWidget)

    def retranslateUi(self, ReactionsDisplayWidget):
        _translate = QtCore.QCoreApplication.translate
        ReactionsDisplayWidget.setWindowTitle(_translate("ReactionsDisplayWidget", "Form"))

