from unittest.mock import Mock
import GEMEditor
import pytest
from GEMEditor.analysis.model_test import _get_original_settings, run_tests
from GEMEditor.model.classes.cobra import Reaction, Metabolite, Model
from GEMEditor.model.classes.modeltest import ModelTest, ReactionSetting, Outcome
from cobra.core.solution import LegacySolution


class TestGetOriginalSettings:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.model = Model("id")
        self.m1 = Metabolite("m1")
        self.m2 = Metabolite("m2")
        self.r1 = Reaction(id="r1")
        self.model.add_reactions((self.r1,))

    def test_boundary_forward(self):
        self.r1.add_metabolites({self.m1: -1})

        # Original settings
        self.r1.upper_bound = 200.
        self.r1.lower_bound = -200
        self.r1.objective_coefficient = 1

        # Get the setting of a boundary reaction
        setting = _get_original_settings(self.model)[0]

        # Check that original values are stored
        assert setting.reaction is self.r1
        assert setting.upper_bound == 200

        # Check that reaction is producing only
        assert setting.lower_bound == 0.
        assert setting.objective_coefficient == 0.

    def test_boundary_reverse(self):
        self.r1.add_metabolites({self.m1: 1})

        # Original settings
        self.r1.upper_bound = 200.
        self.r1.lower_bound = -200
        self.r1.objective_coefficient = 1

        # Get the setting of a boundary reaction
        setting = _get_original_settings(self.model)[0]

        # Check that original values are stored
        assert setting.reaction is self.r1
        assert setting.lower_bound == -200

        # Check that reaction is producing only
        assert setting.upper_bound == 0.
        assert setting.objective_coefficient == 0.

    def test_inactive_reaction(self):
        self.r1.add_metabolites({self.m1: -1,
                                 self.m2: 1})
        self.r1.lower_bound = 0.
        self.r1.upper_bound = 0.
        self.r1.objective_coefficient = 1.

        # Get the setting of a boundary reaction
        setting = _get_original_settings(self.model)[0]

        # Check that objective setting is deactivated
        assert setting.reaction is self.r1
        assert setting.lower_bound == 0.
        assert setting.upper_bound == 0.
        assert setting.objective_coefficient == 0.

    @pytest.mark.parametrize("params, expectations", [((-200, 200, 1.), (-200, 200, 0.)),
                                                       ((0, 200, 1.), (0., 200, 0.)),
                                                       ((-200, 0, 1.), (-200, 0, 0.)),
                                                      ((-200, -50, 1.), (-200, -50, 0.)),
                                                      ((100, 200, 1.), (100, 200, 0.))])
    def test_setting_for_optimized_reactions(self, params, expectations):
        self.r1.add_metabolites({self.m1: -1,
                                 self.m2: 1})

        self.r1.lower_bound = params[0]
        self.r1.upper_bound = params[1]
        self.r1.objective_coefficient = params[2]

        setting = _get_original_settings(self.model)[0]

        # Check that the settings are expected
        assert setting.lower_bound == expectations[0]
        assert setting.upper_bound == expectations[1]
        assert setting.objective_coefficient == expectations[2]

    @pytest.mark.parametrize("params", [(-200, 200, 0.), (0, 200, 0.), (-200, 0, 0.),
                                        (-200, -50, 0.), (100, 200, 0.)])
    def test_no_setting_for_nonoptimized_reactions(self, params):
        self.r1.add_metabolites({self.m1: -1,
                                 self.m2: 1})

        self.r1.lower_bound = params[0]
        self.r1.upper_bound = params[1]
        self.r1.objective_coefficient = params[2]

        assert not _get_original_settings(self.model)


@pytest.fixture()
def fluxes():
    return {"r1": 10., "r2": 0.}


@pytest.fixture()
def infeasible_solution():
    return LegacySolution(f=None, status="infeasible")


