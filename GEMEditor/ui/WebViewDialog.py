# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'WebViewDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WebViewDialog(object):
    def setupUi(self, WebViewDialog):
        WebViewDialog.setObjectName("WebViewDialog")
        WebViewDialog.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(WebViewDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.webView = QtWebEngineWidgets.QWebEngineView(WebViewDialog)
        self.webView.setUrl(QtCore.QUrl("about:blank"))
        self.webView.setObjectName("webView")
        self.verticalLayout.addWidget(self.webView)
        self.buttonBox = QtWidgets.QDialogButtonBox(WebViewDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(WebViewDialog)
        self.buttonBox.accepted.connect(WebViewDialog.accept)
        self.buttonBox.rejected.connect(WebViewDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(WebViewDialog)

    def retranslateUi(self, WebViewDialog):
        _translate = QtCore.QCoreApplication.translate
        WebViewDialog.setWindowTitle(_translate("WebViewDialog", "Dialog"))

from PyQt5 import QtWebEngineWidgets
