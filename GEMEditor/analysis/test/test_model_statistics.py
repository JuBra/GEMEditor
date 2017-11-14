import pytest
from GEMEditor.analysis.model_statistics import get_reaction_set
from GEMEditor.model.classes.cobra import Reaction, Metabolite


class Testget_reaction_set:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.reaction = Reaction("r1")
        self.metabolite1 = Metabolite("met1")
        self.metabolite2 = Metabolite("met2")

        self.reaction.add_metabolites({self.metabolite1: -1.,
                                       self.metabolite2: 1.})

        self.reaction2 = Reaction("r2")
        self.reaction2.add_metabolites({self.metabolite1: 1.,
                                       self.metabolite2: -1.})

    def test_setup(self):
        assert self.reaction.metabolites[self.metabolite1] == -1.
        assert self.reaction.metabolites[self.metabolite2] == 1.
        assert self.reaction2.metabolites[self.metabolite1] == 1.
        assert self.reaction2.metabolites[self.metabolite2] == -1.

    def test_normal_reaction(self):
        return_set = get_reaction_set(self.reaction)
        assert isinstance(return_set, frozenset)
        assert len(return_set) == 2
        element1, element2 = list(return_set)

        # Check that elements are of type set
        assert isinstance(element1, frozenset)
        assert len(element1) == 1
        assert isinstance(element2, frozenset)
        assert len(element2) == 1

        # Check that subelements are tuples
        subelement1 = list(element1)[0]
        assert isinstance(subelement1, tuple)
        assert len(subelement1) == 2
        metabolite, stoichiometry = subelement1
        assert self.reaction.metabolites[metabolite] == stoichiometry

        subelement2 = list(element2)[0]
        assert isinstance(subelement2, tuple)
        assert len(subelement2) == 2
        metabolite, stoichiometry = subelement2
        assert self.reaction.metabolites[metabolite] == stoichiometry

    def test_normal_reaction_remove_direction(self):
        return_set = get_reaction_set(self.reaction, remove_directionality=True)
        assert isinstance(return_set, frozenset)
        assert len(return_set) == 2
        element1, element2 = list(return_set)

        # Check that elements are of type set
        assert isinstance(element1, frozenset)
        assert len(element1) == 1
        assert isinstance(element2, frozenset)
        assert len(element2) == 1

        # Check that subelements are tuples
        subelement1 = list(element1)[0]
        assert isinstance(subelement1, tuple)
        assert len(subelement1) == 2
        metabolite, stoichiometry = subelement1
        assert abs(self.reaction.metabolites[metabolite]) == stoichiometry

        subelement2 = list(element2)[0]
        assert isinstance(subelement2, tuple)
        assert len(subelement2) == 2
        metabolite, stoichiometry = subelement2
        assert abs(self.reaction.metabolites[metabolite]) == stoichiometry

    def test_equivalence_opposite_stoichiometry(self):
        assert get_reaction_set(self.reaction) != get_reaction_set(self.reaction2)
        assert get_reaction_set(self.reaction, remove_directionality=True) == get_reaction_set(self.reaction2, remove_directionality=True)



