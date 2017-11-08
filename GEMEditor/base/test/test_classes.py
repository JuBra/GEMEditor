import gc
from PyQt5.QtWidgets import QApplication, QDialog
from GEMEditor.base.classes import WindowManager


# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestWindowManager:

    def test_behavior(self):
        manager = WindowManager()
        dialog = QDialog(None)

        # Check addition
        assert not manager.windows
        manager.add(dialog)
        assert dialog in manager.windows

        # Check that dialog is prevented from gc
        del dialog
        gc.collect()
        assert manager.windows

        # Close dialog removes dialog
        dialog = list(manager.windows)[0]
        dialog.reject()
        assert not manager.windows

    def test_closing(self):
        manager = WindowManager()
        dialog = QDialog(None)
        manager.add(dialog)

        # Remove all dialogs
        manager.remove_all()

        assert not manager.windows
