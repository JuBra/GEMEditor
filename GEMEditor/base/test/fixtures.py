import pytest
from unittest.mock import Mock


@pytest.fixture()
def progress_not_cancelled(monkeypatch):
    monkeypatch.setattr("GEMEditor.base.classes.ProgressDialog.show", Mock())
    monkeypatch.setattr("GEMEditor.base.classes.ProgressDialog.exec_", Mock())
    monkeypatch.setattr("GEMEditor.base.classes.ProgressDialog.wasCanceled", Mock(return_value=False))

@pytest.fixture()
def settings_valid_email(monkeypatch):
    monkeypatch.setattr("GEMEditor.base.classes.Settings.setValue", Mock())
    monkeypatch.setattr("GEMEditor.base.classes.Settings.")
