from GEMEditor.cobraClasses import Reaction, Metabolite, Model
from GEMEditor.data_classes import ReactionSetting, Outcome, ModelTest
from cobra.core.solution import Solution
from GEMEditor.analysis.model_test import get_original_settings, run_test
import GEMEditor
from unittest.mock import Mock

import pytest


class TestGetOriginalSettings:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.model = Model("id")

    @pytest.fixture()
    def setup_r1(self):
        self.metabolite1 = Metabolite("m1")
        self.r1 = Reaction(id="r1", objective_coefficient=0.,
                           lower_bound=-200., upper_bound=200.)
        self.r1.add_metabolites({self.metabolite1: -1})

    @pytest.fixture()
    def setup_r2(self):
        self.metabolite1 = Metabolite("m1")
        self.r2 = Reaction(id="r2", objective_coefficient=1.,
                           lower_bound=-200., upper_bound=200.)
        self.r2.add_metabolites({self.metabolite1: -1})

    @pytest.fixture()
    def setup_r3(self):
        self.metabolite1 = Metabolite("m1")
        self.metabolite2 = Metabolite("m2")
        self.r3 = Reaction(id="r3", objective_coefficient=0.,
                           lower_bound=-200., upper_bound=200.)
        self.r3.add_metabolites({self.metabolite1: -1,
                                 self.metabolite2: 1})

    @pytest.fixture()
    def setup_r4(self):
        self.metabolite1 = Metabolite("m1")
        self.metabolite2 = Metabolite("m2")
        self.r4 = Reaction(id="r3", objective_coefficient=1.,
                           lower_bound=-200., upper_bound=200.)
        self.r4.add_metabolites({self.metabolite1: -1,
                                 self.metabolite2: 1})

    @pytest.mark.usefixtures("setup_r1")
    def test_r1(self):
        self.model.reactions = [self.r1]
        assert self.r1.boundary is True
        assert self.r1.objective_coefficient == 0.
        r1_old_ub = self.r1.upper_bound
        r1_old_lb = self.r1.lower_bound
        r1_old_obj_coeff = self.r1.objective_coefficient
        return_value = get_original_settings(self.model)

        assert len(return_value) == 1
        assert isinstance(return_value[0], ReactionSetting)
        assert return_value[0].reaction is self.r1
        assert return_value[0].upper_bound == r1_old_ub
        assert return_value[0].lower_bound == r1_old_lb
        assert return_value[0].objective_coefficient == r1_old_obj_coeff

        assert self.r1.upper_bound == 0.
        assert self.r1.lower_bound == 0.
        assert self.r1.objective_coefficient == 0.

    @pytest.mark.usefixtures("setup_r2")
    def test_r2(self):
        self.model.reactions = [self.r2]
        assert self.r2.boundary is True
        assert self.r2.objective_coefficient != 0.
        r2_old_ub = self.r2.upper_bound
        r2_old_lb = self.r2.lower_bound
        r2_old_obj_coeff = self.r2.objective_coefficient
        return_value = get_original_settings(self.model)

        assert len(return_value) == 1
        assert isinstance(return_value[0], ReactionSetting)
        assert return_value[0].reaction is self.r2
        assert return_value[0].upper_bound == r2_old_ub
        assert return_value[0].lower_bound == r2_old_lb
        assert return_value[0].objective_coefficient == r2_old_obj_coeff

        assert self.r2.upper_bound == 0.
        assert self.r2.lower_bound == 0.
        assert self.r2.objective_coefficient == 0.

    @pytest.mark.usefixtures("setup_r3")
    def test_r3(self):
        self.model.reactions = [self.r3]
        assert self.r3.boundary is False
        assert self.r3.objective_coefficient == 0.
        r3_old_ub = self.r3.upper_bound
        r3_old_lb = self.r3.lower_bound
        r3_old_obj_coeff = self.r3.objective_coefficient
        return_value = get_original_settings(self.model)

        assert len(return_value) == 0
        assert self.r3.upper_bound == r3_old_ub
        assert self.r3.lower_bound == r3_old_lb
        assert self.r3.objective_coefficient == r3_old_obj_coeff

    @pytest.mark.usefixtures("setup_r4")
    def test_r4(self):
        self.model.reactions = [self.r4]
        assert self.r4.boundary is False
        assert self.r4.objective_coefficient != 0.
        r4_old_ub = self.r4.upper_bound
        r4_old_lb = self.r4.lower_bound
        r4_old_obj_coeff = self.r4.objective_coefficient
        return_value = get_original_settings(self.model)

        assert len(return_value) == 1
        assert isinstance(return_value[0], ReactionSetting)
        assert return_value[0].reaction is self.r4
        assert return_value[0].upper_bound == r4_old_ub
        assert return_value[0].lower_bound == r4_old_lb
        assert return_value[0].objective_coefficient == r4_old_obj_coeff

        assert self.r4.upper_bound == r4_old_ub
        assert self.r4.lower_bound == r4_old_lb
        assert self.r4.objective_coefficient == 0.

    @pytest.mark.usefixtures("setup_r4", "setup_r3")
    def test_only_proper_reaction_modified(self):
        self.model.reactions = [self.r4, self.r3]
        assert self.r4.boundary is False
        assert self.r4.objective_coefficient != 0.
        r4_old_ub = self.r4.upper_bound
        r4_old_lb = self.r4.lower_bound
        r4_old_obj_coeff = self.r4.objective_coefficient

        assert self.r3.boundary is False
        assert self.r3.objective_coefficient == 0.
        r3_old_ub = self.r3.upper_bound
        r3_old_lb = self.r3.lower_bound
        r3_old_obj_coeff = self.r3.objective_coefficient

        return_value = get_original_settings(self.model)

        assert len(return_value) == 1
        assert isinstance(return_value[0], ReactionSetting)
        assert return_value[0].reaction is self.r4
        assert return_value[0].upper_bound == r4_old_ub
        assert return_value[0].lower_bound == r4_old_lb
        assert return_value[0].objective_coefficient == r4_old_obj_coeff

        assert self.r4.upper_bound == r4_old_ub
        assert self.r4.lower_bound == r4_old_lb
        assert self.r4.objective_coefficient == 0.

        assert self.r3.upper_bound == r3_old_ub
        assert self.r3.lower_bound == r3_old_lb
        assert self.r3.objective_coefficient == r3_old_obj_coeff


