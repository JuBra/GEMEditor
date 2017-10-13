import pytest
from GEMEditor.database.model import *
from PyQt5.QtWidgets import QApplication

app = QApplication([])


class TestAnnotationSettingsDialog:

    @pytest.mark.parametrize("check_state", (True, False))
    def test_get_settings(self, check_state):
        dialog = AnnotationSettingsDialog({}, {})

        # Check states
        dialog.checkBox_charge.setChecked(check_state)
        dialog.checkBox_formula.setChecked(check_state)

        # Check getting the settings
        settings = dialog.get_settings()
        assert settings["formula"] == dialog.checkBox_formula.isChecked()
        assert settings["charge"] == dialog.checkBox_charge.isChecked()

    @pytest.mark.parametrize("check_state", (True, False))
    def test_get_settings_resources(self, check_state):
        metabolite_resources = {"a": 1, "b": 2}
        reaction_resources = {"c": 3, "d": 4}
        dialog = AnnotationSettingsDialog(metabolite_resources, reaction_resources)

        # Set state for metabolite checkboxes
        for checkbox in dialog.metabolite_checkboxes:
            checkbox.setChecked(check_state)

        # Set state for reaction checkboxes
        for checkbox in dialog.reaction_checkboxes:
            checkbox.setChecked(check_state)

        settings = dialog.get_settings()
        if check_state:
            assert set(settings["reaction_resources"]) == set(reaction_resources.values())
            assert set(settings["metabolite_resources"]) == set(metabolite_resources.values())
        else:
            assert not settings["reaction_resources"]
            assert not settings["metabolite_resources"]
