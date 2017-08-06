from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog


class CustomStandardDialog(QDialog):
    def __init__(self, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)

    @QtCore.pyqtSlot()
    def save_dialog_geometry(self):
        # Store the geometry of the dialog during the closing
        settings = QtCore.QSettings()
        settings.setValue(self.__class__.__name__+"Geometry", self.saveGeometry())
        settings.sync()

    def restore_dialog_geometry(self):
        # Restore the geometry of the dialog
        # Should be called in the __init__(self) of the subclass
        settings = QtCore.QSettings()
        geometry = settings.value(self.__class__.__name__+"Geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)