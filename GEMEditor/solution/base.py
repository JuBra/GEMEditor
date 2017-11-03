from cobra.core import LegacySolution, Solution


def set_status_to_label(label, status):
    """ Set the status to label

    Parameters
    ----------
    label: QLabel
    status: str

    Returns
    -------

    """
    if status == "optimal":
        label.setStyleSheet("color: ForestGreen; font-weight: bold;")
    else:
        label.setStyleSheet("")
    label.setText(status)


def set_objective_to_label(label, objective):
    """ Set objective to label

    Parameters
    ----------
    label: QLabel
    objective: float or str

    Returns
    -------
    None
    """
    try:
        label.setText("{0:.2f}".format(objective))
    except TypeError:
        label.setText("{0!s}".format(objective))


def status_objective_from_solution(solution):
    """ Get the status and objective from solution

    Parameters
    ----------
    solution: Solution or LegacySolution

    Returns
    -------
    status: str
    objective: str or float
    """
    if isinstance(solution, LegacySolution):
        status, objective = solution.status, solution.f
    elif isinstance(solution, Solution):
        status, objective = solution.status, solution.objective_value
    else:
        status, objective = "No solution set", "-"
    return str(status), objective


def fluxes_from_solution(solution):
    """ Get the stored flux values from solution

    Parameters
    ----------
    solution: Solution or LegacySolution

    Returns
    -------
    fluxes: dict or panda.Series
    """
    if isinstance(solution, LegacySolution):
        fluxes = solution.x_dict
    elif isinstance(solution, Solution):
        fluxes = solution.fluxes
    else:
        raise TypeError("Expected LegacySolution or Solution object")
    return fluxes


def shadow_prices_from_solution(solution):
    """ Get the shadow prices from solution

    Parameters
    ----------
    solution: Solution or LegacySolution

    Returns
    -------
    prices: dict or panda.Series
    """
    if isinstance(solution, LegacySolution):
        prices = solution.y_dict
    elif isinstance(solution, Solution):
        prices = solution.shadow_prices
    else:
        raise TypeError("Expected LegacySolution or Solution object")
    return prices
