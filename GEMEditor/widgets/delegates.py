from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QItemDelegate, QDoubleSpinBox, QComboBox



class FloatInputDelegate(QItemDelegate):
    def __init__(self, parent, precision=6, allowed_range=(-1000., 1000.)):
        QItemDelegate.__init__(self, parent)
        self.precision = precision
        self.allowed_range = allowed_range

    def createEditor(self, parent, option, index):
        editor = QDoubleSpinBox(parent)
        editor.setRange(*self.allowed_range)
        editor.setDecimals(self.precision)
        return editor

    def setEditorData(self, spin_box, index):
        value = index.model().data(index, QtCore.Qt.DisplayRole)
        spin_box.setValue(value or 0.)

    def setModelData(self, spin_box, model, index):
        value = spin_box.value()
        model.setData(index, round(value, self.precision), QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class ComboBoxDelegate(QItemDelegate):
    def __init__(self, parent, choices=None):
        QItemDelegate.__init__(self, parent)
        self.choices = choices or []
        self.choices = ["--Select--"] + self.choices

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.addItems(self.choices)
        return editor

    def setEditorData(self, combo_box, index):
        value = index.model().data(index, QtCore.Qt.DisplayRole)
        current_index = combo_box.findText(str(value))
        if current_index == -1:
            current_index = 0
        combo_box.setCurrentIndex(current_index)

    def setModelData(self, combo_box, model, index):
        value = combo_box.currentText()
        model.setData(index, value, QtCore.Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
