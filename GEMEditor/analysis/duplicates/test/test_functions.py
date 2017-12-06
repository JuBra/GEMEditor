import itertools
from PyQt5.QtWidgets import QApplication
from GEMEditor.analysis.duplicates.functions import *
from GEMEditor.model.classes import Annotation, Reaction, Metabolite, Evidence, Model, Gene

# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


class Test_get_reaction_set:

    def test_get_reaction_set_wo_directionality(self):
        reaction = Reaction("React1")
        metabolite1 = Metabolite("Met1")
        metabolite2 = Metabolite("Met2")
        stoichiometry = {metabolite1: -1,
                         metabolite2: 1}
        reaction.add_metabolites(stoichiometry)
        assert get_reaction_set(reaction, remove_directionality=True) == \
               frozenset([frozenset([(metabolite1, 1)]), frozenset([(metabolite2, 1)])])

    def test_get_reaction_set_with_directionality(self):
        reaction = Reaction("React1")
        metabolite1 = Metabolite("Met1")
        metabolite2 = Metabolite("Met2")
        stoichiometry = {metabolite1: -1,
                         metabolite2: 1}
        reaction.add_metabolites(stoichiometry)
        assert get_reaction_set(reaction, remove_directionality=False) == \
               frozenset([frozenset([(metabolite1, -1)]), frozenset([(metabolite2, 1)])])

    def test_match_for_different_directionality(self):
        r1 = Reaction("r1")
        r2 = Reaction("r2")
        m1 = Metabolite("m1")
        m2 = Metabolite("m2")
        r1.add_metabolites({m1: -1, m2: 1})
        r2.add_metabolites({m1: 1, m2: -1})

        assert get_reaction_set(r1, remove_directionality=True) == \
               get_reaction_set(r2, remove_directionality=True)

        assert get_reaction_set(r1, remove_directionality=False) != \
               get_reaction_set(r2, remove_directionality=False)


class Test_group_duplicate_reactions:

    def test_group_duplicate_reactions(self):
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

    def test_group_duplicates_reactions_different_reactions(self):
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


class Test_get_metabolites_same_compartment:

    def test_sorting_of_compartments(self):
        metabolite1 = Metabolite(compartment=None)
        metabolite2 = Metabolite(compartment="c")
        metabolite3 = Metabolite(compartment="c")

        grouping = get_metabolites_same_compartment([metabolite1, metabolite2, metabolite3])

        assert len(grouping) == 2
        assert set(grouping["c"]) == set([metabolite2, metabolite3])
        assert grouping[""] == [metabolite1]


class Test_get_duplicated_metabolites:

    def test_using_annotations(self):
        met1 = Metabolite()
        met2 = Metabolite()
        met3 = Metabolite()

        met1.annotation.add(Annotation(collection="chebi", identifier="CHEBI:35128"))
        met2.annotation.add(Annotation(collection="chebi", identifier="CHEBI:35128"))
        met3.annotation.add(Annotation(collection="chebi", identifier="CHEBI:17676"))

        # Group items with overlapping annotations
        groups = get_duplicated_metabolites([met1, met2, met3])
        assert len(groups) == 1
        assert set(groups.pop()) == set([met1, met2])

    def test_using_database_mapping(self):
        met1 = Metabolite()
        met2 = Metabolite()
        met3 = Metabolite()

        datbase_mapping = {met1: "1",
                           met2: "1",
                           met3: "2"}

        # Group items mapping to the same datbase entry
        groups = get_duplicated_metabolites([met1, met2, met3], datbase_mapping)
        assert len(groups) == 1
        assert set(groups.pop()) == set([met1, met2])


