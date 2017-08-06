from GEMEditor.analysis.duplicates import group_duplicate_reactions, get_reaction_set
from GEMEditor.cobraClasses import Reaction, Metabolite
import itertools


def test_get_reaction_set_wo_directionality():
    reaction = Reaction("React1")
    metabolite1 = Metabolite("Met1")
    metabolite2 = Metabolite("Met2")
    stoichiometry = {metabolite1: -1,
                     metabolite2: 1}
    reaction.add_metabolites(stoichiometry)
    assert get_reaction_set(reaction, remove_directionality=True) == \
           frozenset([frozenset([(metabolite1, 1)]), frozenset([(metabolite2, 1)])])


def test_get_reaction_set_with_directionality():
    reaction = Reaction("React1")
    metabolite1 = Metabolite("Met1")
    metabolite2 = Metabolite("Met2")
    stoichiometry = {metabolite1: -1,
                     metabolite2: 1}
    reaction.add_metabolites(stoichiometry)
    assert get_reaction_set(reaction, remove_directionality=False) == \
           frozenset([frozenset([(metabolite1, -1)]), frozenset([(metabolite2, 1)])])


def test_group_duplicate_reactions():
    reaction1 = Reaction("React1")
    reaction2 = Reaction("React2")
    metabolite1 = Metabolite("Met1")
    metabolite2 = Metabolite("Met2")
    reaction1.add_metabolites({metabolite1: -1,
                               metabolite2: 1})
    reaction2.add_metabolites({metabolite1: 1,
                               metabolite2: -1})
    result = group_duplicate_reactions([reaction1, reaction2])
    assert len(result) == 1
    assert reaction1 in list(result.values())[0]
    assert reaction2 in list(result.values())[0]


def test_group_duplicates_reactions_different_reactions():
    reaction1 = Reaction("React1")
    reaction2 = Reaction("React2")
    metabolite1 = Metabolite("Met1")
    metabolite2 = Metabolite("Met2")
    reaction1.add_metabolites({metabolite1: -1,
                               metabolite2: 1})
    reaction2.add_metabolites({metabolite1: 1,
                               metabolite2: -2})
    result = group_duplicate_reactions([reaction1, reaction2])
    assert len(result) == 2
    assert all(len(x) == 1 for x in itertools.chain(result.values()))
    assert reaction1 in itertools.chain(*result.values())
    assert reaction2 in itertools.chain(*result.values())
