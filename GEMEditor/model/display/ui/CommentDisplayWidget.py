# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'CommentDisplayWidget.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CommentDisplayWidget(object):
    def setupUi(self, CommentDisplayWidget):
        CommentDisplayWidget.setObjectName("CommentDisplayWidget")
        CommentDisplayWidget.resize(271, 192)
        self.verticalLayout = QtWidgets.QVBoxLayout(CommentDisplayWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.commentInput = QtWidgets.QTextEdit(CommentDisplayWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.commentInput.sizePolicy().hasHeightForWidth())
        self.commentInput.setSizePolicy(sizePolicy)
        self.commentInput.setObjectName("commentInput")
        self.verticalLayout.addWidget(self.commentInput)

        self.retranslateUi(CommentDisplayWidget)
        QtCore.QMetaObject.connectSlotsByName(CommentDisplayWidget)

    def retranslateUi(self, CommentDisplayWidget):
        _translate = QtCore.QCoreApplication.translate
        CommentDisplayWidget.setWindowTitle(_translate("CommentDisplayWidget", "Form"))

