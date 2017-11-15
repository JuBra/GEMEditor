import pytest
from GEMEditor.model.classes.cobra import Model
from GEMEditor.model.classes.reference import Reference, Author
from GEMEditor.model.classes.annotation import Annotation
from GEMEditor.rw import *
from GEMEditor.rw.annotation import annotate_element_from_xml
from GEMEditor.rw.reference import add_references, parse_references
from lxml.etree import Element


class TestAddReference:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.first_author = Author(lastname="FirstLastname",
                               firstname="FirstFirstname",
                               initials="FirstInitials")
        self.second_author = Author(lastname="SecondLastname",
                               firstname="SecondFirstname",
                               initials="SecondInitials")
        self.authors = [self.first_author, self.second_author]
        self.test_pmid = "123456"
        self.test_pmc = "PMC12345"
        self.test_doi = "10.1016/j.chemosphere.2016.03.102"
        self.test_url = "http://google.com"
        self.test_year = "1999"
        self.test_title = "Test title"
        self.test_journal = "Test journal"
        self.test_ref_id = "Test_id"
        self.reference = Reference(id=self.test_ref_id,
                                   pmid=self.test_pmid,
                                   pmc=self.test_pmc,
                                   doi=self.test_doi,
                                   url=self.test_url,
                                   year=self.test_year,
                                   title=self.test_title,
                                   journal=self.test_journal,
                                   authors=self.authors)
        self.model = Model("Test")
        self.model.references[self.reference.id] = self.reference

    def test_setup(self):
        assert self.reference.pmid == self.test_pmid
        assert self.reference.pmc == self.test_pmc
        assert self.reference.doi == self.test_doi
        assert self.reference.url == self.test_url
        assert self.reference.year == self.test_year
        assert self.reference.title == self.test_title
        assert self.reference.journal == self.test_journal
        assert isinstance(self.reference.authors, list)
        assert len(self.authors) == len(self.reference.authors)
        assert self.authors[0] == self.first_author
        assert self.authors[1] == self.second_author
        assert len(self.model.references) == 1

    def test_add_references(self):
        root = Element("root")
        add_references(root, self.model)

        references_list_node = root.find(ge_listOfReferences)
        assert references_list_node is not None
        assert len(references_list_node) == 1

        reference_node = references_list_node.find(ge_reference)
        assert reference_node is not None
        assert len(reference_node) == 2

        author_list_node = reference_node.find(ge_listOfAuthors)
        assert author_list_node is not None
        assert len(author_list_node) == 2

        first_author_node = author_list_node.find(ge_author)
        assert first_author_node is not None
        assert first_author_node.get("firstname") == self.first_author.firstname
        assert first_author_node.get("lastname") == self.first_author.lastname
        assert first_author_node.get("initials") == self.first_author.initials

        second_author_node = first_author_node.getnext()
        assert second_author_node is not None
        assert second_author_node.get("firstname") == self.second_author.firstname
        assert second_author_node.get("lastname") == self.second_author.lastname
        assert second_author_node.get("initials") == self.second_author.initials

        annotation = annotate_element_from_xml(reference_node)
        assert len(annotation) == 3
        assert Annotation("pubmed", self.test_pmid) in annotation
        assert Annotation("pmc", self.test_pmc) in annotation
        assert Annotation("doi", self.test_doi) in annotation

        assert reference_node.attrib == {"url": self.test_url,
                                         "year": self.test_year,
                                         "title": self.test_title,
                                         "journal": self.test_journal,
                                         "id": self.test_ref_id}

    def test_addition_of_optional_attributes_only_when_set(self):

        root = Element("root")
        reference = Reference()
        model = Model("Testmodel")
        model.references[reference.id] = reference
        add_references(root, model)

        reference_node = root.find("/".join([ge_listOfReferences, ge_reference]))
        assert reference_node is not None
        assert reference_node.get("url") is None
        assert reference_node.find(ge_listOfAuthors) is None
        assert reference_node.get("year") is None
        assert reference_node.get("title") is None
        assert reference_node.get("journal") is None
        assert reference_node.get("id") == reference.id
        assert reference_node.find(sbml3_annotation) is None

    def test_parsing_consistency(self):
        root = Element("root")
        add_references(root, self.model)

        references = parse_references(root)
        assert len(references) == 1

        reference = references[0]
        assert reference is not self.reference
        assert reference.doi == self.test_doi
        assert reference.pmid == self.test_pmid
        assert reference.pmc == self.test_pmc
        assert reference.journal == self.test_journal
        assert reference.title == self.test_title
        assert reference.id == self.reference.id
        assert reference.authors[0] == self.first_author
        assert reference.authors[1] == self.second_author

    def test_annotation_optional(self):
        # Todo: Implement test
        assert True

