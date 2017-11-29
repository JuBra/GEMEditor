import pytest
from unittest.mock import Mock, patch, call, PropertyMock
from GEMEditor.model.classes.cobra import Reaction, Gene
from GEMEditor.model.classes.modeltest import ModelTest, ReactionSetting, GeneSetting, Outcome
from GEMEditor.model.classes.reference import Reference


class TestModelTest:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.test = ModelTest()
        self.outcome1 = Outcome()
        self.reaction_setting = ReactionSetting()
        self.gene_setting = GeneSetting()
        self.reference1 = Reference()

    def test_setup(self):
        assert self.test.description == ""
        assert self.test.outcomes == []
        assert self.test.reaction_settings == []
        assert self.test.gene_settings == []
        assert len(self.test.references) == 0

    def test_add_outcomes(self):
        self.test.add_outcome(self.outcome1)
        assert self.outcome1 in self.test.outcomes

    def test_add_reaction_setting(self):
        self.test.add_setting(self.reaction_setting)
        assert self.reaction_setting in self.test.reaction_settings

    def test_add_gene_setting(self):
        self.test.add_setting(self.gene_setting)
        assert self.gene_setting in self.test.gene_settings

    def test_add_reference(self):
        self.test.add_reference(self.reference1)
        assert self.reference1 in self.test.references

    def test_clear_all(self):
        self.test.add_outcome(self.outcome1)
        self.test.add_reference(self.reference1)
        self.test.add_setting(self.reaction_setting)

        self.test.clear_all()
        assert len(self.test.outcomes) == 0
        assert len(self.test.gene_settings) == 0
        assert len(self.test.reaction_settings) == 0
        assert len(self.test.references) == 0


class TestOutcomes:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.outcome = Outcome()
        self.solution = Mock()

    def test_setup(self):
        assert self.outcome.reaction is None
        assert self.outcome.value is None
        assert self.outcome.operator is None

    def test_check_solution(self):
        reaction_id = "test_id"
        reaction = Reaction(reaction_id)
        fluxes = {reaction_id: 5.}

        new_outcome = Outcome(reaction, value=0., operator="greater than")
        assert new_outcome.check(fluxes) is True
        self.solution.x_dict = {reaction_id: 0.}
        assert new_outcome.check(fluxes) is False

        new_outcome.operator = "less than"
        assert new_outcome.check(fluxes) is False
        new_outcome.value = 10.
        assert new_outcome.check(fluxes) is True

        new_outcome.operator = ""
        assert new_outcome.check(fluxes) is False

    def test_empty_outcome_is_not_valid(self):
        assert self.outcome.is_valid() is False

    def test_no_operator_set_is_invalid(self):
        self.outcome.reaction = Reaction()
        self.outcome.value = 0.

        assert self.outcome.operator is None
        assert self.outcome.is_valid() is False

    @pytest.mark.parametrize("parameters", [(Reaction(), 0., "greater than", True),
                                            (None, 0., "greater than", False),
                                            (Reaction(), None, "greater than", False),
                                            (Reaction(), 0., None, False),
                                            (None, None, None, False)])
    def test_outcome_is_valid(self, parameters):
        outcome = Outcome(reaction=parameters[0],
                          value=parameters[1],
                          operator=parameters[2])

        assert outcome.is_valid() is parameters[3]


class TestSetting:

    def test_set_parameters(self):
        old_lb = -1000.
        old_ub = 1000.
        old_obj_value = 1.

        with patch('GEMEditor.model.classes.cobra.Reaction.objective_coefficient', new_callable=PropertyMock) as objective_coefficient:
            objective_coefficient.return_value = old_obj_value
            reaction = Reaction("test_id",
                                lower_bound=old_lb,
                                upper_bound=old_ub)

            new_lb = -500.
            new_ub = 500.
            new_obj_value = 0.
            setting = ReactionSetting(reaction, upper_bound=new_ub, lower_bound=new_lb, objective_coefficient=new_obj_value)

            assert reaction.upper_bound == old_ub
            assert reaction.lower_bound == old_lb
            assert reaction.objective_coefficient == old_obj_value

            setting.do()

            assert reaction.upper_bound == new_ub
            assert reaction.lower_bound == new_lb
            assert objective_coefficient.call_args == call(new_obj_value)
            objective_coefficient.return_value = new_obj_value

            setting.undo()
            assert reaction.upper_bound == old_ub
            assert reaction.lower_bound == old_lb
            assert objective_coefficient.call_args == call(old_obj_value)
            objective_coefficient.return_value = old_obj_value

            # Check that calling undo a second time does not change the value
            prior_call_count = objective_coefficient.call_count
            setting.undo()
            assert reaction.upper_bound == old_ub
            assert reaction.lower_bound == old_lb
            assert objective_coefficient.call_count == prior_call_count


class TestGeneCondition:

    def test_setting_resetting_boundaries(self):
        gene = Gene()
        reaction = Reaction(lower_bound=-1000., upper_bound=1000.)
        reaction.add_child(gene)
        gene.functional = True

        condition = GeneSetting(gene, False)

        assert gene.functional is True
        assert reaction.upper_bound == 1000.
        assert reaction.lower_bound == -1000.

        condition.do()

        assert gene.functional is False
        assert reaction.upper_bound == 0.
        assert reaction.lower_bound == 0.

        condition.undo()

        assert gene.functional is True
        assert reaction.upper_bound == 1000.
        assert reaction.lower_bound == -1000.

        # Check that calling undo second time does not change value
        condition.undo()

        assert gene.functional is True
        assert reaction.upper_bound == 1000.
        assert reaction.lower_bound == -1000.
