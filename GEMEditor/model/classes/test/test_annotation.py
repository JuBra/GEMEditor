import pytest
from GEMEditor.model.classes.annotation import Annotation


class TestAnnotation:

    @pytest.fixture(autouse=True)
    def init_objects(self):
        self.annotation1 = Annotation("test_collection", "test_id")
        self.annotation2 = Annotation("test_collection", "test_id")
        self.empty_annotation = Annotation()

    def test_init_(self):
        """ Test that collection and identifier is initialized to None """
        assert self.empty_annotation.collection is None
        assert self.empty_annotation.identifier is None
        assert self.empty_annotation.type == "is"
        assert self.annotation1.collection == "test_collection"
        assert self.annotation1.identifier == "test_id"
        assert self.annotation1.type == "is"

    def test__hash_(self):
        """ Test that annotations containing the same information
        return the same value by __hash__()"""

        assert self.annotation1 is not self.annotation2
        assert self.annotation1.__hash__() == self.annotation2.__hash__()
        assert self.annotation1.__hash__() != self.empty_annotation.__hash__()

    def test_annotation_eq1(self):
        """ Test equality of annotations """
        assert self.annotation1 == self.annotation2
        assert self.annotation1 is not self.annotation2

    def test_annotation_eq2(self):
        """ Test not equality if type is different """

        assert Annotation("a", "a", "is") != Annotation("a", "a", "has")
        assert Annotation("a", "a", "is").__hash__() != Annotation("a", "a", "has").__hash__()

    def test_annotation_ex2(self):
        """ Test class is checked for in annotation equality """

        class Mock:
            def __init__(self, collection=None, identifier=None, type="is"):
                self.collection = collection
                self.identifier = identifier
                self.type = type

        mock = Mock("test_collection", "test_id")
        assert self.annotation1 != mock
        assert self.annotation1.collection == mock.collection
        assert self.annotation1.identifier == mock.identifier

    def test_prevent_setting_of_variables(self):
        """ Test that collection and identifier cannot be set
         in order to assure hash stability """
        with pytest.raises(AttributeError):
            self.annotation1.collection = "test"
        with pytest.raises(AttributeError):
            self.annotation1.identifier = "bla"