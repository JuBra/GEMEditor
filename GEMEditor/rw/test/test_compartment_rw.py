import pytest
from GEMEditor.rw import *
from GEMEditor.cobraClasses import Model, Metabolite, Compartment
from GEMEditor.data_classes import Compartment
import lxml.etree as ET
from lxml.etree import Element

from GEMEditor.rw.compartment import add_compartments, parse_compartments
from GEMEditor.rw.test.ex_compartment import valid_compartment_list


def test_parse_compartments():
    parent_node = ET.fromstring(valid_compartment_list)
    model = Model()
    parse_compartments(parent_node, model)

    assert model.compartments["p"] == Compartment("p", "Periplasm")
    assert model.compartments["c"] == Compartment("c", "Cytoplasm")
    assert model.compartments["e"] == Compartment("e", "Extracellular")


def test_add_compartments():
    model = Model()
    model.compartments["c"] = Compartment("c", "Cytoplasm")

    root = Element("Root")
    add_compartments(root, model)

    compartment_list = root.find(sbml3_listOfCompartments)
    assert compartment_list is not None

    compartment = compartment_list.find(sbml3_compartment)
    assert compartment is not None
    assert compartment.get("id") == "c"
    assert compartment.get("name") == "Cytoplasm"


def test_add_compartments_defined_in_metabolite():
    model = Model()
    metabolite = Metabolite(id="test", compartment="c")
    model.add_metabolites([metabolite])

    root = Element("Root")
    add_compartments(root, model)

    compartment_list = root.find(sbml3_listOfCompartments)
    assert compartment_list is not None

    compartment = compartment_list.find(sbml3_compartment)
    assert compartment is not None
    assert compartment.get("id") == "c"
    assert compartment.get("name") is None


def test_add_compartment_empty_model():
    model = Model()

    root = Element("root")
    add_compartments(root, model)

    compartment_list = root.find(sbml3_listOfCompartments)
    assert compartment_list is None


def test_consistency_write_read():
    model1 = Model()
    model1.compartments["c"] = Compartment("c", "Cytoplasm")

    root = Element("Root")
    add_compartments(root, model1)

    model2 = Model()
    parse_compartments(root, model2)

    assert model2.compartments == model1.compartments
