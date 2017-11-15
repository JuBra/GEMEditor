import pytest
from GEMEditor.model.classes.reference import Reference, Author
from GEMEditor.model.classes.annotation import Annotation


class TestReference:

    @pytest.fixture(autouse=True)
    def init_objects(self):
        self.reference1 = Reference("test_abbrev", "name")
        self.reference2 = Reference("test_abbrev", "name")
        self.empty_reference = Reference()

    def test___init__(self):
        """ Test the default values of empty reference """
        assert self.empty_reference.authors == []
        assert self.empty_reference.pmid == ""
        assert self.empty_reference.pmc == ""
        assert self.empty_reference.abstract == ""
        assert self.empty_reference.doi == ""
        assert self.empty_reference.title == ""
        assert self.empty_reference.year == ""
        assert self.empty_reference.url == ""
        assert self.empty_reference.journal == ""

    def test_author_string1(self):
        """ Check that empty string is returned if no author is set """
        assert self.empty_reference.reference_string() == ""

    def test_author_string2(self):
        """ Test correct string for single author """
        self.empty_reference.authors = [Author("Family", "First", "Initials")]
        self.empty_reference.year = "2015"
        assert self.empty_reference.reference_string() == "Family Initials, 2015"

    def test_author_string3(self):
        """ Test correct string for two authors """
        self.empty_reference.authors = [Author("FamilyFirst", "", "InitialsFirst"),
                                        Author("FamilySecond", "", "InitialsSecond")]

        self.empty_reference.year = "2015"
        expected = "FamilyFirst InitialsFirst and FamilySecond InitialsSecond, 2015"
        assert self.empty_reference.reference_string() == expected

    def test_author_string4(self):
        """ Test correct string for 3 authors """
        self.empty_reference.authors = [Author("Family1", "", "Initials1"),
                                        Author("Family2", "", "Initials2"),
                                        Author("Family3", "", "Initials3")]
        self.empty_reference.year = "2015"
        expected = "Family1 Initials1 et al., 2015"
        assert self.empty_reference.reference_string() == expected

    def test_annotation_property(self):
        reference = Reference()
        reference.pmc = "1234"
        reference.pmid = "54321"
        reference.doi = "5555"

        assert Annotation("pubmed", reference.pmid) in reference.annotation
        assert Annotation("pmc", reference.pmc) in reference.annotation
        assert Annotation("doi", reference.doi) in reference.annotation


class TestAuthor:

    def test_setup(self):
        author = Author("lastname", "firstname", "initials")
        assert author.lastname == "lastname"
        assert author.firstname == "firstname"
        assert author.initials == "initials"
        assert Author() == ("", "", "")

    def test_author_str(self):
        """ Check author_str property returns the proper value"""
        assert Author(lastname="Last", initials="P", firstname="").display_str == "Last P"
        assert Author("Last", "", "").display_str == "Last"