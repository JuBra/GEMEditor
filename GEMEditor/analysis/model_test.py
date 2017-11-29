import logging
from PyQt5.QtWidgets import QApplication
from GEMEditor.solution.base import fluxes_from_solution
from GEMEditor.model.classes.modeltest import ReactionSetting


LOGGER = logging.getLogger(__name__)


def _run_single_test(model, testcase):
    """ Run a testcase without preparing/restoring model

    This function should only be used in a setting where
    the model has been prepared for running tests and the
    original state is restored after completion of test
    runs.

    Parameters
    ----------
    model: GEMEditor.model.classes.Model,
        Model for which to run the test
    testcase: GEMEditor.model.classes.ModelTest,
        Testcase to run

    Returns
    -------
    status: bool,
        True if the solution matches all test conditions,
        False otherwise
    solution: cobra.core.Solution,
        FBA solution of the simulation run

    """
    status = False

    # Apply all settings
    for setting in testcase.all_settings():
        setting.do()

    # Solve the model
    solution = model.optimize()

    # Undo test settings
    for setting in reversed(testcase.all_settings()):
        setting.undo()

    # Check solution
    if solution:
        fluxes = fluxes_from_solution(solution)
        status = all([x.check(fluxes) for x in testcase.outcomes])

    return status, solution


def run_tests(test_cases, model, progress):
    """ Run and check test cases

    Before running the test cases the model is prepared by:
    1) Setting all objective values to zero
    2) Setting all boundary reactions to production only

    These settings will be restored after running all tests.

    Parameters
    ----------
    test_cases: list,
        Testcases that should be run
    model: GEMEditor.model.classes.Model,
        Model for which to run the test
    progress: QProgressDialog,
        Progress dialog to notify user

    Returns
    -------
    results: dict,
        Collected results of the individual tests
    """
    results = dict()

    # Prepare model for running tests
    original_settings = get_original_settings(model)
    for setting in original_settings:
        setting.do()

    LOGGER.debug("Running test cases..")
    progress.setLabelText("Running test cases..")
    progress.setRange(0, len(test_cases))

    # Run testcases
    for i, test_case in enumerate(test_cases):
        if progress.wasCanceled():
            LOGGER.debug("Running test aborted at #{0!s}".format(i))
            break
        progress.setValue(i)
        QApplication.processEvents()

        # Run test
        results[test_case] = _run_single_test(model, test_case)

    # Restore original values
    for setting in reversed(original_settings):
        setting.undo()

    return results


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
