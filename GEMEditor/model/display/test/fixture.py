from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget


class MockSlot(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.called = False
        self.last_caller = None

    @QtCore.pyqtSlot()
    def slot(self):
        self.called = True
        self.last_caller = self.sender()
