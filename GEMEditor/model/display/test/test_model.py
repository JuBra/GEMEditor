import pytest
from GEMEditor.model.classes.cobra import Model, Compartment, Metabolite
from GEMEditor.model.display.model import ModelDisplayWidget


class TestModelDisplayWidget:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.parent = QWidget()
        self.widget = ModelDisplayWidget(self.parent)

        self.test_id = "Test_model"
        self.test_name = "Test name"
        self.model = Model(self.test_id,
                           name=self.test_name)

        self.comp1_abbrev = "c"
        self.comp1_name = "Cytoplasm"
        self.comp1 = Compartment(self.comp1_abbrev, self.comp1_name)
        self.model.gem_compartments[self.comp1_abbrev] = self.comp1

        self.gene = Gene(id="test_id", name="test_name")
        self.metabolite = Metabolite(id="test_id", compartment="c")
        self.reaction = Reaction(id="test_id")

        self.model.add_metabolites([self.metabolite])
        self.model.add_reactions([self.reaction])
        self.model.genes.append(self.gene)

    def test_setup(self):
        assert len(self.model.metabolites) == 1
        assert len(self.model.reactions) == 1
        assert len(self.model.genes) == 1
        assert self.model.id == self.test_id
        assert self.model.name == self.test_name
        assert self.model.gem_compartments[self.comp1_abbrev] == self.comp1

    def test_model_addition(self):
        path = "Test_path"
        self.widget.set_model(self.model, path=path)

        assert self.widget.label_model_id.text() == self.test_id
        assert self.widget.label_model_name.text() == self.test_name
        assert self.widget.label_number_genes.text() == str(len(self.model.genes))
        assert self.widget.label_number_reactions.text() == str(len(self.model.reactions))
        assert self.widget.label_number_metabolites.text() == str(len(self.model.metabolites))
        assert self.widget.label_model_path.text() == path

    def test_clear_information(self):
        path = "Test_path"
        self.widget.set_model(self.model, path=path)

        self.widget.clear_information()
        assert self.widget.label_model_name.text() == ""
        assert self.widget.label_model_id.text() == ""
        assert self.widget.label_number_reactions.text() == ""
        assert self.widget.label_number_metabolites.text() == ""
        assert self.widget.label_number_genes.text() == ""
        assert self.widget.label_model_path.text() == path

    def test_setting_empty_model(self):
        path = "Test_path"
        self.widget.set_model(self.model, path=path)

        self.widget.set_model(None)
        assert self.widget.label_model_name.text() == ""
        assert self.widget.label_model_id.text() == ""
        assert self.widget.label_number_reactions.text() == ""
        assert self.widget.label_number_metabolites.text() == ""
        assert self.widget.label_number_genes.text() == ""
        assert self.widget.label_model_path.text() == ""