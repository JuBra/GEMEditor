# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'StoichiometryDisplayWidget.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_StoichiometryDisplayWidget(object):
    def setupUi(self, StoichiometryDisplayWidget):
        StoichiometryDisplayWidget.setObjectName("StoichiometryDisplayWidget")
        StoichiometryDisplayWidget.resize(306, 240)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(StoichiometryDisplayWidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.dataView = ElementTableView(StoichiometryDisplayWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dataView.sizePolicy().hasHeightForWidth())
        self.dataView.setSizePolicy(sizePolicy)
        self.dataView.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.SelectedClicked)
        self.dataView.setSortingEnabled(True)
        self.dataView.setObjectName("dataView")
        self.dataView.horizontalHeader().setStretchLastSection(True)
        self.dataView.verticalHeader().setVisible(False)
        self.verticalLayout_4.addWidget(self.dataView)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.statusDescriptionLabel = QtWidgets.QLabel(StoichiometryDisplayWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusDescriptionLabel.sizePolicy().hasHeightForWidth())
        self.statusDescriptionLabel.setSizePolicy(sizePolicy)
        self.statusDescriptionLabel.setMinimumSize(QtCore.QSize(0, 20))
        self.statusDescriptionLabel.setObjectName("statusDescriptionLabel")
        self.horizontalLayout.addWidget(self.statusDescriptionLabel)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout_4)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.add_button = QtWidgets.QPushButton(StoichiometryDisplayWidget)
        self.add_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/add_icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.add_button.setIcon(icon)
        self.add_button.setObjectName("add_button")
        self.verticalLayout.addWidget(self.add_button)
        self.delete_button = QtWidgets.QPushButton(StoichiometryDisplayWidget)
        self.delete_button.setEnabled(False)
        self.delete_button.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/remove_icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.delete_button.setIcon(icon1)
        self.delete_button.setObjectName("delete_button")
        self.verticalLayout.addWidget(self.delete_button)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.statusLabel = QtWidgets.QLabel(StoichiometryDisplayWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusLabel.sizePolicy().hasHeightForWidth())
        self.statusLabel.setSizePolicy(sizePolicy)
        self.statusLabel.setMinimumSize(QtCore.QSize(28, 20))
        self.statusLabel.setMaximumSize(QtCore.QSize(28, 20))
        self.statusLabel.setStyleSheet("padding: 1 5 1 5;")
        self.statusLabel.setText("")
        self.statusLabel.setPixmap(QtGui.QPixmap(":/status_unknown"))
        self.statusLabel.setScaledContents(True)
        self.statusLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.statusLabel.setObjectName("statusLabel")
        self.verticalLayout.addWidget(self.statusLabel)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(StoichiometryDisplayWidget)
        self.add_button.clicked.connect(StoichiometryDisplayWidget.add_item)
        self.delete_button.clicked.connect(StoichiometryDisplayWidget.delete_item)
        QtCore.QMetaObject.connectSlotsByName(StoichiometryDisplayWidget)

    def retranslateUi(self, StoichiometryDisplayWidget):
        _translate = QtCore.QCoreApplication.translate
        StoichiometryDisplayWidget.setWindowTitle(_translate("StoichiometryDisplayWidget", "Form"))
        self.statusDescriptionLabel.setText(_translate("StoichiometryDisplayWidget", "Status:"))

from GEMEditor.widgets.views import ElementTableView
from GEMEditor.icons_rc import *
