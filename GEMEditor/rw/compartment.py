from lxml.etree import SubElement
from six import iteritems
from GEMEditor.rw import *
from GEMEditor.data_classes import Compartment


def add_compartments(model_node, model):
    """ Write the content of the model compartment
    dictionary to the xml file by adding an sbml
    listOfComartments node and adding all compartments to it"""

    # Check that all compartments are actually present in the list
    compartments = set([metabolite.compartment for metabolite in model.metabolites])
    for x in compartments:
        if x not in model.gem_compartments:
            model.gem_compartments[x] = None
    if len(model.gem_compartments) > 0:
        compartmenst_list = SubElement(model_node, sbml3_listOfCompartments)
        for id, compartment in iteritems(model.gem_compartments):
            compartment_node = SubElement(compartmenst_list, sbml3_compartment, id=id,
                                          constant="true")
            if compartment.name:
                compartment_node.set("name", compartment.name)


def parse_compartments(model_node, model=None, progress=None):
    """ Parse the compartment list if found and add
    all compartments to the model.gem_compartments dictionary """

    compartment_list_node = model_node.find(sbml3_listOfCompartments)

    compartments = {}
    if compartment_list_node is not None:
        for compartment_node in compartment_list_node.iterfind(sbml3_compartment):
            compartment = Compartment(id=compartment_node.get("id"),
                                      name=compartment_node.get("name"))
            if model is not None:
                model.gem_compartments[compartment.id] = compartment
            else:
                compartments[compartment.id] = compartment
    return compartments
