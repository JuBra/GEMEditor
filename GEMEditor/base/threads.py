from PyQt5 import QtCore


class ProgressSignals(QtCore.QObject):

    new_value = QtCore.pyqtSignal(int)
    new_range = QtCore.pyqtSignal(int, int)
    new_label = QtCore.pyqtSignal(str)
    increment_progress = QtCore.pyqtSignal()

    def __init__(self):
        super(ProgressSignals, self).__init__()
        self.was_canceled = False

    def cancel(self):
        self.was_canceled = True

    def increment(self):
        self.increment_progress.emit()

    def setValue(self, value):
        self.new_value.emit(value)

    def setRange(self, lower, upper):
        self.new_range.emit(lower, upper)

    def setLabelText(self, text):
        self.new_label.emit(text)
