import pytest
from GEMEditor.model.classes.cobra import Reaction, Gene, GeneGroup, Metabolite, Model
from GEMEditor.rw import *
from GEMEditor.rw.reaction import add_reactions, parse_reaction, _bound_name
from lxml.etree import Element


class TestAddReactions:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.test_id = "test_id"
        self.test_name = "test_name"
        self.test_subsystem = "test_subsystem"
        self.test_comment = "Test_comment"
        self.test_upper_bound = cobra_default_ub_value
        self.test_lower_bound = cobra_default_lb_value
        self.test_objective_coefficient = 1.

        self.reaction = Reaction(id=self.test_id,
                                 name=self.test_name,
                                 subsystem=self.test_subsystem,
                                 lower_bound=self.test_lower_bound,
                                 upper_bound=self.test_upper_bound)
        self.reaction.comment = self.test_comment

        self.metabolite1 = Metabolite(id="test_met1")
        self.metabolite1_coeff = -1
        self.metabolite2 = Metabolite(id="test_met2")
        self.metabolite2_coeff = 1
        self.metabolites = {self.metabolite1: self.metabolite1_coeff,
                            self.metabolite2: self.metabolite2_coeff}

        self.reaction.add_metabolites(self.metabolites)

        self.gene1_id = "gene_id1"
        self.gene1_name = "gene_name1"
        self.gene1 = Gene(id=self.gene1_id,
                          name=self.gene1_name)

        self.gene2_id = "gene_id2"
        self.gene2_name = "gene_name2"
        self.gene2 = Gene(id=self.gene2_id,
                          name=self.gene2_name)

        self.gene3_id = "gene_id3"
        self.gene3_name = "gene_name3"
        self.gene3 = Gene(id=self.gene3_id,
                          name=self.gene3_name)

        self.gene_group_id = "gene_group_id"
        self.gene_group_type = "or"
        self.gene_group = GeneGroup(id=self.gene_group_id,
                                    type=self.gene_group_type)

        self.reaction.add_child(self.gene1)
        self.reaction.add_child(self.gene_group)
        self.gene_group.add_child(self.gene2)
        self.gene_group.add_child(self.gene3)

        self.model = Model(id_or_model="Test")
        self.model.add_reactions([self.reaction])
        self.reaction.objective_coefficient = 1.

    def test_setup_items(self):

        assert self.reaction.id == self.test_id
        assert self.reaction.name == self.test_name
        assert self.reaction.subsystem == self.test_subsystem
        assert self.reaction.comment == self.test_comment
        assert self.reaction.upper_bound == self.test_upper_bound
        assert self.reaction.lower_bound == self.test_lower_bound
        assert self.reaction.objective_coefficient == self.test_objective_coefficient

        assert self.gene1.id == self.gene1_id
        assert self.gene1.name == self.gene1_name

        assert self.gene2.id == self.gene2_id
        assert self.gene2.name == self.gene2_name

        assert self.gene3.id == self.gene3_id
        assert self.gene3.name == self.gene3_name

        assert self.gene_group.id == self.gene_group_id
        assert self.gene_group.type == self.gene_group_type

        assert self.gene1 in self.reaction.genes
        assert self.gene2 in self.reaction.genes
        assert self.gene3 in self.reaction.genes

        assert self.gene2 in self.gene_group._children
        assert self.gene3 in self.gene_group._children
        assert self.gene1 not in self.gene_group._children

        assert len(self.reaction._children) == 2
        assert self.reaction._children[0] is self.gene1
        assert self.reaction._children[1] is self.gene_group

        assert len(self.model.reactions) == 1
        assert self.model.reactions[0] is self.reaction

        assert len(self.model.metabolites) == 2
        assert self.model.metabolites.get_by_id(self.metabolite1.id) is self.metabolite1
        assert self.model.metabolites.get_by_id(self.metabolite2.id) is self.metabolite2

        assert self.reaction.metabolites == {self.metabolite1: self.metabolite1_coeff,
                                             self.metabolite2: self.metabolite2_coeff}

    def test_parse_reaction(self):

        root = Element("root")
        add_reactions(root, self.model)

        assert len(root) == 3

        reaction_list_node = root.find(sbml3_listOfReactions)
        assert reaction_list_node is not None
        assert len(reaction_list_node) == 1

        reaction_node = reaction_list_node.find(sbml3_reaction)
        assert reaction_node is not None
        assert reaction_node.get("id") == cobra_reaction_prefix + self.test_id
        assert reaction_node.get("name") == self.test_name
        assert reaction_node.get(ge_subsystem) == self.test_subsystem
        assert reaction_node.get(ge_comment) == self.test_comment
        assert reaction_node.get(fbc_upperFluxBound) == cobra_default_ub_name
        assert reaction_node.get(fbc_lowerFluxBound) == cobra_default_lb_name

        assert len(reaction_node) == 3

        reactant_list_node = reaction_node.find(sbml3_listOfReactants)
        assert reactant_list_node is not None
        assert len(reactant_list_node) == 1

        reactant_node = reactant_list_node.find(sbml3_speciesReference)
        assert reactant_node is not None
        assert reactant_node.get("species") == cobra_metabolite_prefix + self.metabolite1.id
        assert reactant_node.get("stoichiometry") == str(abs(self.metabolite1_coeff))

        product_list_node = reaction_node.find(sbml3_listOfProducts)
        assert product_list_node is not None
        assert len(product_list_node) == 1

        product_node = product_list_node.find(sbml3_speciesReference)
        assert product_node is not None
        assert product_node.get("species") == cobra_metabolite_prefix + self.metabolite2.id
        assert product_node.get("stoichiometry") == str(abs(self.metabolite2_coeff))

        list_of_geneassociations = reaction_node.find(fbc_geneProductAssociation)
        assert list_of_geneassociations is not None
        assert len(list_of_geneassociations) == 1

        gene_group_node = list_of_geneassociations.find(fbc_or)
        assert gene_group_node is not None
        assert gene_group_node.get(ge_id) is None

        assert len(gene_group_node) == 2
        gene_node = gene_group_node.find(fbc_geneProductRef)
        assert gene_node is not None
        assert gene_node.get(fbc_geneProduct) == cobra_gene_prefix + self.gene1_id

        gene_group_node2 = gene_group_node.find(fbc_or)
        assert gene_group_node2 is not None
        assert gene_group_node2.get(ge_id) == self.gene_group_id
        assert len(gene_group_node2) == 2

        for x in gene_group_node2:
            assert x.tag == fbc_geneProductRef
            assert x.get(fbc_geneProduct) in [cobra_gene_prefix + self.gene2_id,
                                              cobra_gene_prefix + self.gene3_id]

        objective_list_node = root.find(fbc_listOfObjectives)
        assert objective_list_node is not None
        assert len(objective_list_node) == 1

        objective_node = objective_list_node.find(fbc_objective)
        assert objective_node is not None
        assert len(objective_node) == 1

        list_of_fluxobjectives = objective_node.find(fbc_listOfFluxObjectives)
        assert list_of_fluxobjectives is not None
        assert len(list_of_fluxobjectives) == 1

        flux_objective_node = list_of_fluxobjectives.find(fbc_fluxObjective)
        assert flux_objective_node is not None
        assert len(flux_objective_node) == 0

        assert flux_objective_node.get(fbc_reaction) == cobra_reaction_prefix + self.test_id
        assert flux_objective_node.get(fbc_coefficient) == "1"

    def test_addition_of_optional_attributes_only_when_set(self):
        root = Element("root")
        reaction = Reaction(id="Test")
        model = Model("Testmodel")
        model.add_reactions([reaction])
        add_reactions(root, model)

        reaction_node = root.find("/".join([sbml3_listOfReactions, sbml3_reaction]))
        assert reaction_node is not None
        assert reaction_node.get("name") is None
        assert reaction_node.get(ge_subsystem) is None
        assert reaction_node.get(ge_comment) is None

    def test_write_read_consistency(self):

        root = Element("root")
        add_reactions(root, self.model)

        model = Model("New model")
        model.genes.append(self.gene1)
        model.genes.append(self.gene2)
        model.genes.append(self.gene3)
        model.add_metabolites([self.metabolite1, self.metabolite2])
        reactions = parse_reaction(root, model)

        assert len(reactions) == 1
        reaction = reactions[0]

        assert reaction.id == self.test_id
        assert reaction.name == self.test_name
        assert reaction.comment == self.test_comment
        assert reaction.subsystem == self.test_subsystem
        assert reaction.upper_bound == self.test_upper_bound
        assert reaction.lower_bound == self.test_lower_bound
        assert reaction.objective_coefficient == self.test_objective_coefficient

        # Test genes
        assert self.gene1 in reaction.genes
        assert self.gene2 in reaction.genes
        assert self.gene3 in reaction.genes

        assert len(reaction.genes) == 3
        reaction_ids = [(x.id, x.name) for x in reaction.genes]
        assert (self.gene1.id, self.gene1.name) in reaction_ids
        assert (self.gene2.id, self.gene2.name) in reaction_ids
        assert (self.gene3.id, self.gene3.name) in reaction_ids

        # Test the children structure
        assert len(reaction._children) == 1
        top_genegroup = reaction._children[0]
        assert isinstance(top_genegroup, GeneGroup)
        assert top_genegroup.type == "or"
        assert len(top_genegroup._children) == 2
        assert top_genegroup._children[0] is self.gene1
        child_genegroup = top_genegroup._children[1]
        assert isinstance(child_genegroup, GeneGroup)
        assert len(child_genegroup._children) == 2
        assert child_genegroup._children[0] is self.gene2
        assert child_genegroup._children[1] is self.gene3

        assert reaction.metabolites == self.metabolites


class TestBoundName:

    def test_bound_name(self):

        assert _bound_name(-1000.) == "neg_1000.0"
        assert _bound_name(0.) == "pos_0.0"
        assert _bound_name(0) == "pos_0"
        assert _bound_name(1000) == "pos_1000"
