import pytest
from unittest.mock import Mock
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtTest
from GEMEditor.database.query import *


app = QApplication([])


@pytest.fixture()
def monkeypatch_settings(monkeypatch):
    monkeypatch.setattr(QtCore.QSettings, "setValue", Mock())
    monkeypatch.setattr(QtCore.QSettings, "sync", Mock())


class TestDatabaseSettingWidget:

    def test_instantiation(self):
        mapping = [("a", 1), ("b", 2)]
        widget = DatabaseSettingWidget(mapping)

        checkboxes = list(widget.widget_resource_mapping.keys())

        # Check that there is one checkbox per item in mapping
        assert len(checkboxes) == len(mapping)
        assert set([x.text() for x in checkboxes]) == set([x[0] for x in mapping])

        # Check that all boxes are checked
        assert all(x.isChecked() for x in checkboxes)

        # Check that selected items return both
        assert set(widget.get_selected_annotations()) == set([x[1] for x in mapping])

        # Uncheck first box
        checkboxes[0].setChecked(False)

        # Check that only the second box is returned
        assert checkboxes[0].text() not in widget.get_selected_annotations()
        assert len(widget.get_selected_annotations()) == 1


class TestAnnotationSettingsDialog:

    @pytest.mark.usefixtures("monkeypatch_settings")
    def test_setup(self):
        metabolite_resources = {"ABC": "test1"}
        reaction_resources = {"DEF": "text2"}

        dialog = AnnotationSettingsDialog(metabolite_resources, reaction_resources)

        # Check that resources are returned by default
        default_result = dialog.get_settings()
        assert default_result["reaction_resources"] == set(reaction_resources.values())
        assert default_result["metabolite_resources"] == set(metabolite_resources.values())

        # Test that formula state is returned
        checkbox = dialog.metabolite_widget.checkBox_use_formula
        assert default_result["formula_charge"] is checkbox.isChecked()
        QtTest.QTest.mouseClick(checkbox, QtCore.Qt.LeftButton)

        new_result = dialog.get_settings()
        assert new_result["formula_charge"] is checkbox.isChecked()





