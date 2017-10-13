import logging
from lxml.etree import SubElement
from GEMEditor.cobraClasses import Gene, GeneGroup, Reaction
from GEMEditor.rw.annotation import annotate_xml_from_model, annotate_element_from_xml
from GEMEditor.rw import *
from cobra.io.sbml3 import strnum, SBML_DOT, clip
from six import iteritems
from collections import defaultdict
from warnings import warn
from PyQt5.QtWidgets import QApplication


LOGGER = logging.getLogger(__name__)


def add_reactions(model_node, model, use_fbc=True):

    if len(model.reactions) > 0:

        bounds_map = _add_parameters(model_node, model)

        objectives_list_node = SubElement(model_node, fbc_listOfObjectives, attrib={fbc_activeObjective: "obj"})
        objective_node = SubElement(objectives_list_node, fbc_objective, attrib={fbc_id: "obj", fbc_type: "maximize"})
        list_of_fluxobjectives = SubElement(objective_node, fbc_listOfFluxObjectives)
        reactions_list_node = SubElement(model_node, sbml3_listOfReactions)

        for reaction in model.reactions:

            reaction_id = cobra_reaction_prefix + reaction.id
            reaction_node = SubElement(reactions_list_node, sbml3_reaction,
                                       attrib={"id": reaction_id,
                                               "fast": "false",
                                               "reversible": str(reaction.lower_bound < 0).lower()})
            # Optional attributes
            if reaction.name:
                reaction_node.set("name", reaction.name)
            if reaction.subsystem:
                reaction_node.set(ge_subsystem, reaction.subsystem)
            if reaction.comment:
                reaction_node.set(ge_comment, reaction.comment)

            if use_fbc:
                reaction_node.set(fbc_lowerFluxBound, bounds_map[reaction.lower_bound])
                reaction_node.set(fbc_upperFluxBound, bounds_map[reaction.upper_bound])

            # Add reaction to flux_objectives_node if the coefficient is not 0
            if reaction.objective_coefficient != 0.:
                SubElement(list_of_fluxobjectives, fbc_fluxObjective,
                           attrib={fbc_reaction: reaction_id,
                                   fbc_coefficient: strnum(reaction.objective_coefficient)})

            # Add metabolites to reaction node
            reaction_sides = defaultdict(list)
            for met, coefficient in sorted(iteritems(reaction._metabolites), key=lambda x: x[0].id):
                met_id = "M_" + met.id
                if coefficient < 0:
                    reaction_sides[sbml3_listOfReactants].append({"species": met_id,
                                                                  "stoichiometry": strnum(abs(coefficient)),
                                                                  "constant": "true"})
                else:
                    reaction_sides[sbml3_listOfProducts].append({"species": met_id,
                                                                 "stoichiometry": strnum(abs(coefficient)),
                                                                 "constant": "true"})

            for key, participants in iteritems(reaction_sides):
                reaction_side = SubElement(reaction_node, key)
                for attrib_dict in participants:
                    SubElement(reaction_side, sbml3_speciesReference, attrib=attrib_dict)

            # Add genes
            if reaction._children:
                genes_node = SubElement(reaction_node, fbc_geneProductAssociation)
                _parse_gene_object_tree(genes_node, reaction)

            # Add gene annotations
            annotate_xml_from_model(reaction_node, reaction)


def _parse_gene_object_tree(tree_node, root_item, level=0):

    if level == 0 and len(root_item._children) > 1:
        _parse_gene_object_tree(SubElement(tree_node, fbc_or), root_item, level=1)
        return
    else:
        for element in root_item._children:
            if isinstance(element, GeneGroup):
                if element.type == "or":
                    new_node = SubElement(tree_node, fbc_or, attrib={ge_id: element.id})
                elif element.type == "and":
                    new_node = SubElement(tree_node, fbc_and, attrib={ge_id: element.id})
                else:
                    raise ValueError("Unknown group type!")
                _parse_gene_object_tree(new_node, element, level=level + 1)
            elif isinstance(element, Gene):
                SubElement(tree_node, fbc_geneProductRef, attrib={fbc_geneProduct: cobra_gene_prefix + element.id.replace(".", SBML_DOT)})


def _parse_gene_xml_tree(node, reaction, genes):
    """ Parse the gene tree as saved in an sbml file with fbc package """

    # Check that
    if node.tag == fbc_geneProductAssociation:
        top_level_child = _parse_gene_xml_tree(node.getchildren()[0], reaction, genes)
        reaction.add_child(top_level_child)
    elif node.tag in (fbc_and, fbc_or):
        gene_group = GeneGroup(id=node.get(ge_id), type="and" if node.tag == fbc_and else "or")
        for child in node.getchildren():
            child_object = _parse_gene_xml_tree(child, reaction, genes)
            gene_group.add_child(child_object)
        return gene_group

    elif node.tag == fbc_geneProductRef:
        gene_id = clip(node.attrib[fbc_geneProduct], "G_")
        # Resubstitute dots
        gene_id = gene_id.replace(SBML_DOT, ".")
        try:
            return genes.get_by_id(gene_id)
        except KeyError:
            new_gene = Gene(id=gene_id, name=gene_id)
            genes.append(new_gene)
            warn("Gene {0} not found in gene list. New gene created!".format(gene_id))
            return new_gene
    else:
        raise TypeError("Unknown node.tag {0} at line {1}".format(node.tag, node.sourceline))


