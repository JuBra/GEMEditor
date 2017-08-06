import re
from lxml.etree import SubElement
from GEMEditor.rw import *
from GEMEditor.rw.annotation import annotate_xml_from_model, annotate_element_from_xml
from GEMEditor.cobraClasses import Metabolite
from GEMEditor import formula_validator
from cobra.io.sbml3 import clip
from PyQt5.QtWidgets import QApplication


def add_metabolites(model_node, model, use_fbc=True):
    # add in metabolites
    species_list = SubElement(model_node, sbml3_listOfSpecies)
    for met in model.metabolites:
        metabolite_node = SubElement(species_list, sbml3_species,
                             attrib={"id": "M_" + met.id,
                                     "constant": "false",
                                     "boundaryCondition": "false",
                                     "hasOnlySubstanceUnits": "false"})

        # Add optional attributes
        if met.name:
            metabolite_node.set("name", met.name)
        if met.compartment:
            metabolite_node.set("compartment", met.compartment)

        # Set fbc specific attributes
        if use_fbc:
            if met.charge != 0:
                metabolite_node.set(fbc_charge, str(met.charge))
            if met.formula:
                metabolite_node.set(fbc_chemicalFormula, met.formula)

        # Add the annotation
        annotate_xml_from_model(metabolite_node, met)


def parse_metabolites(metabolites_node, model=None, progress=None, use_fbc=True):

    species_node = metabolites_node.find(sbml3_listOfSpecies)

    if species_node is None:
        return
    elif progress is None:
        pass
    elif not progress.wasCanceled():
        progress.setLabelText("Reading metabolites...")
        progress.setRange(0, len(species_node))
    else:
        return

    metabolites = []
    for i, xml_element in enumerate(species_node.iterfind(sbml3_species)):

        if progress is None:
            pass
        elif not progress.wasCanceled():
            progress.setValue(i)
            QApplication.processEvents()
        else:
            return

        new_metabolite = Metabolite(id=clip(xml_element.get("id"), "M_"),
                                    name=xml_element.get("name"),
                                    compartment=xml_element.get("compartment"))

        if use_fbc:
            formula = xml_element.get(fbc_chemicalFormula)
            if formula:
                if re.match(formula_validator, formula):
                    new_metabolite.formula = formula
                else:
                    # Todo: Implement logging of errors
                    print("Formula '{}' for {} is invalid!".format(formula, new_metabolite.id))

            charge = xml_element.get(fbc_charge)
            if charge is not None:
                new_metabolite.charge = int(charge)
            # Defaults to the standard value of 0 if charge not set in file

        annotate_element_from_xml(xml_element, new_metabolite)

        metabolites.append(new_metabolite)

    if model is not None:
        model.add_metabolites(metabolites)

    return metabolites
