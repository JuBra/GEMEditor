from lxml.etree import SubElement
from GEMEditor.rw import *
from PyQt5.QtWidgets import QApplication
from GEMEditor.evidence_class import Evidence


def add_evidences_to_xml(model_node, model):
    """ Serialize all evidence objects present in the model

    Save all evidences present in the model to a xml node that
    is used for saving the model to an sbml file.

    Parameters
    ----------
    model_node : lxml.etree.Element
    model : GEMEditor.cobraClasses.Model

    Returns
    -------
    None
    """

    if len(model.all_evidences) > 0:
        list_of_evidences = SubElement(model_node, ge_listOfEvidences)

        for element in model.all_evidences.valuerefs():
            evidence = element()
            if evidence is None:
                continue

            evidence_node = SubElement(list_of_evidences, ge_evidence,
                                       attrib={"id": evidence.internal_id,
                                               "assertion": evidence.assertion,
                                               "entity_id": evidence.entity.id,
                                               "entity_type": type(evidence.entity).__name__,
                                               "eco": evidence.eco})
            if evidence.comment:
                evidence_node.set("comment", evidence.comment)
            if evidence.term:
                evidence_node.set("term", evidence.term)
            if evidence.link:
                evidence_node.set("link_id", evidence.link.id)
                evidence_node.set("link_type", type(evidence.link).__name__)
            if evidence.target:
                evidence_node.set("target_id", evidence.target.id)
                evidence_node.set("target_type", type(evidence.target).__name__)

            # Add linked references if present
            if evidence.references:
                list_of_reference_links_node = SubElement(evidence_node, ge_listOfReferenceLinks)
                for reference in evidence.references:
                    SubElement(list_of_reference_links_node, ge_referenceLink, attrib={"id": reference.id})


def parse_evidences_from_xml(model_node, model, progress=None):

    list_of_evidences_node = model_node.find(ge_listOfEvidences)

    if list_of_evidences_node is None:
        return
    elif progress is None:
        pass
    elif not progress.wasCanceled():
        progress.setLabelText("Reading evidences...")
        progress.setRange(0, len(list_of_evidences_node))
    else:
        return

    for i, evidence_node in enumerate(list_of_evidences_node.iterfind(ge_evidence)):

        if progress is None:
            pass
        elif not progress.wasCanceled():
            progress.setValue(i)
            QApplication.processEvents()
        else:
            return

        new_evidence = Evidence(internal_id=evidence_node.get("id"), term=evidence_node.get("term"),
                                assertion=evidence_node.get("assertion"), comment=evidence_node.get("comment"),
                                eco=evidence_node.get("eco"))

        entity_id = evidence_node.get("entity_id")
        entity_type = evidence_node.get("entity_type")

        entity = get_item_from_model(entity_type, entity_id, model)
        new_evidence.set_entity(entity)

        # Add linked item if present
        link_id = evidence_node.get("link_id")
        link_type = evidence_node.get("link_type")
        if link_id and link_type:
            link = get_item_from_model(link_type, link_id, model)
            new_evidence.set_linked_item(link)

        target_id = evidence_node.get("target_id")
        target_type = evidence_node.get("target_type")
        if target_id and target_type:
            target = get_item_from_model(target_type, target_id, model)
            new_evidence.set_target(target)

        # Add all references if present
        reference_list_node = evidence_node.find(ge_listOfReferenceLinks)
        if reference_list_node is not None:
            for refLink_node in reference_list_node.iterfind(ge_referenceLink):
                new_evidence.add_reference(model.references[refLink_node.get("id")])

        model.all_evidences[new_evidence.internal_id] = new_evidence


def add_linked_item(linked_items_list_node, item, item_type):
    SubElement(linked_items_list_node, item_type,
               attrib={"id": item.id,
                       "type": type(item).__name__})


def get_item_from_model(item_type, item_id, model):
    """ Return the appropriate item from the model according to the specified
    item type and item id.

    Parameters
    ----------
    item_type : str
    item_id : str
    model : GEMEditor.cobraClasses.Model

    Returns
    -------
    item : GEMEditor.cobraClasses.Reaction, GEMEditor.cobraClasses.Metabolite, GEMEditor.cobraClasses.Gene, GEMEditor.cobraClasses.Model

    Raises
    ------
    ValueError
        If item_type is not "Reaction", "Model", "Gene", "GeneGroup" or "Metabolite"
    KeyError
        If item id is not present in the corresponding collection
    """

    if item_type == "Reaction":
        return model.reactions.get_by_id(item_id)
    elif item_type == "Metabolite":
        return model.metabolites.get_by_id(item_id)
    elif item_type == "Gene":
        return model.genes.get_by_id(item_id)
    elif item_type == "GeneGroup":
        raise NotImplementedError
    elif item_type == "Model":
        return model
    elif item_type == "Compartment":
        return model.compartments[item_id]
    else:
        raise ValueError("Unexpected item type '{0}' with id {1}".format(item_type, item_id))
