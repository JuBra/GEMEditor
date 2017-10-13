import logging
from GEMEditor.base.functions import check_element_balance


LOGGER = logging.getLogger(__name__)


def update_formula_from_neighborhood(metabolite):
    """ Calculate the formula of a metabolite from linked reactions

    Parameters
    ----------
    metabolite: GEMEditor.cobraClasses.Metabolite

    Returns
    -------
    return_value: bool, True if the metabolite has been updated, False otherwise
    """

    putative_formulas = set()

    for reaction in metabolite.reactions:
        if len(reaction.metabolites) < 2 or sum([not x.formula for x in reaction.metabolites]) > 1:
            # Can not retrieve formula in case of:
            # - more than 1 metabolites without formula
            # - reaction is a boundary reaction
            continue
        else:
            putative_formula = ""
            elemental_imbalance = check_element_balance(reaction.metabolites)
            for key, count in sorted(elemental_imbalance.items(), key=lambda x: x[0]):
                if abs(count) == 1:
                    count_str = ""
                else:
                    count_str = str(abs(count))

                putative_formula += "".join((key, count_str))

            if putative_formula:
                putative_formulas.add(putative_formula)

    if len(putative_formulas) == 1:
        metabolite.formula = putative_formulas.pop()
        return True
    else:
        return False


def update_formulae_iteratively(model):
    """ Update the metabolite formula iteratively

    Update the formulae of metabolites where no formula
    is set. As an updated metabolite might lead to another
    formula being determined run iteratively until no new
    formula can be set.

    Parameters
    ----------
    model: GEMEditor.cobraClasses.Model

    Returns
    -------
    return_value: list, Updated metabolites
    """

    formula_missing = [m for m in model.metabolites if not m.formula]

    n = 0
    while any([update_formula_from_neighborhood(m)
               for m in model.metabolites if not m.formula]):
        n += 1
        LOGGER.debug("Iteration {0!s}".format(n))

    return [m for m in formula_missing if m.formula]



