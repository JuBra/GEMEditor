

def get_reaction_set(reaction, remove_directionality=False):
    """ Get a frozen set containing subsets of the substrates and products

    Parameters
    ----------
    reaction: GEMEditor.model.classes.cobra.Reaction
        Reaction instance for which to generate the frozenset
    remove_directionality: bool
        Specify if the directionality of the reaction should be considered

    Returns
    -------
    frozenset
    """
    if remove_directionality:
        substrates = [(element[0], abs(element[1])) for element in reaction.metabolites.items() if element[1] < 0]
    else:
        substrates = [element for element in reaction.metabolites.items() if element[1] < 0]
    products = [element for element in reaction.metabolites.items() if element[1] > 0]
    return frozenset([frozenset(substrates), frozenset(products)])
