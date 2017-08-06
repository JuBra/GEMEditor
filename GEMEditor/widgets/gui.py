from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QLineEdit, QToolButton, QStyle
from GEMEditor import icons_rc


class ButtonLineEdit(QLineEdit):

    def __init__(self, parent):
        QLineEdit.__init__(self, parent)

        self.button = QToolButton(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/clear_icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button.setIcon(icon)
        self.button.setStyleSheet('border: 0px; padding: 0px;')
        self.button.setCursor(QtCore.Qt.ArrowCursor)
        self.button.hide()

        frame_width = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        button_size = self.button.sizeHint()

        self.setStyleSheet('QLineEdit {padding-right: %dpx; }' % (button_size.width() + frame_width + 1))
        self.setMinimumSize(max(self.minimumSizeHint().width(), button_size.width() + frame_width*2 + 2),
                            max(self.minimumSizeHint().height(), button_size.height() + frame_width*2 + 2))

        # Connect signals
        self.button.clicked.connect(self.clear_input)
        self.textChanged.connect(self.toggle_button)

        self.setPlaceholderText("Search..")

    @QtCore.pyqtSlot()
    def clear_input(self):
        self.clear()

    @QtCore.pyqtSlot()
    def toggle_button(self):
        self.button.setVisible(bool(self.text()))

    def resizeEvent(self, event):
        button_size = self.button.sizeHint()
        frame_width = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        self.button.move(self.rect().right() - frame_width - button_size.width(),
                         (self.rect().bottom() - button_size.height() + 1)/2)
        QLineEdit.resizeEvent(self, event)

