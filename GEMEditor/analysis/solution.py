from collections import defaultdict
from cobra.core.Formula import Formula


def get_turnover(solution, mapping):
    """ Get the turnover of metabolites

    Calculate the turnover of all metabolites that are mapped
    in the mapping dictionary. The turnover is considered to be the
    net flux all reactions that are neither boundary nor transport
    reactions.


    Parameters
    ----------
    solution : cobra.core.Solution
    mapping : dict

    Returns
    -------
    turnover : dict
    """

    turnover = dict()

    for name, metabolite_list in mapping.items():
        production = 0
        consumption = 0
        for metabolite in metabolite_list:
            for reaction in metabolite.reactions:
                # Only add the flux of reactions that are not boundary
                # or transport reactions
                if reaction.boundary is True or len(reaction.get_compartments()) > 1:
                    continue
                flux = solution[reaction.id] * reaction.stoichiometry[metabolite]
                if flux > 0:
                    production += flux
                elif flux < 0:
                    consumption -= flux

        # Add result to result dictionary
        turnover[name] = production
    return turnover


def get_yields(solution, model):
    """ Calculate the yields for the individual metabolites that are produced

    The function uses the flux values listed in the solution object to calculate
    the net flux for each individual metabolite that is part of a boundary reaction,
    where the net flux is the sum of the stoichiometric coefficient multiplied by the
    flux value of the individual boundary reaction.

    All metabolites with a net influx greater zero are considered products whereas
    all metabolites with a negative net influx are considered substrates.

    The individual fluxes for the elements are calculated by multiplying the net
    metabolite flux with the stoichiometric coefficients of the sum formula of
    the metabolites.

    The elemental fluxes are used for the calculation of yield coefficients of the
    individual elements for all relevant metabolites.

    Parameters
    ----------
    solution :
    model : GEMEditor.cobraClasses.Model

    Returns
    -------
    status : bool
    yields : dict
    """

    overall_fluxes = defaultdict(float)

    for reaction in model.reactions:
        # Only process boundary reactions
        if reaction.boundary is False:
            continue

        flux_value = solution[reaction.id]
        # Allow for reaction to have multiple metabolites
        for metabolite, stoichiometry in reaction.stoichiometry.items():
            overall_fluxes[metabolite] += flux_value * stoichiometry

    elemental_influxes = defaultdict(float)

    # Status should be true if there have been no problems
    status = True

    for metabolite, flux in overall_fluxes.items():
        if flux > 0.:
            # Metabolite is a substrate
            if not metabolite.formula:
                status = False
                break
            else:
                elements = Formula(metabolite.formula).elements
                for key, value in elements.items():
                    elemental_influxes[key] += value * flux

    yields = dict()
    for metabolite, flux in overall_fluxes.items():
        if flux < 0.:
            # Metabolite is a product
            if metabolite.formula:
                elements = Formula(metabolite.formula).elements
                yields[metabolite] = dict()
                for element, stoichiometry in elements.items():
                    yields[metabolite][element] = (stoichiometry * flux) / elemental_influxes[element]
    return status, yields



