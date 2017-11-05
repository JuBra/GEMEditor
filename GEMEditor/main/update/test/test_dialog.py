import pytest
import GEMEditor
from PyQt5.QtWidgets import QApplication, QDialogButtonBox
from PyQt5 import QtTest, QtCore
from unittest.mock import Mock
from GEMEditor import VERSION_IGNORED
from GEMEditor.main.update.dialog import UpdateAvailableDialog

app = QApplication([])

@pytest.fixture()
def patch_ignored_version(monkeypatch):
    monkeypatch.setattr(GEMEditor.main.update.dialog.QSettings, "value", Mock(return_value="0.1.5"))
    monkeypatch.setattr(GEMEditor.main.update.dialog.QSettings, "sync", Mock())
    monkeypatch.setattr(GEMEditor.main.update.dialog.QSettings, "setValue", Mock())

@pytest.fixture()
def mock_desktopservice(monkeypatch):
    monkeypatch.setattr(GEMEditor.main.update.dialog.QDesktopServices, "openUrl", Mock())


class TestUpdateAvailableDialog:

    def test_version_ignored(self, patch_ignored_version):
        dialog = UpdateAvailableDialog(latest_version="0.1.5")
        assert dialog.version_is_ignored() is True

    def test_version_not_ignored(self, patch_ignored_version):
        dialog = UpdateAvailableDialog(latest_version="0.1.6")
        assert dialog.version_is_ignored() is False

    def test_ignore_new_version(self, patch_ignored_version):
        dialog = UpdateAvailableDialog(latest_version="0.1.6")
        dialog.checkBox.setChecked(True)

        from GEMEditor.main.update.dialog import QSettings
        assert QSettings.setValue.called is False

        QtTest.QTest.mouseClick(dialog.buttonBox.button(QDialogButtonBox.No), QtCore.Qt.LeftButton)

        QSettings.setValue.assert_called_with(VERSION_IGNORED, "0.1.6")

    def test_version_not_ignored_if_yes_button_called(self, patch_ignored_version, mock_desktopservice):
        dialog = UpdateAvailableDialog(latest_version="0.1.6")
        dialog.checkBox.setChecked(True)

        from GEMEditor.main.update.dialog import QSettings, QDesktopServices
        assert QSettings.setValue.called is False
        assert QDesktopServices.openUrl.called is False

        QtTest.QTest.mouseClick(dialog.buttonBox.button(QDialogButtonBox.Yes), QtCore.Qt.LeftButton)

        assert QSettings.setValue.called is False
        assert QDesktopServices.openUrl.called is True