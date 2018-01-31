from collections import defaultdict


def get_rates(fluxes, metabolite):
    """ Calculate the rates of the individual reactions

    Parameters
    ----------
    fluxes: dict or pandas.Series
    metabolite: GEMEditor.model.classes.cobra.Metabolite

    Returns
    -------
    rates: dict,
        Partial rates of the individual reactions
    """

    rates = dict()

    for reaction in metabolite.reactions:
        rates[reaction] = float(fluxes[reaction.id] * reaction.metabolites[metabolite])

    return rates


def get_turnover(fluxes, metabolite):
    """ Calculate the turnover for a specific metabolite

    Parameters
    ----------
    fluxes: dict or pandas.Series
    metabolite: GEMEditor.model.classes.cobra.Metabolite

    Returns
    -------
    float:
        Turnover of the metabolite
    """

    rates = get_rates(fluxes, metabolite)
    sum_rates = sum(abs(x) for x in rates.values())

    return float(sum_rates / 2)


def get_yields(fluxes, model):
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
    fluxes :
    model : GEMEditor.model.classes.cobra.Model

    Returns
    -------
    status : bool
    yields : dict
    """

    total_rates = defaultdict(float)
    elemental_influxes = defaultdict(float)
    yields = defaultdict(dict)

    for reaction in model.reactions:
        # Only process boundary reactions
        if not reaction.boundary:
            continue

        # Only process active reactions
        flux_value = fluxes[reaction.id]
        if flux_value == 0.:
            continue

        # Allow for reaction to have multiple metabolites
        for metabolite, coefficient in reaction.metabolites.items():
            total_rates[metabolite] += flux_value * coefficient

    # Status should be true if there have been no problems
    status = True

    for metabolite, rate in sorted(total_rates.items(), key=lambda x: x[1], reverse=True):  # Sorting needed for correct calculation
        elements = metabolite.elements

        if rate > 0.:  # Metabolite is substrate
            # Check formula is set for metabolite
            if not elements:
                status = False
                break

            # Add elemental rates
            for key, value in elements.items():
                elemental_influxes[key] += value * rate

        elif rate < 0.:  # Metabolite is product
            if not elements:
                continue

            for element, stoichiometry in elements.items():
                yields[element][metabolite] = abs((stoichiometry * rate) / elemental_influxes[element])

    return status, yields
