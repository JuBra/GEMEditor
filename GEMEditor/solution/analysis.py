

def get_turnover(fluxes, metabolite):
    """ Calculate the turnover for a specific metabolite

    Parameters
    ----------
    fluxes: dict or pandas.Series
    metabolite: GEMEditor.cobraClasses.Metabolite

    Returns
    -------
    float
    """
    sum_rates = 0

    for reaction in metabolite.reactions:
        rate = fluxes[reaction.id] * reaction.metabolites[metabolite]
        sum_rates += abs(rate)

    return sum_rates / 2
