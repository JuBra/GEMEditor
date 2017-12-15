# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\src\EditTestDialog.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_EditTestDialog(object):
    def setupUi(self, EditTestDialog):
        EditTestDialog.setObjectName("EditTestDialog")
        EditTestDialog.resize(447, 307)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(EditTestDialog)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.nameLabel = QtWidgets.QLabel(EditTestDialog)
        self.nameLabel.setObjectName("nameLabel")
        self.gridLayout.addWidget(self.nameLabel, 0, 0, 1, 1)
        self.nameLineEdit = QtWidgets.QLineEdit(EditTestDialog)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.gridLayout.addWidget(self.nameLineEdit, 0, 1, 1, 1)
        self.verticalLayout_4.addLayout(self.gridLayout)
        self.splitter_horizontal = QtWidgets.QSplitter(EditTestDialog)
        self.splitter_horizontal.setOrientation(QtCore.Qt.Vertical)
        self.splitter_horizontal.setObjectName("splitter_horizontal")
        self.splitter_vertical = QtWidgets.QSplitter(self.splitter_horizontal)
        self.splitter_vertical.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_vertical.setObjectName("splitter_vertical")
        self.groupBox = QtWidgets.QGroupBox(self.splitter_vertical)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.groupBox)
        self.tabWidget.setObjectName("tabWidget")
        self.reactionTab = ReactionSettingDisplayWidget()
        self.reactionTab.setObjectName("reactionTab")
        self.tabWidget.addTab(self.reactionTab, "")
        self.geneTab = GeneSettingDisplayWidget()
        self.geneTab.setObjectName("geneTab")
        self.tabWidget.addTab(self.geneTab, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.groupBox_2 = QtWidgets.QGroupBox(self.splitter_vertical)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tabWidget2 = QtWidgets.QTabWidget(self.groupBox_2)
        self.tabWidget2.setObjectName("tabWidget2")
        self.outcomeTab = OutcomeDisplayWidget()
        self.outcomeTab.setObjectName("outcomeTab")
        self.tabWidget2.addTab(self.outcomeTab, "")
        self.referenceTab = ReferenceDisplayWidget()
        self.referenceTab.setObjectName("referenceTab")
        self.tabWidget2.addTab(self.referenceTab, "")
        self.verticalLayout_2.addWidget(self.tabWidget2)
        self.groupBox_3 = QtWidgets.QGroupBox(self.splitter_horizontal)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.commentWidget = CommentDisplayWidget(self.groupBox_3)
        self.commentWidget.setObjectName("commentWidget")
        self.verticalLayout_3.addWidget(self.commentWidget)
        self.verticalLayout_4.addWidget(self.splitter_horizontal)
        self.buttonBox = QtWidgets.QDialogButtonBox(EditTestDialog)
        self.buttonBox.setStyleSheet("")
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_4.addWidget(self.buttonBox)

        self.retranslateUi(EditTestDialog)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget2.setCurrentIndex(0)
        self.buttonBox.accepted.connect(EditTestDialog.accept)
        self.buttonBox.rejected.connect(EditTestDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EditTestDialog)

    def retranslateUi(self, EditTestDialog):
        _translate = QtCore.QCoreApplication.translate
        EditTestDialog.setWindowTitle(_translate("EditTestDialog", "Edit case"))
        self.nameLabel.setText(_translate("EditTestDialog", "Name:"))
        self.groupBox.setTitle(_translate("EditTestDialog", "Conditions:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.reactionTab), _translate("EditTestDialog", "Reactions"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.geneTab), _translate("EditTestDialog", "Genes"))
        self.groupBox_2.setTitle(_translate("EditTestDialog", "Outcomes:"))
        self.tabWidget2.setTabText(self.tabWidget2.indexOf(self.outcomeTab), _translate("EditTestDialog", "Outcomes"))
        self.tabWidget2.setTabText(self.tabWidget2.indexOf(self.referenceTab), _translate("EditTestDialog", "References"))
        self.groupBox_3.setTitle(_translate("EditTestDialog", "Comment"))

from GEMEditor.model.display.base import CommentDisplayWidget, ReferenceDisplayWidget
from GEMEditor.model.display.modeltest import GeneSettingDisplayWidget, OutcomeDisplayWidget, ReactionSettingDisplayWidget
import icons_rc
