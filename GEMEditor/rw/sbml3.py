import logging
import lxml.etree as ET
from GEMEditor.model.classes.cobra import Compartment
from GEMEditor.rw import *
from GEMEditor.rw.compartment import add_compartments, parse_compartments
from GEMEditor.rw.evidences import add_evidences_to_xml, parse_evidences_from_xml
from GEMEditor.rw.fluxset import add_tests_to_xml, parse_test_from_xml
from GEMEditor.rw.gene import add_genes, parse_genes
from GEMEditor.rw.metabolite import add_metabolites, parse_metabolites
from GEMEditor.rw.model import setup_sbml3_model, parse_model_info
from GEMEditor.rw.reaction import add_reactions, parse_reaction
from GEMEditor.rw.reference import add_references, parse_references
from GEMEditor.rw.units import add_unit_definitions
from PyQt5.QtWidgets import QProgressDialog
from lxml.etree import Element, register_namespace, ElementTree


LOGGER = logging.getLogger(__name__)


def setup_sbml3_node():
    sbml_node = Element(sbml3_sbml, attrib={"level": "3", "version": "1", "sboTerm": "SBO:0000624", fbc_required: "false"}, nsmap=nsmap)

    for key in nsmap:
        register_namespace(key, nsmap[key])

    return sbml_node


def write_sbml3_model(path, model, progress=None):
    """ Save current model to SBML file

    Parameters
    ----------
    path: str
    model: GEMEditor.model.classes.cobra.Model
    progress: QProgressDialog

    Returns
    -------
    Element
    """

    LOGGER.debug("Saving file: {}".format(path))

    # Setup root SBML node
    sbml_node = setup_sbml3_node()

    # Setup model node
    model_node = setup_sbml3_model(sbml_node, model)

    # Add all model items to the model node
    add_unit_definitions(model_node)
    add_compartments(model_node, model)
    add_metabolites(model_node, model)
    add_genes(model_node, model)
    add_reactions(model_node, model)
    add_references(model_node, model)
    add_tests_to_xml(model_node, model)
    add_evidences_to_xml(model_node, model)

    # Write model to path
    LOGGER.debug("Writing file..")
    with open(path, "wb") as write_file:
        ElementTree(sbml_node).write(write_file, pretty_print=True, encoding="UTF-8", xml_declaration=True)
    LOGGER.debug("Model saved.")

    return sbml_node


def read_sbml3_model(parser, model, path, progress):
    """ Read SBML model

    Parameters
    ----------
    parser: GEMEditor.rw.parser.BaseParser,
        Parser object reading file
    model: GEMEditor.model.classes.Model,
        Model being read
    path: str
        Path to model file
    progress: QProgressDialog
        Progress dialog

    """

    # Read file
    with open(path, "r", encoding="UTF-8") as open_file:
        tree = ET.parse(open_file)

    # Get SBML node
    sbml_node = tree.getroot()
    if sbml_node.tag is None or sbml_node.tag != sbml3_sbml:
        parser.error("The file does not contain a sbml3 model")
        return

    # Get model node
    model_node = sbml_node.find(sbml3_model)
    if model_node is None:
        parser.error("No model node found!")
        return

    # Parse model information
    parse_model_info(parser, model, model_node, progress)
    parse_references(parser, model, model_node, progress)
    parse_compartments(parser, model, model_node, progress)
    parse_metabolites(parser, model, model_node, progress)
    parse_genes(parser, model, model_node, progress)
    parse_reactions(parser, model, model_node, progress)
    parse_test_cases(parser, model, model_node, progress)
    parse_evidences(parser, model, model_node, progress)

    model_node, model = returned_values

    # Parse GEM Editor related stuff
    parsing_functions = [parse_references, parse_compartments, parse_metabolites,
                         parse_genes, parse_reaction, parse_test_from_xml, parse_evidences_from_xml]

    for parse_function in parsing_functions:
        if progress is None:
            parse_function(model_node, model)
        elif not progress.wasCanceled():
            parse_function(model_node, model, progress)
        else:
            return

    # Add compartments from metabolites if not saved
    for x in model.metabolites:
        if x.compartment not in model.gem_compartments:
            model.gem_compartments[x.compartment] = Compartment(x.compartment, None)

    model.setup_tables()
    return model