class TestRunTest:

    @pytest.fixture(autouse=True)
    def setup_test(self):
        self.model = Model("id")
        self.metabolite1 = Metabolite("m1")
        self.metabolite2 = Metabolite("m2")

        self.reaction1 = Reaction("r1", lower_bound=-1000., upper_bound=1000.)
        self.model.add_reactions((self.reaction1,))
        self.reaction1.objective_coefficient = 0.
        self.r1_init_setting = self.reaction1.get_setting()
        self.reaction1.add_metabolites({self.metabolite1: -1,
                                        self.metabolite2: 1})
        self.reaction1.flux_value = 50.
        self.setting1 = ReactionSetting(reaction=self.reaction1,
                                        upper_bound=0.,
                                        lower_bound=0.,
                                        objective_coefficient=1.)

        self.reaction2 = Reaction("r2", lower_bound=0., upper_bound=50.)
        self.model.add_reactions((self.reaction2,))
        self.reaction2.objective_coefficient = 1.
        self.setting2 = ReactionSetting(reaction=self.reaction2,
                                        upper_bound=1000.,
                                        lower_bound=-1000.,
                                        objective_coefficient=0.)
        self.r2_init_setting = self.reaction2.get_setting()
        self.reaction2.add_metabolites({self.metabolite1: -1})

        self.true_outcome1 = Outcome(reaction=self.reaction1,
                                     value=15.,
                                     operator="less than")

        self.false_outcome1 = Outcome(reaction=self.reaction1,
                                      value=15.,
                                      operator="greater than")

    @pytest.fixture()
    def mock_optimize(self, monkeypatch, solution):
        monkeypatch.setattr("GEMEditor.model.classes.cobra.Model.optimize", Mock(return_value=solution))

    @pytest.fixture()
    def mock_optimize_infeasible(self, monkeypatch, infeasible_solution):
        monkeypatch.setattr("GEMEditor.model.classes.cobra.Model.optimize", Mock(return_value=infeasible_solution))
        return infeasible_solution

    @pytest.fixture()
    def mock_get_original_settings(self, monkeypatch):
        return_value = [Mock(), Mock()]
        monkeypatch.setattr("GEMEditor.analysis.model_test._get_original_settings", Mock(return_value=return_value))
        return return_value

    @pytest.fixture()
    def progress(self):
        return Mock(wasCanceled=Mock(return_value=False))

    def test_outcomes(self, fluxes):
        assert self.true_outcome1.check(fluxes) is True
        assert self.false_outcome1.check(fluxes) is False

    @pytest.mark.usefixtures("mock_optimize")
    def test_mock(self):
        result = Model().optimize()
        assert isinstance(result.x_dict, dict)

    @pytest.mark.usefixtures("mock_optimize")
    def test_run_test_true_outcome(self, progress):
        model_test = ModelTest()
        model_test.outcomes = [self.true_outcome1]

        results = run_tests((model_test,), Model(), progress)
        status, _ = results[model_test]
        assert status is True

    @pytest.mark.usefixtures("mock_optimize")
    def test_run_test_false_outcome(self, progress):
        model_test = ModelTest()
        model_test.outcomes = [self.false_outcome1]

        results = run_tests((model_test,), Model(), progress)
        status, _ = results[model_test]
        assert status is True

    @pytest.mark.usefixtures("mock_optimize")
    def test_run_test_false_outcome2(self, progress):
        model_test = ModelTest()
        model_test.outcomes = [self.true_outcome1, self.false_outcome1]

        results = run_tests((model_test,), Model(), progress)
        status, _ = results[model_test]
        assert status is False

    def test_run_test_infeasible_solution(self, mock_optimize_infeasible, progress):
        model_test = ModelTest()
        model_test.outcomes = [self.true_outcome1, self.false_outcome1]

        results = run_tests((model_test,), Model(), progress)
        status, solution = results[model_test]
        assert solution is mock_optimize_infeasible
        assert status is False

    @pytest.mark.usefixtures("mock_optimize")
    def test_value_restored(self, progress):
        model_test = ModelTest()
        self.setting2.do = Mock()
        model_test.reaction_settings = [self.setting1, self.setting2]
        assert self.setting2.do.called is False
        assert self.reaction1 is self.setting1.reaction

        results = run_tests((model_test,), Model(), progress)
        status, _ = results[model_test]
        assert self.setting2.do.called is True
        assert self.reaction1.upper_bound == self.r1_init_setting.upper_bound
        assert self.reaction1.lower_bound == self.r1_init_setting.lower_bound
        assert self.reaction1.objective_coefficient == self.r1_init_setting.objective_coefficient

    @pytest.mark.usefixtures("mock_optimize", "mock_get_original_settings")
    def test_restore_initial_get_original_not_called(self, progress):
        assert GEMEditor.analysis.model_test._get_original_settings.called is False
        model_test = ModelTest()
        model_test.outcomes = [self.true_outcome1]

        results = run_tests((model_test,), Model(), progress)
        status, _ = results[model_test]
        assert GEMEditor.analysis.model_test._get_original_settings.called is False

    @pytest.mark.usefixtures("mock_optimize")
    def test_restore_initial_get_original_called(self, mock_get_original_settings, progress):
        original_settings = mock_get_original_settings
        assert GEMEditor.analysis.model_test._get_original_settings.called is False
        model_test = ModelTest()
        model_test.outcomes = [self.true_outcome1]

        results = run_tests((model_test,), Model(), progress)
        status, _ = results[model_test]
        assert GEMEditor.analysis.model_test._get_original_settings.called is True
        for x in original_settings:
            assert x.do.called is True
