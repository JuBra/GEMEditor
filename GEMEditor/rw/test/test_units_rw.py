from GEMEditor.rw.units import add_unit_definitions
from lxml.etree import Element
from GEMEditor.rw import *


class TestAddUnitsDefinition:

    def test_node_addition(self):
        root = Element("root")
        add_unit_definitions(root)

        list_of_unitdefinitions_node = root.find(sbml3_listOfUnitDefinitions)
        assert list_of_unitdefinitions_node is not None
        assert len(list_of_unitdefinitions_node) == 1

        unit_definition_node = list_of_unitdefinitions_node.find(sbml3_unitDefinition)
        assert unit_definition_node is not None
        assert unit_definition_node.get("id") == "mmol_per_gDW_per_hr"

        list_of_units_node = unit_definition_node.find(sbml3_listOfUnits)
        assert list_of_units_node is not None
        assert len(list_of_units_node) == 3

        expected_values = set([("1", "mole", "1", "-3"),
                               ("-1", "gram", "1", "0"),
                               ("-1", "second", "3600", "0")])

        found_set = set()
        for child in list_of_units_node.iterfind(sbml3_unit):
            found_set.add((child.get("exponent"), child.get("kind"), child.get("multiplier"), child.get("scale")))

        assert expected_values == found_set