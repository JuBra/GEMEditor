import pytest
import cobra.test
from cobra.flux_analysis import flux_variability_analysis
from GEMEditor.solution.display import factory_solution
from cobra.flux_analysis import pfba, single_gene_deletion, single_reaction_deletion, loopless_solution


@pytest.fixture(scope="class")
def model():
    model = cobra.test.create_test_model("ecoli")
    for g in model.genes:
        g.genome = None
    return


class TestSolutionDialog:

    def test_setup_fba_dialog(self, model):
        solution = model.optimize()
        dialog = factory_solution("fba", model, solution)
        assert dialog.label_status.text() == solution.status
        assert dialog.label_label_objective.text() == str(round(solution.objective_value, 2))

    def test_setup_loopless_dialog(self, model):
        solution = loopless_solution(model)
        dialog = factory_solution("fba", model, solution)
        assert dialog.label_status.text() == solution.status
        assert dialog.label_label_objective.text() == str(round(solution.objective_value, 2))

    def test_setup_pfba_dialog(self, model):
        solution = pfba(model)
        dialog = factory_solution("fba", model, solution)
        assert dialog.label_status.text() == solution.status
        assert dialog.label_label_objective.text() == str(round(solution.objective_value, 2))

    def test_setup_fva_dialog(self, model):
        solution = flux_variability_analysis(model)
        dialog = factory_solution("fva", model, solution)
        assert dialog.label_status.text() == "NA"
        assert dialog.label_label_objective.text() == "NA"

    def test_setup_single_gene_deletion(self, model):
        solution = single_gene_deletion(model)
        dialog = factory_solution("single_gene_deletion", model, solution)
        assert dialog.label_status.text() == "NA"
        assert dialog.label_label_objective.text() == "NA"

    def test_setup_single_reaction_deletion(self, model):
        solution = single_reaction_deletion(model)
        dialog = factory_solution("single_reaction_deletion", model, solution)
        assert dialog.label_status.text() == "NA"
        assert dialog.label_label_objective.text() == "NA"
