import pytest
from unittest.mock import Mock
from GEMEditor.database.model import *
from GEMEditor.model.classes.cobra import Model, Metabolite, Reaction
from GEMEditor.model.classes.annotation import Annotation
from GEMEditor.database.test.fixtures import database
from PyQt5.QtWidgets import QApplication

# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


@pytest.fixture()
def progress():
    mock = Mock()
    mock.wasCanceled = Mock(return_value=False)
    return mock

#Todo: Reimplement test case to not edit settings
# class TestAnnotationSettingsDialog:
#
#     @pytest.mark.parametrize("check_state", (True, False))
#     def test_get_settings(self, check_state):
#         dialog = AnnotationSettingsDialog()
#
#         # Check states
#         dialog.checkBox_charge.setChecked(check_state)
#         dialog.checkBox_formula.setChecked(check_state)
#
#         # Check getting the settings
#         settings = dialog.get_settings()
#         assert settings["formula"] == dialog.checkBox_formula.isChecked()
#         assert settings["charge"] == dialog.checkBox_charge.isChecked()
#
#     @pytest.mark.parametrize("check_state", (True, False))
#     def test_get_settings_resources(self, check_state):
#         metabolite_resources = {"a": 1, "b": 2}
#         reaction_resources = {"c": 3, "d": 4}
#         dialog = AnnotationSettingsDialog(metabolite_resources, reaction_resources)
#
#         # Set state for metabolite checkboxes
#         for checkbox in dialog.metabolite_checkboxes:
#             checkbox.setChecked(check_state)
#
#         # Set state for reaction checkboxes
#         for checkbox in dialog.reaction_checkboxes:
#             checkbox.setChecked(check_state)
#
#         settings = dialog.get_settings()
#         if check_state:
#             assert set(settings["reaction_resources"]) == set(reaction_resources.values())
#             assert set(settings["metabolite_resources"]) == set(metabolite_resources.values())
#         else:
#             assert not settings["reaction_resources"]
#             assert not settings["metabolite_resources"]


class Test_get_reactions_with_same_signature:

    def test_get_entry_matching_signature(self, database):
        signature = set([1, 2, 3, 4])
        entries = set([1])
        result = get_reactions_with_same_signature(database, entries,
                                                   signature, set())
        assert result == set([1])

    def test_dont_get_reactions_matching_signature_not_in_entries(self, database):
        signature = set([1, 2, 3, 4])
        entries = set()
        result = get_reactions_with_same_signature(database, entries,
                                                   signature, set())
        assert result == set()

    def test_not_matching_when_one_metabolite_missing(self, database):
        signature = set([1, 2, 3])
        entries = set([1])
        result = get_reactions_with_same_signature(database, entries,
                                                   signature, set())
        assert result == set()

    def test_not_matching_if_additional_metabolite(self, database):
        signature = set([1, 2, 3, 4, 5])
        entries = set([1])
        result = get_reactions_with_same_signature(database, entries,
                                                   signature, set())
        assert result == set()

    def test_match_if_additional_metabolite_is_ignored(self, database):
        signature = set([1, 2, 3])
        entries = set([1])
        result = get_reactions_with_same_signature(database, entries,
                                                   signature, set([4]))
        assert result == set([1])


class Test_map_by_annotation:

    def test_map_metabolites(self, database):
        metabolite = Metabolite("m1")
        metabolite.annotation.add(Annotation(identifier="MNXM2", collection="metanetx.chemical"))
        metabolite.annotation.add(Annotation(identifier="MNXM215", collection="metanetx.chemical"))

        assert map_by_annotation(database, metabolite) == set([1, 2])

    def test_empty_result_if_not_in_db(self, database):
        metabolite = Metabolite("m1")
        metabolite.annotation.add(Annotation(identifier="MNXM2000", collection="metanetx.chemical"))

        assert map_by_annotation(database, metabolite) == set()


class Test_update_metabolite_database_mapping:

    def test_map_metabolite_by_annotation(self, database, progress):
        model = Model()
        met1 = Metabolite("m1")
        model.add_metabolites([met1])
        met1.annotation.add(Annotation(identifier="MNXM2", collection="metanetx.chemical"))

        update_metabolite_database_mapping(database, model, progress)
        assert model.database_mapping[met1] == 1

    def test_map_metabolite_by_name(self, database, progress):
        model = Model()
        met1 = Metabolite("m1", name="Water")
        model.add_metabolites([met1])

        update_metabolite_database_mapping(database, model, progress)
        assert model.database_mapping[met1] == 1

    def test_not_mapped_for_name_substring(self, database, progress):
        model = Model()
        met1 = Metabolite("m1", name="ater")
        model.add_metabolites([met1])

        update_metabolite_database_mapping(database, model, progress)
        assert model.database_mapping[met1] is None

    def test_map_metabolite_by_formula(self, database, progress):
        model = Model()
        met1 = Metabolite("m1", formula="H2O")
        model.add_metabolites([met1])

        update_metabolite_database_mapping(database, model, progress)
        assert model.database_mapping[met1] == 1


class Test_check_ambiguous_mappings:

    def test_do_nothing_if_no_ambiguous_maps(self):
        model = Model()
        metabolite = Metabolite()
        model.database_mapping[metabolite] = 1
        check_ambiguous_mappings(model, None)

        assert model.database_mapping[metabolite] == 1

    def test_ambiguous_maps_present(self):
        # Todo: Implement test
        assert True


class Test_update_reaction_database_mapping:

    def test_map_reaction_by_stoichiometry(self, database, progress):
        model = Model()
        met1 = Metabolite("m1")
        met2 = Metabolite("m2")
        met3 = Metabolite("m3")
        met4 = Metabolite("m4")
        model.add_metabolites((met1, met2,
                               met3, met4))
        model.database_mapping.update({met1: 1,
                                       met2: 2,
                                       met3: 3,
                                       met4: 4})
        reaction = Reaction("r1")
        reaction.add_metabolites({met1: -1, met2: -1,
                                  met3: 1, met4: 1})
        model.add_reactions([reaction])

        update_reaction_database_mapping(database, model, progress)

        assert model.database_mapping[reaction] == 1

    def test_map_reaction_by_annotation(self, database, progress):
        model = Model()
        met1 = Metabolite("m1")
        met2 = Metabolite("m2")
        model.add_metabolites([met1, met2])

        reaction = Reaction("r1")
        reaction.add_metabolites({met1: -1, met2: 1})
        reaction.annotation.add(Annotation(identifier="MNXR14892",
                                           collection="metanetx.reaction"))
        model.add_reactions([reaction])

        update_reaction_database_mapping(database, model, progress)

        assert model.database_mapping[reaction] == 1

    def test_no_map_by_stoichiometry_if_any_metabolite_not_mapped(self, database, progress):
        model = Model()
        met1 = Metabolite("m1")
        met2 = Metabolite("m2")
        model.add_metabolites((met1, met2))
        model.database_mapping.update({met1: 1})

        reaction = Reaction("r1")
        reaction.add_metabolites({met1: -1, met2: -1})
        model.add_reactions([reaction])

        update_reaction_database_mapping(database, model, progress)
        assert reaction not in model.database_mapping


