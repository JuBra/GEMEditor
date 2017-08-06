# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GenesDisplayWidget.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_GenesDisplayWidget(object):
    def setupUi(self, GenesDisplayWidget):
        GenesDisplayWidget.setObjectName("GenesDisplayWidget")
        GenesDisplayWidget.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(GenesDisplayWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.geneView = GeneTreeView(GenesDisplayWidget)
        self.geneView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.geneView.setObjectName("geneView")
        self.verticalLayout.addWidget(self.geneView)

        self.retranslateUi(GenesDisplayWidget)
        self.geneView.customContextMenuRequested['QPoint'].connect(GenesDisplayWidget.show_gene_contextmenu)
        QtCore.QMetaObject.connectSlotsByName(GenesDisplayWidget)

    def retranslateUi(self, GenesDisplayWidget):
        _translate = QtCore.QCoreApplication.translate
        GenesDisplayWidget.setWindowTitle(_translate("GenesDisplayWidget", "Form"))

from GEMEditor.widgets.views import GeneTreeView
