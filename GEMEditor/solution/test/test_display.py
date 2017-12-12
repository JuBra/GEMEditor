import pytest
import cobra.test
from cobra.flux_analysis import flux_variability_analysis
from GEMEditor.solution.display import factory_solution
from cobra.flux_analysis import pfba, single_gene_deletion, single_reaction_deletion, loopless_solution


class TestSolutionDialog:

    @pytest.fixture(scope="session")
    def setup(self):
        self.model = cobra.test.create_test_model("ecoli")

    def test_setup_fba_dialog(self):
        solution = self.model.optimize()
        dialog = factory_solution("fba", self.model, solution)
        assert dialog.label_status.text() == solution.status
        assert dialog.label_label_objective.text() == str(solution.objective)

    def test_setup_loopless_dialog(self):
        solution = loopless_solution(self.model)
        dialog = factory_solution("fba", self.model, solution)
        assert dialog.label_status.text() == solution.status
        assert dialog.label_label_objective.text() == str(solution.objective)

    def test_setup_pfba_dialog(self):
        solution = pfba(self.model)
        dialog = factory_solution("fba", self.model, solution)
        assert dialog.label_status.text() == solution.status
        assert dialog.label_label_objective.text() == str(solution.objective)

    def test_setup_fva_dialog(self):
        solution = flux_variability_analysis(self.model)
        dialog = factory_solution("fva", self.model, solution)
        assert dialog.label_status.text() == "NA"
        assert dialog.label_label_objective.text() == "NA"

    def test_setup_single_gene_deletion(self):
        solution = single_gene_deletion(self.model)
        dialog = factory_solution("single_gene_del", self.model, solution)
        assert dialog.label_status.text() == "NA"
        assert dialog.label_label_objective.text() == "NA"

    def test_setup_single_reaction_deletion(self):
        solution = single_reaction_deletion(self.model)
        dialog = factory_solution("single_reaction_del", self.model, solution)
        assert dialog.label_status.text() == "NA"
        assert dialog.label_label_objective.text() == "NA"
