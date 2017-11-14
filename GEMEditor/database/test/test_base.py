import pytest
from GEMEditor.database.base import DatabaseWrapper
from GEMEditor.model.classes.reference import Annotation


class TestDatabaseWrapper:

    def test_setup_no_database_file(self):
        with pytest.raises(FileNotFoundError):
            DatabaseWrapper("")

    def test_get_synonyms_from_id(self, database):
        result = database.get_synonyms_from_id(1, "metabolite")
        assert result == ["Water"]

        result = database.get_synonyms_from_id(1, "metabOlite")
        assert result == ["Water"]

        result = database.get_synonyms_from_id(1, "reaction")
        assert result == ["Glucose-6-Phosphatase"]

        result = database.get_synonyms_from_id(1, "reaCtion")
        assert result == ["Glucose-6-Phosphatase"]

        with pytest.raises(ValueError):
            database.get_synonyms_from_id(1, "pathway")

    def test_get_annotations_from_id(self, database):
        result = database.get_annotations_from_id(1, "metabolite")
        assert result == [Annotation(identifier="MNXM2", collection="metanetx.chemical")]

        result = database.get_annotations_from_id(1, "metabOlite")
        assert result == [Annotation(identifier="MNXM2", collection="metanetx.chemical")]

        result = database.get_annotations_from_id(1, "reaction")
        assert result == [Annotation(identifier="MNXR14892", collection="metanetx.reaction")]

        result = database.get_annotations_from_id(1, "reaCtion")
        assert result == [Annotation(identifier="MNXR14892", collection="metanetx.reaction")]

        with pytest.raises(ValueError):
            database.get_annotations_from_id(1, "pathway")

    def test_get_ids_from_annotation(self, database):
        result = database.get_ids_from_annotation(identifier="MNXM2",
                                                  collection="metanetx.chemical")
        assert result == [1]

        result = database.get_ids_from_annotation(identifier="MNXR14892",
                                                  collection="metanetx.reaction")
        assert result == [1]

        assert database.get_ids_from_annotation(identifier="", collection="") == []

    def test_get_ids_from_name(self, database):
        result = database.get_ids_from_name(name="Water", entry_type="metabolite")
        assert result == [1]

        result = database.get_ids_from_name(name="Water", entry_type="metabOlite")
        assert result == [1]

        result = database.get_ids_from_name(name="Glucose-6-Phosphatase", entry_type="reaction")
        assert result == [1]

        result = database.get_ids_from_name(name="Glucose-6-Phosphatase", entry_type="reaCtion")
        assert result == [1]

        result = database.get_ids_from_name(name="", entry_type="metabolite")
        assert result == []

    def test_get_ids_from_formula(self, database):
        result = database.get_ids_from_formula("H2O")
        assert result == [1]

        result = database.get_ids_from_formula("HO4P")
        assert result == [3]

        result = database.get_ids_from_formula("C5")
        assert result == []

    def test_get_metabolite_from_id(self, database):
        result = database.get_metabolite_from_id(1)
        assert result.formula == "H2O"
        assert result.name == "Water"
        assert Annotation(identifier="MNXM2", collection="metanetx.chemical") in result.annotation

        result = database.get_metabolite_from_id(50)
        assert result is None

    def test_get_reaction_participants_from_id(self, database):
        # Todo: Implement test
        assert True

    def test_get_reaction_string_from_id(self, database):
        result = database.get_reaction_string_from_id(1)
        assert result == "1 `H2O` + 1 `alpha-D-glucose 6-phosphate` = 1 `phosphate` + 1 `alpha-D-glucose`"

        assert database.get_reaction_string_from_id(10) is None

    def test_get_reaction_from_id(self, database):
        result = database.get_reaction_from_id(1)
        assert Annotation(identifier="MNXR14892", collection="metanetx.reaction") in result.annotation

        assert database.get_reaction_from_id(15) is None

    def test_get_miriam_collections(self, database):
        # Todo: specify entries
        result = database.get_miriam_collections("metabolite")
        assert result

        result = database.get_miriam_collections("reaction")
        assert result

        result = database.get_miriam_collections("not")
        assert not result

    def test_get_reaction_id_from_participant_ids(self, database):
        # All in the same reaction
        assert database.get_reaction_id_from_participant_ids([1, 2, 3, 4]) == set([1])
        # Not all in the same reaction
        assert database.get_reaction_id_from_participant_ids([1, 2, 3, 4, 5]) == set()








