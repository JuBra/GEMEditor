from GEMEditor.model.classes.cobra import Model
from GEMEditor.rw import *
from lxml.etree import SubElement


def setup_sbml3_model(sbml_node, model):

    model_node = SubElement(sbml_node, sbml3_model, attrib={fbc_strict: "true"})

    if model.id is not None:
        model_node.set("id", model.id)
    if model.name is not None:
        model_node.set("name", model.name)

    return model_node


def parse_model_info(parser, model, model_node, progress):
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

    model.id = model_node.get("id")
    model.name = model_node.get("name")
