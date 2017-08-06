from GEMEditor.data_classes import ReactionSetting


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
    """ Get the current reaction settings of the model.

    Stored attributes:
        - lower_bound
        - upper_bound
        - objective_coefficient

    in a list of settings which provides the opportunity
    to revert to the original state after running tests.
    The bounds of all boundary reactions are set to zero
    as well as all objective coefficients as all relevant
    parameters are expected to be set in the test case
    settings. """

    original_settings = []

    for x in model.reactions:

        # Set all boundary reactions to 0
        if x.boundary is True:
            original_settings.append(ReactionSetting(x, x.upper_bound, 0., 0.))

        # Set all objective coefficients to zero
        elif x.objective_coefficient != 0.:
            original_settings.append(ReactionSetting(reaction=x,
                                                     upper_bound=x.upper_bound,
                                                     lower_bound=x.lower_bound,
                                                     objective_coefficient=0.))

    return original_settings
