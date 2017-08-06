# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AnnotationDisplayWidget.ui'
#
# Created by: PyQt5 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

class Ui_AnnotationDisplayWidget(object):
    def setupUi(self, AnnotationDisplayWidget):
        AnnotationDisplayWidget.setObjectName(_fromUtf8("AnnotationDisplayWidget"))
        AnnotationDisplayWidget.resize(251, 167)
        self.horizontalLayout = QtGui.QHBoxLayout(AnnotationDisplayWidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.dataView = QTableView(AnnotationDisplayWidget)
        self.dataView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.dataView.setObjectName(_fromUtf8("dataView"))
        self.dataView.horizontalHeader().setStretchLastSection(True)
        self.dataView.verticalHeader().setVisible(False)
        self.horizontalLayout.addWidget(self.dataView)
        self.verticalLayout_5 = QtGui.QVBoxLayout()
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.addAnnotationButton = QtGui.QPushButton(AnnotationDisplayWidget)
        self.addAnnotationButton.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/add_icon")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addAnnotationButton.setIcon(icon)
        self.addAnnotationButton.setObjectName(_fromUtf8("addAnnotationButton"))
        self.verticalLayout_5.addWidget(self.addAnnotationButton)
        self.deleteAnnotationButton = QtGui.QPushButton(AnnotationDisplayWidget)
        self.deleteAnnotationButton.setEnabled(False)
        self.deleteAnnotationButton.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/remove_icon")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.deleteAnnotationButton.setIcon(icon1)
        self.deleteAnnotationButton.setObjectName(_fromUtf8("deleteAnnotationButton"))
        self.verticalLayout_5.addWidget(self.deleteAnnotationButton)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout_5)

        self.retranslateUi(AnnotationDisplayWidget)
        QtCore.QObject.connect(self.deleteAnnotationButton, QtCore.SIGNAL(_fromUtf8("clicked()")), AnnotationDisplayWidget.delete_selected_rows)
        QtCore.QObject.connect(self.addAnnotationButton, QtCore.SIGNAL(_fromUtf8("clicked()")), AnnotationDisplayWidget.add_annotation)
        QtCore.QMetaObject.connectSlotsByName(AnnotationDisplayWidget)

    def retranslateUi(self, AnnotationDisplayWidget):
        AnnotationDisplayWidget.setWindowTitle(_translate("AnnotationDisplayWidget", "Form", None))

