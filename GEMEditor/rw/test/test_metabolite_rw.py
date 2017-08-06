import pytest
from GEMEditor.rw import *
from GEMEditor.cobraClasses import Metabolite, Model
from GEMEditor.rw.metabolite import add_metabolites, parse_metabolites
from GEMEditor.rw.test.ex_metabolite import valid_metabolite_with_annotation, valid_metabolite_wo_annotation
from GEMEditor.data_classes import Annotation
from cobra.io.sbml3 import strnum
from lxml.etree import Element
import lxml.etree as ET


class TestMetaboliteIO:

    @pytest.fixture(autouse=True)
    def setup_items(self):

        self.test_id = "test_id"
        self.test_name = "test_name"
        self.test_formula = "H2O"
        self.test_charge = 0
        self.test_compartment = "t"
        self.metabolite = Metabolite(id=self.test_id,
                                     name=self.test_name,
                                     formula=self.test_formula,
                                     charge=self.test_charge,
                                     compartment=self.test_compartment)

        self.annotation1 = Annotation("chebi", "CHEBI:37671")
        self.metabolite.annotation.add(self.annotation1)

        self.model = Model("Test")
        self.model.add_metabolites([self.metabolite])
        self.root = Element("root")

    def test_setup(self):

        assert self.metabolite.id == self.test_id
        assert self.metabolite.name == self.test_name
        assert self.metabolite.formula == self.test_formula
        assert self.metabolite.compartment == self.test_compartment
        assert self.metabolite.charge == self.test_charge

        assert len(self.model.metabolites) == 1
        assert len(self.metabolite.annotation) == 1
        assert isinstance(self.metabolite.annotation, set)
        assert self.annotation1 in self.metabolite.annotation

    def test_adding_metabolites_to_xml(self):

        add_metabolites(self.root, self.model)

        assert len(self.root) == 1

        metabolite_list_node = self.root.find(sbml3_listOfSpecies)
        assert metabolite_list_node is not None
        assert len(metabolite_list_node) == 1

        metabolite = metabolite_list_node.find(sbml3_species)
        assert metabolite is not None
        assert metabolite.get(fbc_charge) is None
        assert metabolite.get("compartment") == self.test_compartment
        assert metabolite.get(fbc_chemicalFormula) == self.test_formula
        assert metabolite.get("id") == cobra_metabolite_prefix + self.test_id
        assert metabolite.get("name") == self.test_name

        annotation_node = metabolite.find("/".join([sbml3_annotation, rdf_RDF, rdf_description,
                                                    bqbiol_is, rdf_bag, rdf_li]))
        assert annotation_node is not None
        assert annotation_node.get(rdf_resource) == "http://identifiers.org/chebi/CHEBI:37671"

    def test_addition_of_attributes_only_when_set(self):
        model = Model("Test")
        metabolite = Metabolite(id="test")
        model.add_metabolites([metabolite])

        add_metabolites(self.root, model)

        metabolite_node = self.root.find(sbml3_listOfSpecies+"/"+sbml3_species)
        assert metabolite_node is not None
        assert metabolite_node.get(fbc_charge) is None
        assert metabolite_node.get(fbc_chemicalFormula) is None
        assert metabolite_node.get("name") is None
        assert metabolite_node.get("compartment") is None

    def test_parsing_of_valid_metabolite(self):
        parent_node = ET.fromstring(valid_metabolite_with_annotation)
        metabolites = parse_metabolites(parent_node)
        assert len(metabolites) == 1

        metabolite = metabolites[0]
        assert metabolite.id == "13GLUCAN"
        assert metabolite.name == "1,3-beta-D-Glucan"
        assert metabolite.compartment == "c"
        assert metabolite.formula == "C18H32O16"
        assert metabolite.charge == 0
        assert len(metabolite.annotation) == 3

        assert Annotation("inchi", "InChI=1S/C18H32O16/c19-1-4-7(22)10(25)11(26)17(31-4)34-15-9(24)6(3-21)32-18(13(15)28)33-14-8(23)5(2-20)30-16(29)12(14)27/h4-29H,1-3H2/t4-,5-,6-,7-,8-,9-,10+,11-,12-,13-,14+,15+,16-,17+,18+/m1/s1") in metabolite.annotation
        assert Annotation("chebi", "CHEBI:37671") in metabolite.annotation
        assert Annotation("kegg.compound", "C00965") in metabolite.annotation

    def test_parsing_of_valid_metabolite_wo_annotation(self):
        parent_node = ET.fromstring(valid_metabolite_wo_annotation)
        metabolites = parse_metabolites(parent_node)
        assert len(metabolites) == 1

        metabolite = metabolites[0]
        assert metabolite.id == "13GLUCAN"
        assert metabolite.name == "1,3-beta-D-Glucan"
        assert metabolite.compartment == "c"
        assert metabolite.formula == ""
        assert metabolite.charge == 0

    def test_read_write_consistency(self):

        root = Element("root")
        add_metabolites(root, self.model)

        metabolites = parse_metabolites(root)
        assert len(metabolites) == 1

        metabolite = metabolites[0]
        assert metabolite.id == self.test_id
        assert metabolite.name == self.test_name
        assert metabolite.charge == self.test_charge
        assert metabolite.formula == self.test_formula
        assert isinstance(metabolite.annotation, set)

        assert self.annotation1 in metabolite.annotation
