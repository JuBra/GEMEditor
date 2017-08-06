from GEMEditor.rw import *
from lxml.etree import Element, SubElement
from GEMEditor.cobraClasses import Model


def setup_sbml3_model(sbml_node, model):

    model_node = SubElement(sbml_node, sbml3_model, attrib={fbc_strict: "true"})

    if model.id is not None:
        model_node.set("id", model.id)
    if model.name is not None:
        model_node.set("name", model.name)

    return model_node


def parse_sbml3_model(sbml_node):

    if sbml_node is not None:
        model_node = sbml_node.find(sbml3_model)
        if model_node is not None:
            model = Model(id_or_model=model_node.get("id"),
                          name=model_node.get("name"))

            return model_node, model
    return None