class Test_merge_metabolites:

    def test_merging_metabolites(self):
        met1 = Metabolite("m1")
        met2 = Metabolite("m2")
        met3 = Metabolite("m3")

        reaction = Reaction()
        original_metabolites = {met1: -1, met2: 1}
        reaction.add_metabolites(original_metabolites)

        merged = merge_metabolites([met1, met3], met3)

        # Check that met1 has been substituted with met3
        assert merged == [met1]
        assert reaction.metabolites == {met3: -1, met2: 1}

    def test_merging_evidences(self):
        met1 = Metabolite("m1")
        evidence1 = Evidence()
        evidence1.set_entity(met1)
        met2 = Metabolite("m2")

        assert evidence1 in met1.evidences

        merge_metabolites([met1, met2], met2)

        assert evidence1 not in met1.evidences
        assert evidence1 in met2.evidences

    def test_add_coefficients_in_overlapping_reactions1(self):
        """ If merged metabolites are involved in the same
        reaction make sure the coefficients are added when
        merging. """

        met1 = Metabolite("met1")
        met2 = Metabolite("met2")
        met3 = Metabolite("met3")

        react = Reaction("r1")
        react.add_metabolites({met1: -1,
                               met2: -1,
                               met3: 1})

        merged = merge_metabolites([met1, met2], met1)

        assert merged == [met2]
        assert react.metabolites[met1] == -2
        assert react.metabolites[met3] == 1

    def test_add_coefficients_in_overlapping_reactions2(self):
        """ If merged metabolites are involved in the same
        reaction make sure the coefficients are added when
        merging. """

        met1 = Metabolite("met1")
        met2 = Metabolite("met2")
        met3 = Metabolite("met3")
        met4 = Metabolite("met4")

        react = Reaction("r1")
        react.add_metabolites({met1: -1,
                               met2: -1,
                               met3: 1,
                               met4: 1})

        merged = merge_metabolites([met1, met3], met1)

        assert merged == [met3]
        assert react.metabolites == {met2: -1, met4: 1}


class Test_merge_reactions:

    def test_merging_reaction(self):
        model = Model("m1")

        react1 = Reaction("r1")
        anno1 = Annotation(collection="ec-code", identifier="2.1.7.0")
        react1.add_annotation(anno1)
        evidence1 = Evidence(entity=react1)
        gene1 = Gene("g1")
        react1.add_child(gene1)
        model.add_evidence(evidence1)

        react2 = Reaction("r2")
        anno2 = Annotation(collection="ec-code", identifier="2.1.7.1")
        react2.add_annotation(anno2)
        evidence2 = Evidence(entity=react2)
        gene2 = Gene("g2")
        react2.add_child(gene2)
        model.add_evidence(evidence2)

        react3 = Reaction("r3")
        anno3 = Annotation(collection="ec-code", identifier="2.1.7.1")
        react3.add_annotation(anno3)
        evidence3 = Evidence(entity=react3)
        gene3 = Gene("g3")
        react3.add_child(gene3)
        model.add_evidence(evidence3)

        model.add_genes((gene1, gene2, gene3))
        model.add_reactions((react1, react2, react3))
        model.setup_reaction_table()

        # Action
        merge_reactions([react1, react2, react3], react1)

        # Check annotation added
        assert anno1 in react1.annotation
        assert anno2 in react1.annotation
        assert anno3 in react3.annotation

        # Check evidences transferred during merge
        assert evidence2 not in react2.evidences
        assert evidence2 in react1.evidences
        assert react1 is evidence2.entity

        assert evidence3 not in react3.evidences
        assert evidence3 in react1.evidences
        assert react1 is evidence3.entity

        # Check merged reactions removed
        assert react2 not in model.reactions
        assert react3 not in model.reactions

        # Check genes transferred during merge
        assert react2 not in gene2.reactions
        assert react1 in gene2.reactions

        assert react3 not in gene3.reactions
        assert react1 in gene3.reactions

        # Check new genegroup is formed
        group = list(react1._children)[0]
        assert gene1 in group._children
        assert gene2 in group._children
        assert gene3 in group._children
        assert group.type == "or"