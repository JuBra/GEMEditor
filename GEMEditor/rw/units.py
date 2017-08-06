from GEMEditor.rw import *
from lxml.etree import SubElement


def add_unit_definitions(model_node):
    unit_definitions_node = SubElement(SubElement(model_node, sbml3_listOfUnitDefinitions), sbml3_unitDefinition,
                          attrib={"id": "mmol_per_gDW_per_hr"})

    list_of_units = SubElement(unit_definitions_node, sbml3_listOfUnits)
    SubElement(list_of_units, sbml3_unit, attrib={"kind": "mole", "scale": "-3", "multiplier": "1", "exponent": "1"})
    SubElement(list_of_units, sbml3_unit, attrib={"kind": "gram", "scale": "0", "multiplier": "1", "exponent": "-1"})
    SubElement(list_of_units, sbml3_unit, attrib={"kind": "second", "scale": "0", "multiplier": "3600", "exponent": "-1"})

    return list_of_units
