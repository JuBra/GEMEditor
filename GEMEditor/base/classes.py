import logging
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import QObject, pyqtSlot, QSettings


LOGGER = logging.getLogger(__name__)


class BaseModelItem:

    def __init__(self):
        super(BaseModelItem, self).__init__()
        self.gem_evidences = set()
        self.gem_annotations = set()

    def add_evidence(self, evidence):
        self.gem_evidences.add(evidence)

    def remove_evidence(self, evidence):
        self.gem_evidences.discard(evidence)

    def get_evidences_by_assertion(self, string):
        return [e for e in self.gem_evidences if e.assertion == string]

    def remove_all_evidences(self):
        for x in self.gem_evidences.copy():
            x.delete_links()

    def gem_prepare_deletion(self):
        self.remove_all_evidences()

    def add_annotation(self, annotation):
        self.gem_annotations.add(annotation)

    def remove_annotation(self, annotation):
        self.gem_annotations.discard(annotation)

    def get_annotation_by_collection(self, *args):
        return set([x.identifier for x in self.gem_annotations if x.collection in args])


class BaseEvidenceElement:
    def __init__(self, *args, **kwargs):
        super(BaseEvidenceElement, self).__init__(*args, **kwargs)
        self.gem_evidences = set()

    def add_evidence(self, evidence):
        self.gem_evidences.add(evidence)

    def remove_evidence(self, evidence):
        self.gem_evidences.discard(evidence)

    def remove_all_evidences(self):
        for x in self.gem_evidences.copy():
            x.delete_links()

    def get_evidences_by_assertion(self, string):
        return [e for e in self.gem_evidences if e.assertion == string]

    def gem_prepare_deletion(self):
        """ Prepare deletion of all items """
        self.remove_all_evidences()

        try:
            super(BaseEvidenceElement, self).gem_prepare_deletion()
        except AttributeError:
            pass


class BaseReferenceElement:
    def __init__(self, *args, **kwargs):
        super(BaseReferenceElement, self).__init__(*args, **kwargs)
        self.gem_references = set()

    def add_reference(self, reference):
        self.gem_references.add(reference)

    def remove_reference(self, reference):
        self.gem_references.discard(reference)

    def gem_prepare_deletion(self):
        """ Prepare deletion of item """
        self.gem_references.clear()

        try:
            super(BaseReferenceElement, self).gem_prepare_deletion()
        except AttributeError:
            pass


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

    def setValue(self, p_str, Any):
        super(Settings, self).setValue(p_str, Any)
        LOGGER.debug("Setting '{0!s}' changed to '{1!s}'".format(p_str, Any))


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
