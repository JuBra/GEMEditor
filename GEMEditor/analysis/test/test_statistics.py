from unittest.mock import Mock

import pytest
from GEMEditor.analysis.statistics import reaction_statistics, metabolite_statistics, gene_statistics
from GEMEditor.model.classes.cobra import Model, Metabolite, Reaction, Gene
from GEMEditor.model.classes.reference import Annotation
from PyQt5.QtWidgets import QApplication

# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestReactionStatistics:

    @pytest.fixture()
    def progress(self):
        return Mock(**{"wasCanceled": Mock(return_value=False)})

    def test_get_reaction_statistics(self, progress):
        model = Model("model1")
        metabolite1 = Metabolite("m1")
        metabolite2 = Metabolite("m2")
        metabolite7 = Metabolite("m7")

        # Add inverted reactions
        reaction1 = Reaction("r1")
        reaction1.add_metabolites({metabolite1: -1,
                                   metabolite2: 1})
        reaction2 = Reaction("r2")
        reaction2.add_metabolites({metabolite1: 1,
                                   metabolite2: -1})

        # Add boundary reaction
        reaction3 = Reaction("r3")
        reaction3.add_metabolites({metabolite1: -1})

        # Add transport reaction
        metabolite3 = Metabolite("m3", compartment="c")
        metabolite4 = Metabolite("m4", compartment="e")
        reaction4 = Reaction("r4")
        reaction4.add_metabolites({metabolite3: -1,
                                   metabolite4: 1})

        # Add unbalanced reaction
        metabolite5 = Metabolite("m5", formula="H")
        metabolite6 = Metabolite("m6", formula="C")
        reaction5 = Reaction("r5")
        reaction5.add_metabolites({metabolite5: -1,
                                   metabolite6: 1})

        # Add reaction with gene
        reaction6 = Reaction("r6")
        reaction6.add_metabolites({metabolite1: -1,
                                   metabolite7: 1})
        gene = Gene()
        reaction6.add_child(gene)

        # Add reaction with annotation
        reaction7 = Reaction("r7")
        reaction7.add_metabolites({metabolite2: -1,
                                   metabolite7: 1})
        reaction7.add_annotation(Annotation("chebi", "CHEBI:1235"))

        model.add_reactions([reaction1, reaction2, reaction3, reaction4, reaction5, reaction6, reaction7])

        # Action
        output_statistics = reaction_statistics(model)

        # Return value of reaction_statistics:
        #
        # ("Total", num_reactions),
        # ("Transport", num_transport),
        # ("Boundary", num_boundary),
        # ("Unbalanced", num_unbalanced),
        # ("Annotated", num_annotated),
        # ("No genes", num_no_genes),
        # ("Evidence for presence", num_has_presence_evidence),
        # ("Known gene", num_known_gene)

        # Check total state
        assert output_statistics["Total"] == 7

        # Check transport reactions
        assert output_statistics["Transport"] == 1

        # Check boundary reactions
        assert output_statistics["Boundary"] == 1

        # Check boundary reactions
        assert output_statistics["Unbalanced"] == 1

        # Check annotated
        assert output_statistics["Annotated"] == 1

        # Check no genes
        # Note: Boundary reactions are excluded from the counting
        assert output_statistics["No genes"] == 5

        # Check evidence for presence
        # Todo: Implement test
        assert True

        # Check known gene
        # Todo: Implement test
        assert True

        # Check that tests exist for all gathered statistics
        assert len(output_statistics) == 8 # Change to number of tests


class TestMetaboliteStatistics:

    def test_get_gene_statistics(self):
        model = Model()
        metabolite1 = Metabolite("m1")
        annotation = Annotation("chebi", "CHEBI:1233")
        metabolite1.annotation.add(annotation)

        metabolite2 = Metabolite("m2")
        model.add_metabolites([metabolite1, metabolite2])

        # Action
        metabolite_stats = metabolite_statistics(model)

        # Return value:
        # ("Total", len(model.metabolites)),
        # ("Annotated", num_anotated),
        # ("DeadEnd", num_dead_ends)

        # 1) Check Total
        assert metabolite_stats["Total"] == 2

        # 2) Check Annotated
        assert metabolite_stats["Annotated"] == 1

        # 3) Check DeadEnd
        assert metabolite_stats["DeadEnd"] == 2

        # Check that there is a test for all options
        assert len(metabolite_stats) == 3


class TestGetGeneStatistics:

    def test_get_gene_statistics(self):
        model = Model()
        reaction = Reaction("r1")
        annotation = Annotation("chebi", "CHEBI:1233")

        gene1 = Gene("g1")
        gene1.annotation.add(annotation)
        gene2 = Gene("g2")
        gene2.annotation.add(annotation)
        reaction.add_child(gene2)
        gene3 = Gene("g3")
        reaction.add_child(gene3)

        for x in [gene1, gene2, gene3]:
            model.add_gene(x)

        # Action
        gene_stats = gene_statistics(model)

        # Return value
        # ("Total", num_genes),
        # ("Unassigned", num_unassigned),
        # ("Verified location", num_exp_verified_localization),
        # ("Predicted location", num_predicted_localization),
        # ("Known function", num_known_function)

        # Check Total
        assert gene_stats["Total"] == 3

        # Check Unassigned
        assert gene_stats["Unassigned"] == 1

        # Check Verified location
        # Todo: Implement test
        assert True

        # Check Predicted location
        # Todo: Implement test
        assert True

        # Check Known function
        # Todo: Implement test
        assert True

