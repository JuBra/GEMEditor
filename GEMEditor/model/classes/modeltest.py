import operator
from collections import OrderedDict
from uuid import uuid4
from GEMEditor.model.classes.base import ReferenceLink


class ModelTest(ReferenceLink):

    def __init__(self, id=None, description="", comment=""):
        super(ModelTest, self).__init__()
        self.id = id or str(uuid4())
        self.description = description or ""
        self.comment = comment or ""
        self.gene_settings = []
        self.reaction_settings = []
        self.outcomes = []

    def add_setting(self, setting):
        if isinstance(setting, ReactionSetting):
            self.reaction_settings.append(setting)
        elif isinstance(setting, GeneSetting):
            self.gene_settings.append(setting)

    def add_outcome(self, outcome):
        self.outcomes.append(outcome)

    def get_gene_settings(self):
        return self.gene_settings

    def get_reaction_settings(self):
        return self.reaction_settings

    def all_settings(self):
        # Note: For correct test running the order is important
        return self.reaction_settings + self.gene_settings

    def clear_all(self):
        self.gene_settings[:] = []
        self.reaction_settings[:] = []
        self.outcomes[:] = []
        for x in list(self.references):
            self.remove_reference(x)


class ReactionSetting:

    def __init__(self, reaction=None, upper_bound=None,
                 lower_bound=None, objective_coefficient=None):
        self.reaction = reaction
        self._old_upper = None
        self._old_lower = None
        self._old_objective = None
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound
        self.objective_coefficient = objective_coefficient
        self.state_saved = False

    def do(self):
        self._old_upper = self.reaction.upper_bound
        self._old_lower = self.reaction.lower_bound
        self._old_objective = self.reaction.objective_coefficient
        self.state_saved = True
        self.reaction.upper_bound = self.upper_bound
        self.reaction.lower_bound = self.lower_bound
        self.reaction.objective_coefficient = self.objective_coefficient

    def undo(self):
        if self.state_saved:
            self.reaction.upper_bound = self._old_upper
            self.reaction.lower_bound = self._old_lower
            self.reaction.objective_coefficient = self._old_objective
            self._old_upper = None
            self._old_lower = None
            self._old_objective = None
            self.state_saved = False

    def __eq__(self, other):
        if (isinstance(other, self.__class__) and
            self.reaction is other.reaction and
            self.upper_bound == other.upper_bound and
            self.lower_bound == other.lower_bound and
            self.objective_coefficient == other.objective_coefficient):
            return True
        else:
            return False

    def is_valid(self):
        if (self.reaction and self.upper_bound is not None and
                    self.lower_bound is not None and self.objective_coefficient is not None):
            return True
        else:
            return False


class GeneSetting:

    def __init__(self, gene=None, activity=None):
        self.gene = gene
        self.activity = activity
        self._old_activity = None
        self._changed_reactions = []

    def do(self):
        self._old_activity = self.gene.functional
        self.gene.functional = self.activity
        for reaction in self.gene.reactions:
            if not reaction.functional:
                self._changed_reactions.append((reaction, reaction.lower_bound, reaction.upper_bound))
                reaction.lower_bound, reaction.upper_bound = 0, 0

    def undo(self):
        for x in reversed(self._changed_reactions):
            x[0].lower_bound = x[1]
            x[0].upper_bound = x[2]
        self._changed_reactions = []
        if self._old_activity is not None:
            self.gene.functional = self._old_activity
            self._old_activity = None

    def __eq__(self, other):
        if (isinstance(other, self.__class__) and
            self.gene is other.gene and self.activity is other.activity):
            return True
        else:
            return False

    def is_valid(self):
        return self.activity is not None and self.gene is not None


class Outcome:

    options = OrderedDict([("greater than", operator.gt),
                           ("less than", operator.lt)])

    def __init__(self, reaction=None, value=None, operator=None):
        self.reaction = reaction
        self.value = value
        self.operator = operator

    def check_solution(self, solution, precision=0.01):
        """ Check if the flux value in the solution matches the expectation in the testcase """
        if not self.operator:
            return False
        selected_operator = self.options[self.operator]
        if selected_operator is operator.gt:
            return selected_operator(solution.x_dict[self.reaction.id]-precision, self.value)
        else:
            return selected_operator(solution.x_dict[self.reaction.id]+precision, self.value)

    def is_valid(self):
        return (self.operator in self.options and
                isinstance(self.value, float) and
                self.reaction is not None)

    def __eq__(self, other):
        if (isinstance(other, self.__class__) and
                    self.reaction is other.reaction and
                    self.value == other.value and
                    self.operator == other.operator):
            return True
        else:
            return False