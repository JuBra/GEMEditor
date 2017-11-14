from GEMEditor.model.classes.modeltest import ReactionSetting


def run_test(test_case, model, solver, restore_initial=False):
    """ Run a specific model test case.

    The objective values of all reactions are set to zero before
    the test, as well as the upper and lower bounds of all boundary
    reactions.
    If restore_initials is True this changes will be
    performed during the test, otherwise the function expects a
    model that already meets these criteria. """

    # Store original values of boundary reactions and
    # reactions with objective coefficient != 0. in list
    if restore_initial:
        original_settings = get_original_settings(model)
        for x in original_settings:
            x.do()

    # Execute all settings
    for setting in test_case.all_settings():
        setting.do()

    # Solve the model
    solution = model.optimize(solver=solver)

    # Revert test specific changes
    for setting in reversed(test_case.all_settings()):
        setting.undo()

    # Restore original values
    if restore_initial:
        for setting in reversed(original_settings):
            setting.undo()

    if solution.x_dict is not None:
        return all([x.check_solution(solution) for x in test_case.outcomes]), solution
    else:
        return False, solution


def get_original_settings(model):
    """ Get all settings needed to prepare for test run

    In the preparation for running test cases care should
    be taken that:

    1) All objective coefficients should be set to 0
    2) All boundary reactions are producing only

    Both the active boundary reactions and the objective
    coefficients need to be specified in the settings of
    the test cases.

    Returns
    -------
    original_settings: list,
        List of settings that need to be executed in order
        to prepare the model for running tests, and should
        be reversed afterwards
    """

    original_settings = []

    for x in model.reactions:

        # Set all boundary reaction to producing only
        if all(v < 0. for v in x.metabolites.values()):
            original_settings.append(ReactionSetting(x, x.upper_bound, 0., 0.))
        elif all(v > 0. for v in x.metabolites.values()):
            original_settings.append(ReactionSetting(x, 0., x.lower_bound, 0.))
        # Set all objective coefficients to zero
        elif x.objective_coefficient != 0.:
            original_settings.append(ReactionSetting(x, x.upper_bound, x.lower_bound, 0.))

    return original_settings
