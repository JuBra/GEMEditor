import pytest
from GEMEditor.database.model import *
from GEMEditor.cobraClasses import Model, Metabolite, Reaction
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


class Test_update_metabolites:

    def test_updating(self):
        model = Model()
        met1 = Metabolite(id="met1", formula="H2O", name="Water", charge=0., compartment="c")
        react1 = Reaction(id="react1", name="test2", subsystem="test2", lower_bound=0., upper_bound=1000.)
        react1.add_metabolites({met1: -1})

        model.add_metabolites([met1])
        model.add_reactions([react1])
        model.setup_tables()

        assert model.QtReactionTable.rowCount() == 1
        assert model.QtMetaboliteTable.rowCount() == 1

        # Check that content is right
        for i, element in enumerate(model.QtMetaboliteTable.header):
            assert str(getattr(met1, element.lower())) == model.QtMetaboliteTable.item(0, i).text()

        # Check that metabolite id is in table
        assert met1.id in model.QtReactionTable.item(0, 2).text()

        # Change metabolite
        met1.id = "new_id"
        met1.name = "new_name"
        met1.formula = "H2O2"
        met1.name = "None"
        met1.charge = 1.
        met1.compartment = "e"

        # Tables are out of sync
        for i, element in enumerate(model.QtMetaboliteTable.header):
            assert str(getattr(met1, element.lower())) != model.QtMetaboliteTable.item(0, i).text()

        # Check reaction table out of sync
        assert react1.id not in model.QtReactionTable.item(0, 2).text()

        update_metabolites(model, [met1])

        # Metabolite table updated
        for i, element in enumerate(model.QtMetaboliteTable.header):
            assert str(getattr(met1, element.lower())) == model.QtMetaboliteTable.item(0, i).text()

        # Reaction table updated
        assert met1.id in model.QtReactionTable.item(0, 2).text()
