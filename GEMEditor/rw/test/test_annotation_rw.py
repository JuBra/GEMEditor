import pytest
from GEMEditor.rw import *
import lxml.etree as ET
from lxml.etree import Element
from GEMEditor.data_classes import Annotation

from GEMEditor.rw.annotation import add_miriam, add_qbiol_bag, add_rdf_annotation, annotate_xml_from_model, parse_miriam_string, annotate_element_from_xml

from GEMEditor.rw.test.ex_annotation import valid_annotation, valid_annotation_id, valid_annotation_provider, invalid_annotation1, invalid_annotation2, valid_annotation_xml


class MockElement:
    def __init__(self):
        self.id = "test_id"
        self.annotation = set()


is_annotation = Annotation("collection", "identifier")
has_annotation = Annotation("collection2", "identifier2", "has")


class TestAddMiriam:
    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.node = Element("test")
        self.annotation = is_annotation

    def test_addition(self):
        """ Test the addition of a valid annotation """
        return_value = add_miriam(self.node, self.annotation)

        assert self.node.find(rdf_li).attrib == {rdf_resource: "http://identifiers.org/collection/identifier"}
        assert return_value is None

    def test_no_addition_for_empty_annotation(self):
        """ Test that no subelement is added if collection or identifier is falsy """

        add_miriam(self.node, Annotation())

        assert list(self.node) == []


class TestAddQbiolBag:
    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.node = Element("test")

    def test_is_addition(self):
        return_value = add_qbiol_bag(self.node, bqbiol_is)

        assert len(self.node) == 1
        assert self.node.find(bqbiol_is) is not None
        assert return_value.tag == rdf_bag

    def test_property_addition(self):
        return_value = add_qbiol_bag(self.node, bqbiol_has)

        assert len(self.node) == 1
        assert self.node.find(bqbiol_has) is not None
        assert return_value.tag == rdf_bag


class TestAddRDFAnnotation:
    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.node = Element("test")
        self.model_element = MockElement()

    def test_addition(self):
        return_value = add_rdf_annotation(self.node, self.model_element)

        assert len(self.node) == 1
        annotation_node = self.node.find(sbml3_annotation)
        assert annotation_node is not None
        assert len(annotation_node) == 1

        assert annotation_node.find(rdf_RDF) is not None
        assert return_value.tag == rdf_description
        assert return_value.attrib == {rdf_about: "#test_id"}
        assert len(return_value) == 0


class TestAnnotateXMLFromModel:
    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.node = Element("test")
        self.empty_element = MockElement()
        self.annotated_element = MockElement()
        self.annotated_element.annotation.add(is_annotation)
        self.annotated_element.annotation.add(has_annotation)
        self.is_annotation_only = MockElement()
        self.is_annotation_only.annotation.add(is_annotation)
        self.has_annotation_only = MockElement()
        self.has_annotation_only.annotation.add(has_annotation)

    def test_empty_annotation(self):
        """ Test that no children are added to the node if the annotation is empty """

        len_before = len(self.node)
        annotate_xml_from_model(self.node, self.empty_element)
        assert len(self.node) == len_before

    def test_addition_annotated_element(self):
        """ Test that the annotations are added properly """

        annotate_xml_from_model(self.node, self.annotated_element)

        # Check that node has only one child i.e. an annotation node
        assert len(self.node) == 1
        annotation_node = self.node.find(sbml3_annotation)
        assert annotation_node is not None

        # Check that node has only one child i.e. an RDF node
        assert len(annotation_node) == 1
        rdf_node = annotation_node.find(rdf_RDF)
        assert rdf_node is not None

        # Chcek that the RDF node has only one child i.e. RDF
        assert len(rdf_node) == 1
        description_node = rdf_node.find(rdf_description)
        assert description_node is not None

        # Check that the RDF description node has two children i.e. bqbiol:is and bqbiol:property
        assert len(description_node) == 2
        is_node = description_node.find(bqbiol_is)
        assert is_node is not None
        has_node = description_node.find(bqbiol_has)
        assert has_node is not None

        # Check that bqbiol elements have only one child each i.e. a rdf bag
        assert len(is_node) == 1
        is_bag = is_node.find(rdf_bag)
        assert is_bag is not None

        assert len(has_node) == 1
        has_bag = has_node.find(rdf_bag)
        assert has_bag is not None

        # Check that the bas only contain one item i.e. the annotation item
        assert len(is_bag) == 1
        is_annotation_node = is_bag.find(rdf_li)
        assert len(is_annotation_node) == 0

        assert len(has_bag) == 1
        has_annotation_node = has_bag.find(rdf_li)
        assert len(has_annotation_node) == 0

        # Check the correctness of the annotation item
        assert is_annotation_node.attrib == {rdf_resource: "http://identifiers.org/collection/identifier"}
        assert has_annotation_node.attrib == {rdf_resource: "http://identifiers.org/collection2/identifier2"}

    def test_is_bag_not_added(self):
        """ Test that no empty bags are created if a certain type of annotation is missing """

        annotate_xml_from_model(self.node, self.has_annotation_only)

        annotation_node = self.node.find(sbml3_annotation)
        assert annotation_node is not None

        rdf_node = annotation_node.find(rdf_RDF)
        assert rdf_node is not None

        description_node = rdf_node.find(rdf_description)
        assert description_node is not None

        assert len(description_node) == 1
        has_node = description_node.find(bqbiol_has)
        assert has_node is not None
        assert len(has_node) == 1

    def test_has_bag_not_added(self):
        """ Test that no empty bags are created if a certain type of annotation is missing """

        annotate_xml_from_model(self.node, self.is_annotation_only)

        annotation_node = self.node.find(sbml3_annotation)
        assert annotation_node is not None

        rdf_node = annotation_node.find(rdf_RDF)
        assert rdf_node is not None

        description_node = rdf_node.find(rdf_description)
        assert description_node is not None

        assert len(description_node) == 1
        is_node = description_node.find(bqbiol_is)
        assert is_node is not None
        assert len(is_node) == 1


def test_parse_annotation_valid():
    """ Test the proper parsing of identifier """
    assert parse_miriam_string(valid_annotation, "is") == Annotation(collection=valid_annotation_provider,
                                                                     identifier=valid_annotation_id,
                                                                     type="is")


def test_parse_annotation_invalid():
    """ Test that value error is for invalid annotations """

    with pytest.raises(ValueError):
        parse_miriam_string(invalid_annotation1, "is")

    with pytest.raises(ValueError):
        parse_miriam_string(invalid_annotation2, "is")


class TestParseValidAnnotation:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.element = MockElement()

    def test_parse_annotation_xml(self):
        xml_tree = ET.fromstring(valid_annotation_xml)
        annotate_element_from_xml(xml_tree, self.element)

        assert len(self.element.annotation) == 4
        assert self.element.annotation == set([Annotation("chebi", "CHEBI:17283", "is"),
                                               Annotation("kegg.compound", "C04549", "is"),
                                               Annotation("chebi", "CHEBI:17283", "has"),
                                               Annotation("kegg.compound", "C04549", "has")])







