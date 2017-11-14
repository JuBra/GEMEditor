from warnings import warn

from GEMEditor.model.classes.reference import Annotation
from GEMEditor.rw import *
from lxml.etree import SubElement
from six.moves.urllib.parse import urlsplit


def annotate_xml_from_model(node, element):
    """ Write the annotation from the model to the xml tree """

    if not element.annotation:
        return

    is_annotations = [x for x in element.annotation if x.type == "is"]
    has_annotations = [x for x in element.annotation if x.type == "has"]

    annotation_node = add_rdf_annotation(node, element)

    if is_annotations:
        rdf_bag_node = add_qbiol_bag(annotation_node, bqbiol_is)
        for x in is_annotations:
            add_miriam(rdf_bag_node, x)

    if has_annotations:
        rdf_bag_node = add_qbiol_bag(annotation_node, bqbiol_has)
        for x in has_annotations:
            add_miriam(rdf_bag_node, x)


def add_rdf_annotation(node, element):
    """" Add a Rdf node to the provided node in order to store annotations"""

    annotation_node = SubElement(node, sbml3_annotation)

    return SubElement(SubElement(annotation_node, rdf_RDF),
                      rdf_description,
                      {rdf_about: "#"+element.id})


def add_miriam(bag, annotation):
    """ Add mmiriam annotation to node """

    if annotation.collection and annotation.identifier:
        SubElement(bag, rdf_li, attrib={rdf_resource: "http://identifiers.org/{0}/{1}".format(annotation.collection,
                                                                                              annotation.identifier)})


def add_qbiol_bag(node, bag_tag):
    """ Add a rdf bag inside a bqbiol:is or bqbiol:property element """
    return SubElement(SubElement(node, bag_tag), rdf_bag)


def annotate_element_from_xml(node, element=None):
    """ Add the annotations contained in the xml file to the model element"""

    try:
        annotation_node = node.find(sbml3_annotation)
        rdf_node = annotation_node.find(rdf_RDF)
        description_node = rdf_node.find(rdf_description)
    except AttributeError:
        return

    if element is None:
        annotation = set()
    else:
        annotation = element.annotation

    for child in description_node:
        add_annotations_to_element(child, annotation)

    return annotation


def add_annotations_to_element(node, element):
    """ Add the annotaitons contained in a bqbiol node to the model element """

    if node.tag == bqbiol_is:
        add_annotations(node, element, type="is")
    elif node.tag == bqbiol_has:
        add_annotations(node, element, type="has")


def add_annotations(node, element, type):
    """ Add annotations from the provided bqbiol node to the element """

    rdf_bag_node = node.find(rdf_bag)
    if rdf_bag_node is not None:
        for li_node in rdf_bag_node.iter(rdf_li):
            try:
                miriam_link = li_node.attrib[rdf_resource]
            except KeyError:
                continue

            try:
                element.add(parse_miriam_string(miriam_link, type))
            except ValueError:
                warn("The annotation '{0}' at line {1} does not match the format http://identifiers.org/provider/id".format(miriam_link, str(node.sourceline)))
                continue


def parse_miriam_string(miriam_link, type):
    """ Parse the miriam annotation contained in node """

    split_url = urlsplit(miriam_link)
    # Remove leading slash and split path in collection and identifier
    collection, identifier = split_url.path.lstrip("/").split("/", 1)
    if split_url.netloc != "identifiers.org":
        raise ValueError("{0} does not start with http://identifiers.org/".format(miriam_link))
    else:
        return Annotation(collection=collection, identifier=identifier, type=type)
