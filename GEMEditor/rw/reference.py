import logging
from GEMEditor.model.classes.reference import Reference, Author
from GEMEditor.rw import *
from GEMEditor.rw.annotation import annotate_xml_from_model, annotate_element_from_xml
from PyQt5.QtWidgets import QApplication
from lxml.etree import SubElement


LOGGER = logging.getLogger(__name__)


def add_references(model_node, model):

    if model.references:
        reference_list_node = SubElement(model_node, ge_listOfReferences)
        for reference in model.references.values():
            reference_node = SubElement(reference_list_node, ge_reference, attrib={"id": reference.id})

            # Add optional attributes
            if reference.year:
                reference_node.set("year", reference.year)
            if reference.title:
                reference_node.set("title", reference.title)
            if reference.url:
                reference_node.set("url", reference.url)
            if reference.journal:
                reference_node.set("journal", reference.journal)


            # Add authors
            if reference.authors:
                author_list_node = SubElement(reference_node, ge_listOfAuthors)
                for author in reference.authors:
                    SubElement(author_list_node, ge_author, attrib={"firstname": author.firstname,
                                                                    "lastname": author.lastname,
                                                                    "initials": author.initials})

            # Add annotations
            annotate_xml_from_model(reference_node, reference)


def parse_references(parser, model_node, model, progress):
    """ Parse basic model information

    Parameters
    ----------
    parser: GEMEditor.rw.parsers.BaseParser,
        Parser object reading file
    model: GEMEditor.model.classes.Model,
        Model being read
    model_node:
        XML node containing model information
    progress: QProgressDialog
        Progress dialog

    """

    reference_list = model_node.find(ge_listOfReferences)
    if reference_list is None or progress.wasCanceled():
        return
    else:
        progress.setLabelText("Reading references...")
        progress.setRange(0, len(reference_list))

    # Add references to model
    for i, reference_node in enumerate(reference_list.iterfind(ge_reference)):

        # Update dialog
        if progress.wasCanceled():
            return
        else:
            LOGGER.debug("Parsing reference on line: {0!s}".format(reference_node.sourceline))
            progress.setValue(i)
            QApplication.processEvents()

        # Parse reference
        reference = Reference(id=reference_node.get("id"),
                              year=reference_node.get("year"),
                              title=reference_node.get("title"),
                              journal=reference_node.get("journal"),
                              url=reference_node.get("url"))

        # Add authors to reference
        author_list = reference_node.find(ge_listOfAuthors)
        if not author_list:
            parser.warn("Line {0!s}: Authors missing in reference '{1!s}'".format(reference_node.sourceline,
                                                                                  reference.id))
        else:
            for author_node in author_list.iterfind(ge_author):
                author = Author(firstname=author_node.get("firstname"),
                                lastname=author_node.get("lastname"),
                                initials=author_node.get("initials"))
                reference.add_author(author)

        annotations = annotate_element_from_xml(reference_node)
        if annotations:
            mapping = {"pubmed": "pmid",
                       "pmc": "pmc",
                       "doi": "doi"}

            for x in annotations:
                if x.collection in mapping:
                    setattr(reference, mapping[x.collection], x.identifier)

        model.add_reference(reference)
