from collections import defaultdict
from GEMEditor.cobraClasses import GeneGroup


def get_reaction_set(reaction, remove_directionality=True):
    """ Get the the reaction stoichiometries from a reaction

    Parameters
    ----------
    reaction : GEMEditor.cobraClasses.Reaction
    remove_directionality: bool

    Returns
    -------
    frozenset
    """
    substrates = []
    products = []
    for metabolite, coefficient in reaction.metabolites.items():
        if coefficient > 0:
            products.append((metabolite, coefficient))
        elif remove_directionality:
            substrates.append((metabolite, abs(coefficient)))
        else:
            substrates.append((metabolite, coefficient))
    return frozenset([frozenset(substrates), frozenset(products)])


def group_duplicate_reactions(list_of_reations):
    """ Find duplicates of the individual reactions

    Parameters
    ----------
    list_of_reations : list

    Returns
    -------

    """

    if not isinstance(list_of_reations, list):
        raise TypeError("The input is not a list!")

    result_dict = defaultdict(list)

    for reaction in list_of_reations:
        result_dict[get_reaction_set(reaction, remove_directionality=True)].append(reaction)
    return result_dict


def extract_genes_from_reaction(reaction):
    """ Remove all genes from a reaction an get a new genegroup from it

    Parameters
    ----------
    reaction: GEMEditor.cobraClasses.Reaction

    Returns
    -------

    """
    if not reaction._children:
        return None
    elif len(reaction._children) == 1:
        child = list(reaction._children)[0]
        child.remove_parent(reaction, all=False)
        return child

    new_genegroup = GeneGroup(type="or")
    for element in reaction._children:
        element.remove_parent(reaction, all=False)
        element.add_parent(new_genegroup)
    return new_genegroup


def merge_reactions(list_of_reactions, base_reaction):
    """ Merge duplicated reactions

    Parameters
    ----------
    list_of_reactions: list, list of reactions that should be merged
    base_reaction: GEMEditor.cobraClasses.Reaction, Reaction to keep

    Returns
    -------

    """

    # Move all genes of the base reaction to new gene group
    temp_children = []

    base_reaction_children = extract_genes_from_reaction(base_reaction)
    if base_reaction_children is not None:
        temp_children.append(base_reaction_children)

    for reaction in list_of_reactions:
        if reaction is not base_reaction:
            # Add annotations
            base_reaction.annotation.update(reaction.annotation)
            # Add genes
            genes = extract_genes_from_reaction(reaction)
            if genes is not None:
                temp_children.append(genes)
            # Move evidences
            for evidence in tuple(reaction.evidences):
                if evidence.entity is reaction:
                    evidence.set_entity(base_reaction)
                elif evidence.link is reaction:
                    evidence.set_linked_item(base_reaction)
                elif evidence.target is reaction:
                    evidence.set_target(base_reaction)
            try:
                reaction.remove_from_model()
            except Exception:
                pass

    # Add new genes to base reaction
    if len(temp_children) > 1:
        combined_genes = GeneGroup(type="or")
        for element in temp_children:
            combined_genes.add_child(element)
        base_reaction.add_child(combined_genes)
    elif len(temp_children) == 1:
        base_reaction.add_child(temp_children[0])
