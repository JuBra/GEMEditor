from GEMEditor.rw import *
from GEMEditor.rw.sbml3 import setup_sbml3_node


class TestSetupModel:

    def test_node_addition(self):
        sbml_node = setup_sbml3_node()

        assert sbml_node.tag == sbml3_sbml
        assert sbml_node.get("level") == "3"
        assert sbml_node.get("sboTerm") == "SBO:0000624"
        assert sbml_node.get("version") == "1"
        assert sbml_node.get(fbc_required) == "false"