@pytest.fixture()
def solution():
    solution = Solution(f=None)
    solution.x_dict = {"r1": 10.,
                       "r2": 0.}
    return solution


@pytest.fixture()
def infeasible_solution():
    return Solution(f=None, status="infeasible")


class TestRunTest:

    @pytest.fixture(autouse=True)
    def setup_test(self):

        self.metabolite1 = Metabolite("m1")
        self.metabolite2 = Metabolite("m2")

        self.reaction1 = Reaction("r1", lower_bound=-1000.,
                                  upper_bound=1000., objective_coefficient=0.)
        self.r1_init_setting = self.reaction1.get_setting()
        self.reaction1.add_metabolites({self.metabolite1: -1,
                                        self.metabolite2: 1})
        self.reaction1.flux_value = 50.
        self.setting1 = ReactionSetting(reaction=self.reaction1,
                                        upper_bound=0.,
                                        lower_bound=0.,
                                        objective_coefficient=1.)

        self.reaction2 = Reaction("r2", lower_bound=0., upper_bound=50.,
                                  objective_coefficient=1.)
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
        monkeypatch.setattr("GEMEditor.cobraClasses.Model.optimize", Mock(return_value=solution))

    @pytest.fixture()
    def mock_optimize_infeasible(self, monkeypatch, infeasible_solution):
        monkeypatch.setattr("GEMEditor.cobraClasses.Model.optimize", Mock(return_value=infeasible_solution))
        return infeasible_solution

    @pytest.fixture()
    def mock_get_original_settings(self, monkeypatch):
        return_value = [Mock(), Mock()]
        monkeypatch.setattr("GEMEditor.analysis.model_test.get_original_settings", Mock(return_value=return_value))
        return return_value

    def test_outcomes(self, solution):
        assert self.true_outcome1.check_solution(solution) is True
        assert self.false_outcome1.check_solution(solution) is False

    @pytest.mark.usefixtures("mock_optimize")
    def test_mock(self):
        result = Model().optimize()
        assert isinstance(result.x_dict, dict)

    @pytest.mark.usefixtures("mock_optimize")
    def test_run_test_true_outcome(self):
        model_test = ModelTest()
        model_test.outcomes = [self.true_outcome1]
        status, _ = run_test(model_test, Model(), None)
        assert status is True

    @pytest.mark.usefixtures("mock_optimize")
    def test_run_test_false_outcome(self):
        model_test = ModelTest()
        model_test.outcomes = [self.false_outcome1]
        status, _ = run_test(model_test, Model(), None)
        assert status is False

    @pytest.mark.usefixtures("mock_optimize")
    def test_run_test_false_outcome2(self):
        model_test = ModelTest()
        model_test.outcomes = [self.true_outcome1, self.false_outcome1]
        status, _ = run_test(model_test, Model(), None)
        assert status is False

    def test_run_test_infeasible_solution(self, mock_optimize_infeasible):
        model_test = ModelTest()
        model_test.outcomes = [self.true_outcome1, self.false_outcome1]
        status, solution = run_test(model_test, Model(), None)
        assert solution is mock_optimize_infeasible
        assert status is False

    @pytest.mark.usefixtures("mock_optimize")
    def test_value_restored(self):
        model_test = ModelTest()
        self.setting2.do = Mock()
        model_test.settings = [self.setting1, self.setting2]
        assert self.setting2.do.called is False
        assert self.reaction1 is self.setting1.reaction

        status, _ = run_test(model_test, Model(), None)
        assert self.setting2.do.called is True
        assert self.reaction1.upper_bound == self.r1_init_setting.upper_bound
        assert self.reaction1.lower_bound == self.r1_init_setting.lower_bound
        assert self.reaction1.objective_coefficient == self.r1_init_setting.objective_coefficient

    @pytest.mark.usefixtures("mock_optimize", "mock_get_original_settings")
    def test_restore_initial_get_original_not_called(self):
        GEMEditor.analysis.model_test.get_original_settings.called is False
        model_test = ModelTest()
        model_test.outcomes = [self.true_outcome1]
        status, _ = run_test(model_test, Model(), None, restore_initial=False)
        GEMEditor.analysis.model_test.get_original_settings.called is False

    @pytest.mark.usefixtures("mock_optimize")
    def test_restore_initial_get_original_called(self, mock_get_original_settings):
        original_settings = mock_get_original_settings
        GEMEditor.analysis.model_test.get_original_settings.called is False
        model_test = ModelTest()
        model_test.outcomes = [self.true_outcome1]
        status, _ = run_test(model_test, Model(), None, restore_initial=True)
        GEMEditor.analysis.model_test.get_original_settings.called is True
        for x in original_settings:
            assert x.do.called is True
