from lxml.etree import SubElement
from GEMEditor.rw import *
from GEMEditor.data_classes import Reference, Author
from GEMEditor.rw.annotation import annotate_xml_from_model, annotate_element_from_xml
from PyQt5.QtWidgets import QApplication


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


def parse_references(model_node, model=None, progress=None):

    reference_list_node = model_node.find(ge_listOfReferences)

    if reference_list_node is None:
        return
    elif progress is None:
        pass
    elif not progress.wasCanceled():
        progress.setLabelText("Reading references...")
        progress.setRange(0, len(reference_list_node))
    elif progress.wasCanceled():
        return

    references = []
    for i, reference_node in enumerate(reference_list_node.iterfind(ge_reference)):

        if progress is None:
            pass
        elif not progress.wasCanceled():
            progress.setValue(i)
            QApplication.processEvents()
        else:
            return

        new_reference = Reference(id=reference_node.get("id"),
                                  year=reference_node.get("year"),
                                  title=reference_node.get("title"),
                                  journal=reference_node.get("journal"),
                                  url=reference_node.get("url"))

        author_list_node = reference_node.find(ge_listOfAuthors)
        if author_list_node is not None:
            authors = []
            for child in author_list_node.iterfind(ge_author):
                authors.append(Author(firstname=child.get("firstname"),
                                      lastname=child.get("lastname"),
                                      initials=child.get("initials")))
            new_reference.authors = authors

        annotation = annotate_element_from_xml(reference_node)
        if annotation:
            for x in annotation:
                if x.collection == "pubmed":
                    new_reference.pmid = x.identifier
                elif x.collection == "pmc":
                    new_reference.pmc = x.identifier
                elif x.collection == "doi":
                    new_reference.doi = x.identifier

        if model is None:
            references.append(new_reference)
        else:
            model.add_reference(new_reference)

    return references