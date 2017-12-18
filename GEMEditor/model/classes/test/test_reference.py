import pytest
from GEMEditor.model.classes.reference import Reference, Author
from GEMEditor.model.classes.annotation import Annotation


class TestReference:

    def test_add_author(self):
        reference = Reference()
        author = Author("Family", "First", "Initials")
        reference.add_author(author)

        assert author in reference.authors

    def test_empty_author_string(self):
        assert Reference().reference_string() == ""

    def test_single_author_string(self):
        reference = Reference(year="2015")
        reference.add_author(Author("Family", "First", "Initials"))

        assert reference.reference_string() == "Family Initials, 2015"

    def test_two_authors_string(self):
        reference = Reference(year="2015")
        reference.add_author(Author("FamilyFirst", "", "InitialsFirst"))
        reference.add_author(Author("FamilySecond", "", "InitialsSecond"))

        expected = "FamilyFirst InitialsFirst and FamilySecond InitialsSecond, 2015"
        assert reference.reference_string() == expected

    def test_multi_author_string(self):
        reference = Reference(year="2015")
        reference.add_author(Author("Family1", "", "Initials1"))
        reference.add_author(Author("Family2", "", "Initials2"))
        reference.add_author(Author("Family3", "", "Initials3"))

        expected = "Family1 Initials1 et al., 2015"
        assert reference.reference_string() == expected

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