def parse_reaction(model_node, model, progress=None):
    """ Parse cobra reactions from a sbml file """

    LOGGER.debug("Reading reactions..")

    reaction_list_node = model_node.find(sbml3_listOfReactions)
    boundary_list_node = model_node.find(sbml3_listOfParameters)
    objectives_list_node = model_node.find(fbc_listOfObjectives)

    # Read objectives
    objectives = {}
    if objectives_list_node is not None:
        objective = objectives_list_node.find(fbc_objective)
        if objective is not None:
            list_of_flux_objectives = objective.find(fbc_listOfFluxObjectives)
            if list_of_flux_objectives is not None:
                for child in list_of_flux_objectives.iterfind(fbc_fluxObjective):
                    if child.get(fbc_reaction):
                        objectives[clip(child.get(fbc_reaction), "R_")] = child.get(fbc_coefficient) or 0.

    # Read flux boundaries
    boundary_dict = {}
    for child in boundary_list_node.iterfind(sbml3_parameter):
        value = child.get("value")
        if value is not None:
            boundary_dict[child.get("id")] = float(value)

    reactions = []
    if reaction_list_node is None:
        return
    elif progress is None:
        pass
    elif not progress.wasCanceled():
        progress.setLabelText("Reading reactions...")
        progress.setRange(0, len(reaction_list_node))
    else:
        return

    for i, reaction_node in enumerate(reaction_list_node.iterfind(sbml3_reaction)):

        if progress is None:
            pass
        elif not progress.wasCanceled():
            progress.setValue(i)
            QApplication.processEvents()
        else:
            return

        reaction_id = clip(reaction_node.get("id"), "R_")
        new_reaction = Reaction(id=reaction_id,
                                name=reaction_node.get("name"),
                                upper_bound=float(boundary_dict[reaction_node.get(fbc_upperFluxBound)]),
                                lower_bound=float(boundary_dict[reaction_node.get(fbc_lowerFluxBound)]),
                                subsystem=reaction_node.get(ge_subsystem),
                                comment=reaction_node.get(ge_comment))

        # Add metabolites
        metabolites = {}
        for x in [sbml3_listOfReactants, sbml3_listOfProducts]:
            metabolite_list = reaction_node.find(x)
            if metabolite_list is not None:
                for metabolite_node in metabolite_list.iterfind(sbml3_speciesReference):
                    metabolite = model.metabolites.get_by_id(clip(metabolite_node.get("species"), "M_"))
                    value = float(metabolite_node.get("stoichiometry"))
                    if x == sbml3_listOfReactants:
                        value = -value
                    metabolites[metabolite] = value
        new_reaction.add_metabolites(metabolites)

        # Add balancing status
        new_reaction.update_balancing_status()

        # Add genes
        gene_node = reaction_node.find(fbc_geneProductAssociation)
        if gene_node is not None:
            _parse_gene_xml_tree(gene_node, new_reaction, model.genes)

        # Parse annotation
        annotate_element_from_xml(reaction_node, new_reaction)

        reactions.append(new_reaction)

    model.add_reactions(reactions)
    LOGGER.debug("Reactions added to model!")

    for key, value in objectives.items():
        try:
            reaction = model.reactions.get_by_id(key)
        except KeyError:
            LOGGER.warning("Reaction {} not existing in the model, but listed in objectives!".format(key))
            continue
        else:
            reaction.objective_coefficient = float(value)

    return reactions


def _bound_name(number):
    return "{sign}_{value}".format(sign="neg" if number < 0 else "pos",
                                   value=str(abs(number)))


def _add_parameters(model_node, model):

    parameter_list = SubElement(model_node, sbml3_listOfParameters)
    param_attr = {"constant": "true",
                  "units": "mmol_per_gDW_per_hr"}

    bounds = set(model.reactions.list_attr("lower_bound")).union(model.reactions.list_attr("upper_bound"))
    bounds_map = {}

    # Add standard boundaries
    for value, name, sboTerm in cobra_standard_boundaries:
        _add_bound(parameter_list, value=value, name=name, sboTerm=sboTerm, param_attr=param_attr)
        bounds_map[value] = name
        bounds.discard(value)

    # Add all other boundaries
    for value in bounds:
        name = _bound_name(value)
        _add_bound(parameter_list, value, name, param_attr)
        bounds_map[value] = name

    return bounds_map


def _add_bound(parameter_list_node, value, name, param_attr, sboTerm="SBO:0000625"):

    SubElement(parameter_list_node, sbml3_parameter, value=strnum(value),
               id=name, sboTerm=sboTerm, **param_attr)
