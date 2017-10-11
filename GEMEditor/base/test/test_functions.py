import pytest
from GEMEditor.base.functions import *
from GEMEditor.cobraClasses import Metabolite
from GEMEditor.data_classes import Annotation


class Test_invert_mapping:

    @pytest.mark.parametrize("mapping", ({"test": [1, 2]},
                                         {"test": set([1, 2])}))
    def test_inversion(self, mapping):
        inverted = invert_mapping(mapping)
        assert inverted[1] == ["test"]
        assert inverted[2] == ["test"]
        assert len(inverted) == 2

        # Invert again
        # Note: Order of the items might change
        original = invert_mapping(inverted)
        assert original.keys() == mapping.keys()
        assert set(original["test"]) == set(mapping["test"])

    def test_one_by_one(self):
        mapping = {1: 2}
        inverted = invert_mapping(mapping)
        assert inverted == {2: [1]}


class Test_generate_copy_id:

    def test_id_not_in_collection(self):
        new_id = generate_copy_id(base_id="Base", collection=set(), suffix="_copy")
        assert new_id == "Base_copy"

    def test_id_in_collection(self):
        new_id = generate_copy_id(base_id="Base", collection=set(("Base_copy",)), suffix="_copy")
        assert new_id == "Base_copy1"

    def test_base_id_is_none(self):
        new_id = generate_copy_id(base_id=None, collection=set(), suffix="_copy")
        assert new_id == "None_copy"

    def test_wrong_collection_type(self):
        """ Some collection that does not support 'in' operator """

        with pytest.raises(TypeError):
            generate_copy_id(base_id="Base", collection=1, suffix="_copy")


class Test_convert_to_bool:

    @pytest.mark.parametrize("input, expectation", [("true", True),
                                                    ("false", False),
                                                    ("tRue", True),
                                                    ("fAlse", False),
                                                    (True, True),
                                                    (False, False)])
    def test_result(self, input, expectation):
        assert convert_to_bool(input) is expectation


class Test_get_annotation_to_item_map:

    def test_annotations(self):
        # Setup metabolites
        met1 = Metabolite("met1")
        annotation1 = Annotation(collection="chebi", identifier="test1")
        annotation2 = Annotation(collection="chebi", identifier="test2")
        met1.annotation.update((annotation1, annotation2))

        met2 = Metabolite("met2")
        annotation3 = Annotation(collection="chebi", identifier="test3")
        met2.annotation.add(annotation3)

        # Run
        mapping = get_annotation_to_item_map([met1, met2])

        assert mapping[annotation1] == [met1]
        assert mapping[annotation2] == [met1]
        assert mapping[annotation3] == [met2]


