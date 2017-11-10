import logging
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import QObject, pyqtSlot, QSettings


LOGGER = logging.getLogger(__name__)


class ProgressDialog(QProgressDialog):
    def __init__(self, parent, title=None, label="", min=0, max=100, min_duration=500):
        super(ProgressDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self.setLabelText(label)
        self.setMinimum(min)
        self.setMaximum(max)
        self.setMinimumDuration(min_duration)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        super(ProgressDialog, self).close()
        # Schedule dialog for deletion
        # Fixes external destruction warning
        self.deleteLater()


class Settings(QSettings):

    def __init__(self, *args):
        super(Settings, self).__init__(*args)
        self.prefix = ""

    def beginGroup(self, p_str):
        super(Settings, self).beginGroup(p_str)
        self.prefix = p_str+"/" if p_str else ""

    def endGroup(self):
        super(Settings, self).endGroup()
        self.prefix = ""

    def setValue(self, p_str, Any):
        super(Settings, self).setValue(p_str, Any)
        LOGGER.debug("Setting '{0}{1!s}' changed to '{2!s:.100}'".format(self.prefix, p_str, Any))


class WindowManager(QObject):
    """ Manage dialog windows

    This class is intended for the management of
    dialog instances. An active reference to the
    instance is kept to avoid premature garbage
    collection that is caused by displaying non-
    modal dialogs via the .show() method which
    returns control immediately. After closing
    the dialog the instance will be removed from
    the manager and is therefore free for gc. """

    def __init__(self):
        super(WindowManager, self).__init__()
        self._windows = set()

    @property
    def windows(self):
        return self._windows.copy()

    def add(self, dialog):
        """ Add a dialog to manager

        Parameters
        ----------
        dialog: QDialog

        Returns
        -------
        None
        """
        self._windows.add(dialog)
        dialog.finished.connect(self.delete_dialog)

    def remove(self, dialog):
        """ Remove dialog from manager

        Parameters
        ----------
        dialog: QDialog

        Returns
        -------
        None
        """
        self._windows.discard(dialog)

    def remove_all(self):
        """ Delete all managed dialogs

        Returns
        -------
        None
        """
        for dialog in self.windows:
            # Remove c object before deleting dialog otherwise warnings
            # are thrown due to external deletion of object
            dialog.done(2)
            dialog.deleteLater()

    @pyqtSlot()
    def delete_dialog(self):
        """ Slot called by finished signal

        Returns
        -------
        None
        """
        sender = self.sender()
        self.remove(sender)
