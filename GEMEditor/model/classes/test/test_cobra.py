import gc

import pytest
from GEMEditor.model.classes.cobra import Reaction, GeneGroup, Gene, Model, prune_gene_tree, Metabolite, CleaningDict, Compartment
from GEMEditor.model.classes.modeltest import ModelTest, ReactionSetting, GeneSetting, Outcome
from GEMEditor.model.classes.reference import Reference
from GEMEditor.model.classes.evidence import Evidence
from PyQt5.QtWidgets import QApplication

# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


@pytest.fixture()
def ex_empty_reaction():
    return Reaction(id="test", name="test")


@pytest.fixture()
def ex_empty_geneGroup():
    return GeneGroup()


@pytest.fixture()
def ex_empty_gene():
    return Gene(id="test", name="test")


def test_genegroup_gene_addition(ex_empty_geneGroup):
    test_gene = Gene(id="test", name="test")
    ex_empty_geneGroup.add_child(test_gene)

    # Check that the child is set in geneGroup
    assert test_gene in ex_empty_geneGroup._children
    # Check that the parent is set in gene
    assert ex_empty_geneGroup in test_gene._parents

    # Check removal of child gene
    ex_empty_geneGroup.remove_child(test_gene)
    assert test_gene not in ex_empty_geneGroup._children
    assert ex_empty_geneGroup not in test_gene._parents


def test_genegroup_genegroup_addition():
    group1 = ex_empty_geneGroup()
    group2 = ex_empty_geneGroup()

    # Add group2 to group1
    group1.add_child(group2)
    assert group2 in group1._children
    assert group1 in group2._parents

    # Remove group2 from group1
    group1.remove_child(group2)
    assert group2 not in group1._children
    assert group2._parents == []


def test_getting_reaction_from_genegroups():
    reaction = ex_empty_reaction()
    group1 = ex_empty_geneGroup()
    group2 = ex_empty_geneGroup()

    group1.add_child(group2)
    reaction.add_child(group1)
    assert reaction in group1.reactions
    assert reaction in group2.reactions


def test_retrieval_of_genes_reaction():
    reaction = ex_empty_reaction()
    group1 = ex_empty_geneGroup()
    group2 = ex_empty_geneGroup()
    gene1 = ex_empty_gene()

    group2.add_child(gene1)
    group1.add_child(group2)

    # Check the retrieval of the gene from the reaction
    reaction.add_child(group1)
    assert gene1 in reaction.genes

    # Check retrieval of reaction from gene
    assert reaction in gene1.reactions


def test_direct_retrieval_of_genes_reaction():
    reaction = ex_empty_reaction()
    gene1 = ex_empty_gene()
    reaction.add_child(gene1)

    assert reaction in gene1.reactions


@pytest.fixture()
def ex_reaction():
    test_reaction = Reaction(id="test", name="test")

    gene1 = Gene("Gene1")
    gene2 = Gene("Gene2")
    gene3 = Gene("Gene3")

    gene_group1 = GeneGroup()
    gene_group1.add_child(gene1)

    gene_group2 = GeneGroup()
    gene_group2.add_child(gene2)
    gene_group2.add_child(gene3)


    gene_group1.add_child(gene_group2)

    test_reaction.add_child(gene3)
    test_reaction.add_child(gene_group1)

    return test_reaction


class TestReaction:

    @pytest.fixture()
    def setup_item(self):
        self.test_id = "test_id"
        self.test_name = "test_name"
        self.test_upper_bound = 1000.
        self.test_lower_bound = -1000.
        self.reaction = Reaction(id=self.test_id,
                                 name=self.test_name,
                                 lower_bound=self.test_lower_bound,
                                 upper_bound=self.test_upper_bound)

    @pytest.mark.usefixtures("setup_item")
    def test_setup_item(self):
        assert self.reaction.id == self.test_id
        assert self.reaction.name == self.test_name
        assert self.reaction.upper_bound == self.test_upper_bound
        assert self.reaction.lower_bound == self.test_lower_bound
        assert self.reaction._model is None

    def test_empty_reaction_setup(self):
        reaction = Reaction()

        assert reaction.id == ""
        assert reaction.name == ""
        assert reaction.subsystem == ""
        assert reaction.lower_bound == 0.
        assert reaction.upper_bound == 1000.
        assert reaction.comment == ""
        assert reaction.annotation == set()
        assert reaction.model is None
        assert len(reaction._children) == 0

    def test_none_reaction_setup(self):
        reaction = Reaction(id=None,
                            name=None,
                            subsystem=None,
                            lower_bound=None,
                            upper_bound=None,
                            comment=None)

        assert reaction.id == ""
        assert reaction.name == ""
        assert reaction.subsystem == ""
        assert reaction.lower_bound == 0.
        assert reaction.upper_bound == 1000.
        assert reaction.comment == ""
        assert len(reaction._children) == 0

    @pytest.mark.usefixtures("setup_item")
    @pytest.mark.parametrize("lower_bound,upper_bound,objective", [(0., 1000., 0.),
                                                                   (-1000., 1000., 1.),
                                                                   (-1000., 0., 20.),
                                                                   (0., 0., 0.)])
    def test_get_setting(self, lower_bound, upper_bound, objective):
        self.reaction.upper_bound = upper_bound
        self.reaction.lower_bound = lower_bound
        setting = self.reaction.get_setting()
        assert setting.reaction is self.reaction
        assert setting.upper_bound == upper_bound
        assert setting.lower_bound == lower_bound

    def test_gene_addition(self):
        reaction = Reaction("reaction_id")
        gene = Gene("gene_id")

        reaction.add_child(gene)
        assert gene in reaction.genes
        assert reaction in gene.reactions

    def test_reaction_gene_addition(self, ex_empty_reaction):
        test_gene = Gene(id="test", name="test")

        # Check addition
        ex_empty_reaction.add_child(test_gene)
        assert test_gene in ex_empty_reaction._children
        assert ex_empty_reaction in test_gene._parents

        # Check removal
        ex_empty_reaction.remove_child(test_gene)
        assert test_gene not in ex_empty_reaction._children
        assert ex_empty_reaction not in test_gene._parents

    def test_reaction_genegroup_addition(self):
        reaction = ex_empty_reaction()
        genegroup = ex_empty_geneGroup()

        # Check addition and references
        reaction.add_child(genegroup)
        assert genegroup in reaction._children
        assert reaction in genegroup._parents

        # Check removal
        reaction.remove_child(genegroup)
        assert genegroup not in reaction._children
        assert genegroup._parents == []

    @pytest.mark.parametrize("parent", [Gene(), GeneGroup(), Reaction()])
    def test_add_parent(self, parent):
        reaction = Reaction()
        with pytest.raises(NotImplementedError):
            reaction.add_parent(parent)

    @pytest.mark.parametrize("parent", [Gene(), GeneGroup(), Reaction()])
    def test_remove_parent(self, parent):
        reaction = Reaction()
        with pytest.raises(NotImplementedError):
            reaction.remove_parent(parent)

    @pytest.mark.usefixtures("setup_item")
    def test_reaction_subsystem_setting(self):
        model = Model()

        # Test subsystem setting while reaction not in model
        new_subsystem1 = "New subsystem"
        self.reaction.subsystem = new_subsystem1
        assert self.reaction.subsystem == new_subsystem1

        # Test that the subsystem is updated on the model
        model.add_reactions([self.reaction])
        assert model is self.reaction._model
        assert len(model.subsystems) == 1
        assert new_subsystem1 in model.subsystems
        assert self.reaction in model.subsystems[new_subsystem1]

        # Test that changing the subsystem is reflected in model.subsystems
        new_subsystem2 = "Different Stubsystem"
        self.reaction.subsystem = new_subsystem2
        assert len(model.subsystems) == 1
        assert new_subsystem2 in model.subsystems
        assert self.reaction in model.subsystems[new_subsystem2]

    def test_reaction_enabled_without_genes(self):
        reaction = Reaction()
        assert reaction.functional is True

    def test_reaction_enabled_true_with_empty_genegroup(self):
        reaction = Reaction()
        genegroup = GeneGroup()
        reaction.add_child(genegroup)

        assert reaction.functional is True

    def test_reaction_is_disabled_with_disabled_gene_only(self):
        reaction = Reaction()
        gene = Gene()
        gene.functional = False
        reaction.add_child(gene)

        assert reaction.functional is False

    def test_reaction_is_disabled_with_gene_in_or_group(self):
        reaction = Reaction()
        genegroup = GeneGroup(type="or")
        reaction.add_child(genegroup)
        gene = Gene()
        genegroup.add_child(gene)
        gene.functional = False

        assert reaction.functional is False

    def test_reaction_is_disabled_with_gene_in_and_group(self):
        reaction = Reaction()
        genegroup = GeneGroup(type="and")
        reaction.add_child(genegroup)
        gene = Gene()
        genegroup.add_child(gene)
        gene.functional = False

        assert reaction.functional is False


class TestGeneGroup:

    def test_empty_gene_group_setup(self):
        gene_group = GeneGroup()

        assert gene_group.id
        assert gene_group.type == "and"

    def test_unlinking_of_genegroup(self):
        reaction = ex_empty_reaction()
        group1 = ex_empty_geneGroup()
        group2 = ex_empty_geneGroup()
        gene1 = ex_empty_gene()

        group2.add_child(gene1)
        group1.add_child(group2)
        reaction.add_child(group1)

        group1.delete_children()
        assert group2._parents == []
        assert group2 not in group1._children
        assert group2 not in gene1._parents

    def test_genegroup_children_removal(self):
        group1 = ex_empty_geneGroup()
        gene1 = ex_empty_gene()
        gene2 = ex_empty_gene()
        group1.add_child(gene1)
        group1.add_child(gene1)

        assert group1._children.count(gene1) == 2

        # Check KeyError for element not in children
        with pytest.raises(ValueError):
            group1.remove_child(gene2)
        assert group1._children.count(gene1) == 2

    def test_genegroup_children_removal2(self):
        group1 = ex_empty_geneGroup()
        gene1 = ex_empty_gene()
        group1.add_child(gene1)
        group1.add_child(gene1)

        # Check removal of all occurence
        group1.remove_child(gene1, all=True)
        assert group1._children == []
        assert group1 not in gene1._parents

    def test_genegroup_children_removal3(self):
        group1 = ex_empty_geneGroup()
        gene1 = ex_empty_gene()
        group1.add_child(gene1)
        group1.add_child(gene1)

        # Check removal of one occurence
        group1.remove_child(gene1, 0)
        assert len(group1._children) == 1
        assert group1 in gene1._parents

    def test_genegroup_enabled_for_empty_group(self):
        genegroup = GeneGroup()
        assert genegroup.functional is None

    def test_genegroup_enabled_different_genes(self):
        group1 = GeneGroup()
        gene1 = Gene()
        gene1.functional = False
        group1.add_child(gene1)

        group1.type = "and"
        assert group1.functional is False

        group1.type = "or"
        assert group1.functional is False

        # Add second functional gene
        gene2 = Gene()
        gene2.functional = True
        group1.add_child(gene2)

        group1.type = "and"
        assert group1.functional is False

        group1.type = "or"
        assert group1.functional is True

        group1.type = "unknown"
        with pytest.raises(ValueError):
            group1.functional


class TestGene:

    def test_default_values(self):
        gene = Gene()
        assert gene.id == ""
        assert gene.name == ""
        assert gene.genome == ""
        assert gene.annotation == set()
        assert gene.functional is True

    @pytest.mark.parametrize("child", [Gene(), Reaction(), GeneGroup()])
    def test_gene_add_child(self, child):
        gene = Gene()
        with pytest.raises(NotImplementedError):
            gene.add_child(child)

    @pytest.mark.parametrize("child", [Gene(), Reaction(), GeneGroup()])
    def test_gene_remove_child(self, child):
        gene = Gene()
        with pytest.raises(NotImplementedError):
            gene.remove_child(child)


class TestModel:

    def test_model_setup(self):
        model = Model()
        assert isinstance(model.subsystems, CleaningDict)
        assert len(model.subsystems) == 0

    def test_updating(self):
        model = Model()
        met1 = Metabolite(id="met1", formula="H2O", name="Water", charge=0., compartment="c")
        react1 = Reaction(id="react1", name="test2", subsystem="test2", lower_bound=0., upper_bound=1000.)
        react1.add_metabolites({met1: -1})

        model.add_metabolites([met1])
        model.add_reactions([react1])
        model.setup_tables()

        assert model.QtReactionTable.rowCount() == 1
        assert model.QtMetaboliteTable.rowCount() == 1

        # Check that content is right
        for i, element in enumerate(model.QtMetaboliteTable.header):
            assert str(getattr(met1, element.lower())) == model.QtMetaboliteTable.item(0, i).text()

        # Check that metabolite id is in table
        assert met1.id in model.QtReactionTable.item(0, 2).text()

        # Change metabolite
        met1.id = "new_id"
        met1.name = "new_name"
        met1.formula = "H2O2"
        met1.name = "None"
        met1.charge = 1.
        met1.compartment = "e"

        # Tables are out of sync
        for i, element in enumerate(model.QtMetaboliteTable.header):
            assert str(getattr(met1, element.lower())) != model.QtMetaboliteTable.item(0, i).text()

        # Check reaction table out of sync
        assert react1.id not in model.QtReactionTable.item(0, 2).text()

        model.gem_update_metabolites([met1])

        # Metabolite table updated
        for i, element in enumerate(model.QtMetaboliteTable.header):
            assert str(getattr(met1, element.lower())) == model.QtMetaboliteTable.item(0, i).text()

        # Reaction table updated
        assert met1.id in model.QtReactionTable.item(0, 2).text()


class TestMetabolite:

    def test_standard_values(self):
        metabolite = Metabolite()
        assert metabolite.id == ""
        assert metabolite.name == ""
        assert metabolite.charge == 0
        assert metabolite.compartment == ""
        assert metabolite.annotation == set()


class TestReactionsAttribute:

    @pytest.fixture()
    def reaction(self):
        return Reaction()

    @pytest.fixture()
    def gene(self):
        return Gene()

    @pytest.fixture()
    def genegroup(self):
        return GeneGroup()

    def test_empty_reaction(self, reaction):
        assert reaction.reactions == set([reaction])

    def test_empty_gene(self, gene):
        assert gene.reactions == set()

    def test_empty_genegroup(self, genegroup):
        assert genegroup.reactions == set()

    def test_empty_set_if_no_reaction(self, gene, genegroup):
        genegroup.add_child(gene)
        assert gene.reactions == set()
        assert genegroup.reactions == set()

    def test_direct_link_gene_group(self, reaction, genegroup):
        reaction.add_child(genegroup)
        assert genegroup.reactions == set([reaction])

    def test_direct_link_gene(self, reaction, gene):
        reaction.add_child(gene)
        assert gene.reactions == set([reaction])

    def test_chain_length_one(self, reaction, gene, genegroup):
        genegroup.add_child(gene)
        reaction.add_child(genegroup)
        assert gene.reactions == set([reaction])

    def test_chain_length_two(self, reaction, gene, genegroup):
        genegroup2 = self.genegroup()
        genegroup.add_child(gene)
        genegroup2.add_child(genegroup)
        assert gene.reactions == set()
        assert genegroup.reactions == set()
        assert genegroup2.reactions == set()
        reaction.add_child(genegroup2)
        assert gene.reactions == set([reaction])
        assert genegroup.reactions == set([reaction])
        assert genegroup2.reactions == set([reaction])

    def test_multiple_reactions(self, reaction, gene):
        reaction2 = self.reaction()
        reaction.add_child(gene)
        reaction2.add_child(gene)
        assert gene.reactions == set([reaction, reaction2])


class TestGenesAttribute:

    @pytest.fixture()
    def reaction(self):
        return Reaction()

    @pytest.fixture()
    def gene(self):
        return Gene()

    @pytest.fixture()
    def genegroup(self):
        return GeneGroup()

    def test_empty_reaction(self, reaction):
        assert reaction.genes == set()

    def test_empty_gene(self, gene):
        assert gene.genes == set([gene])

    def test_empty_genegroup(self, genegroup):
        assert genegroup.reactions == set()

    def test_empty_set_if_no_gene(self, reaction, genegroup):
        reaction.add_child(genegroup)
        assert reaction.genes == set()
        assert genegroup.genes == set()

    def test_direct_link_gene_group(self, gene, genegroup):
        gene.add_parent(genegroup)
        assert genegroup.genes == set([gene])

    def test_direct_link_reaction(self, reaction, gene):
        reaction.add_child(gene)
        assert reaction.genes == set([gene])

    def test_chain_length_one(self, reaction, gene, genegroup):
        genegroup.add_child(gene)
        reaction.add_child(genegroup)
        assert reaction.genes == set([gene])

    def test_chain_length_two(self, reaction, gene, genegroup):
        genegroup2 = self.genegroup()
        reaction.add_child(genegroup2)
        genegroup2.add_child(genegroup)
        assert reaction.genes == set()
        assert genegroup.genes == set()
        assert genegroup2.genes == set()
        genegroup.add_child(gene)
        assert reaction.genes == set([gene])
        assert genegroup.genes == set([gene])
        assert genegroup2.genes == set([gene])

    def test_multiple_genes(self, reaction, gene):
        gene2 = Gene()
        reaction.add_child(gene)
        reaction.add_child(gene2)
        assert reaction.genes == set([gene, gene2])


class TestGeneReactionRule:

    @pytest.fixture()
    def reaction(self):
        return Reaction()

    def test_empty_reaction(self, reaction):
        assert reaction.gene_reaction_rule == ""

    def test_one_gene_reaction(self, reaction):
        gene = Gene("test id")
        reaction.add_child(gene)
        assert reaction.gene_reaction_rule == gene.id

    def test_one_gene_genegroup(self):
        gene = Gene("test 1")
        genegroup = GeneGroup()
        genegroup.add_child(gene)
        assert genegroup.gem_reaction_rule == gene.id

    def test_gene_only(self):
        gene = Gene("test 1")
        assert gene.gem_reaction_rule == gene.id

    def test_two_genes_one_gene_group(self, reaction):
        gene1 = Gene("test 1")
        gene2 = Gene("test 2")
        group = GeneGroup(type="and")
        group.add_child(gene1)
        group.add_child(gene2)
        reaction.add_child(group)
        assert reaction.gene_reaction_rule == gene1.id + " and " + gene2.id
        group.type = "or"
        assert reaction.gene_reaction_rule == gene1.id + " or " + gene2.id

    def test_nested_genegroups_wo_gene(self):
        genegroup1 = GeneGroup()
        genegroup2 = GeneGroup()
        genegroup1.add_child(genegroup2)
        assert genegroup1.gem_reaction_rule == ""

    def test_nested_genegroups_with_gene(self):
        genegroup1 = GeneGroup()
        genegroup2 = GeneGroup()
        gene = Gene("gene id")
        genegroup1.add_child(genegroup2)
        genegroup2.add_child(gene)
        assert genegroup1.gem_reaction_rule == gene.id
        gene2 = Gene("gene2 id")
        genegroup2.add_child(gene2)
        assert genegroup1.gem_reaction_rule == "("+gene.id+" and "+gene2.id+")"

    def test_multiple_nested(self):
        reaction = Reaction()
        parent = reaction
        for _ in range(5):
            genegroup = GeneGroup()
            parent.add_child(genegroup)
            parent = genegroup
        gene = Gene("Gene id")
        parent.add_child(gene)
        assert reaction.gene_reaction_rule == gene.id
        gene2 = Gene("Gene 2")
        parent.add_child(gene2)
        assert reaction.gene_reaction_rule == "(" + gene.id+" and "+gene2.id+")"

    def test_gene_and_gene_group(self):
        gene1 = Gene("gene 1")
        gene2 = Gene("gene 2")
        gene3 = Gene("gene 3")
        genegroup1 = GeneGroup(type="and")
        genegroup2 = GeneGroup(type="or")
        reaction = Reaction()
        reaction.add_child(genegroup1)
        genegroup1.add_child(gene1)
        genegroup1.add_child(genegroup2)
        genegroup2.add_child(gene2)
        assert reaction.gene_reaction_rule == gene1.id+" and "+gene2.id
        genegroup2.add_child(gene3)
        assert reaction.gene_reaction_rule == gene1.id+" and ("+gene2.id+" or "+gene3.id+")"


class TestDeleteChildren:

    def test_delete_children(self):
        reaction = Reaction()
        reaction2 = Reaction()
        genegroup = GeneGroup()
        gene = Gene()

        reaction.add_child(genegroup)
        reaction2.add_child(genegroup)
        genegroup.add_child(gene)
        assert genegroup in reaction._children
        assert reaction in genegroup._parents
        assert genegroup in reaction2._children
        assert reaction2 in genegroup._parents
        assert gene in genegroup._children
        assert genegroup in gene._parents
        reaction.delete_children()
        assert genegroup not in reaction._children
        assert reaction not in genegroup._parents
        assert gene not in genegroup._children
        assert genegroup not in gene._parents
        assert genegroup in reaction2._children
        assert reaction2 in genegroup._parents


class TestModelAddReactions:

    def test_add_reactions(self):
        # Todo: Implement
        assert True


class TestGeneTreePruning:

    def test_reaction_wo_children(self):
        reaction = Reaction("r1")
        prune_gene_tree(reaction)
        assert True

    def test_removal_empty_genegroup(self):
        reaction = Reaction("r1")
        gene_group = GeneGroup()
        reaction.add_child(gene_group)

        assert gene_group in reaction._children
        assert reaction in gene_group._parents
        prune_gene_tree(reaction)

        assert gene_group not in reaction._children
        assert reaction not in gene_group._parents

    @pytest.mark.parametrize("type", ("or", "and"))
    def test_removal_of_genegroup_with_one_child(self, type):
        reaction = Reaction("r1")
        gene_group = GeneGroup(type=type)
        gene = Gene()
        reaction.add_child(gene_group)
        gene_group.add_child(gene)

        assert gene_group in reaction._children
        assert reaction in gene_group._parents
        assert gene in reaction.genes
        prune_gene_tree(reaction)

        assert gene_group not in reaction._children
        assert reaction not in gene_group._parents
        assert gene in reaction.genes

    def test_removal_of_nested_or_groups(self):
        reaction = Reaction("r1")
        gene_group1 = GeneGroup(type="or")
        gene_group2 = GeneGroup(type="or")
        gene1 = Gene("g1")
        gene2 = Gene("g2")
        gene3 = Gene("g3")
        gene_group1.add_child(gene1)
        for x in (gene2, gene3):
            gene_group2.add_child(x)
        gene_group1.add_child(gene_group2)
        reaction.add_child(gene_group1)

        assert reaction.genes == set([gene1, gene2, gene3])
        prune_gene_tree(reaction)
        assert reaction.genes == set([gene1, gene2, gene3])
        assert not gene_group2._children
        assert not gene_group2._parents


def metabolite_in_model(metabolite, model, valid=True):
    assert (metabolite in model.metabolites) is valid
    assert (metabolite in model.QtMetaboliteTable.get_items()) is valid
    assert (model is metabolite.model) is valid


def reaction_in_model(reaction, model, valid=True):
    assert (reaction in model.reactions) is valid
    assert (reaction in model.QtReactionTable.get_items()) is valid
    assert (model is reaction.model) is valid


def gene_in_model(gene, model, valid=True):
    assert (gene in model.genes) is valid
    assert (gene in model.QtGeneTable.get_items()) is valid
    assert (model is gene.model) is valid


def metabolite_in_reaction(metabolite, reaction, valid=True):
    assert (reaction in metabolite.reactions) is valid
    assert (metabolite in reaction.metabolites) is valid


def case_in_model(case, model, valid=True):
    assert (case in model.tests) is valid
    assert (case in model.QtTestsTable.get_items()) is valid


def item_in_evidence(item, evidence, valid=True):
    assert (evidence in item.evidences) is valid
    assert any(item is getattr(evidence, name) for name in ("entity", "target")) is valid


def reference_in_model(reference, model, valid=True):
    assert (reference in model.references.values()) is valid
    assert (reference in model.QtReferenceTable.get_items()) is valid


def evidence_in_model(evidence, model, valid=True):
    if valid is not True:
        raise ValueError("Cannot check evidence not in model as the test still holds a strong ref to evidence.")
    gc.collect()
    assert (evidence in model.all_evidences.values()) is valid


def gene_in_reaction(gene, reaction, valid=True):
    assert (gene in reaction.genes) is valid
    assert (reaction in gene.reactions) is valid


def reference_in_item(reference, item, valid=True):
    assert (reference in item.references) is valid
    assert (item in reference.linked_items) is valid


class TestModelDeleteItems:

    @pytest.fixture(autouse=True)
    def setup_complete_model(self):
        self.model = Model("model")

        # Setup reaction1
        self.metabolite = Metabolite("m1")
        self.reaction = Reaction("r1")
        self.gene = Gene("g1")
        self.reaction.add_child(self.gene)
        self.model.add_genes((self.gene,))
        self.reaction.add_metabolites({self.metabolite: -1})
        self.model.add_reactions((self.reaction,))

        # Setup reaction2
        self.metabolite2 = Metabolite("m2")
        self.reaction2 = Reaction("r2")
        self.gene2 = Gene("g2")
        self.genegroup = GeneGroup()
        self.genegroup.add_child(self.gene2)
        self.reaction2.add_child(self.genegroup)
        self.model.add_genes((self.gene2,))
        self.reaction2.add_metabolites({self.metabolite2: 1})
        self.model.add_reactions((self.reaction2,))

        # Setup evidences
        self.evidence = Evidence(assertion="Catalyzes")
        self.evidence.set_entity(self.gene)
        self.evidence.set_target(self.reaction)
        self.reference = Reference()
        self.model.add_reference(self.reference)
        self.evidence.add_reference(self.reference)
        self.model.add_evidence(self.evidence)

        # Setup test case
        self.testcase = ModelTest()
        reaction_setting = ReactionSetting(self.reaction, 1000., -1000., 0.)
        gene_setting = GeneSetting(gene=self.gene2, activity=False)
        outcome = Outcome(self.reaction2, 0., "greater")
        self.testcase.add_outcome(outcome)
        self.testcase.add_setting(gene_setting)
        self.testcase.add_setting(reaction_setting)
        self.model.add_test(self.testcase)
        self.reference2 = Reference()
        self.model.add_reference(self.reference2)
        self.testcase.add_reference(self.reference2)

        self.model.setup_tables()

    def test_setup(self):
        # Test genes
        gene_in_model(self.gene, self.model)
        gene_in_model(self.gene2, self.model)

        # Test reactions
        reaction_in_model(self.reaction, self.model)
        reaction_in_model(self.reaction2, self.model)

        # Test metabolites
        metabolite_in_model(self.metabolite, self.model)
        metabolite_in_model(self.metabolite2, self.model)

        # Test evidences
        evidence_in_model(self.evidence, self.model)

        # Test model test
        case_in_model(self.testcase, self.model)

        # Test references
        reference_in_model(self.reference, self.model)
        reference_in_model(self.reference2, self.model)

        # Test connections
        # Reference <-> Evidence
        reference_in_item(self.reference, self.evidence)
        # Reference2 <-> Testcase
        reference_in_item(self.reference2, self.testcase)

        # Gene1 <-> Reaction1
        gene_in_reaction(self.gene, self.reaction)
        gene_in_reaction(self.gene2, self.reaction2)

        # Metabolite1 <-> Reaction1
        metabolite_in_reaction(self.metabolite, self.reaction)
        metabolite_in_reaction(self.metabolite2, self.reaction2)

        # Evidence <-> Gene1/Reaction
        item_in_evidence(self.gene, self.evidence)
        item_in_evidence(self.reaction, self.evidence)

    def test_deletion_metabolite(self):
        # Action
        self.model.gem_remove_metabolites((self.metabolite,))

        # Test gene
        gene_in_model(self.gene, self.model)
        gene_in_model(self.gene2, self.model)

        # Test reactions
        reaction_in_model(self.reaction, self.model)
        reaction_in_model(self.reaction2, self.model)

        # Test metabolites
        metabolite_in_model(self.metabolite, self.model, valid=False)
        metabolite_in_model(self.metabolite2, self.model)

        # Test evidences
        evidence_in_model(self.evidence, self.model)

        # Test model test
        case_in_model(self.testcase, self.model)

        # Test references
        reference_in_model(self.reference, self.model)
        reference_in_model(self.reference2, self.model)

        # Test connections
        # Reference <-> Evidence
        reference_in_item(self.reference, self.evidence)
        # Reference2 <-> Testcase
        reference_in_item(self.reference2, self.testcase)

        # Gene1 <-> Reaction1
        gene_in_reaction(self.gene, self.reaction)
        gene_in_reaction(self.gene2, self.reaction2)

        # Metabolite1 <-> Reaction1
        metabolite_in_reaction(self.metabolite, self.reaction, valid=False)
        metabolite_in_reaction(self.metabolite2, self.reaction2)

        # Evidence <-> Gene1/Reaction
        item_in_evidence(self.gene, self.evidence)
        item_in_evidence(self.reaction, self.evidence)

    def test_deletion_metabolite2(self):
        # Action
        self.model.gem_remove_metabolites((self.metabolite2,))

        # Test genes
        gene_in_model(self.gene, self.model)
        gene_in_model(self.gene2, self.model)

        # Test reactions
        reaction_in_model(self.reaction, self.model)
        reaction_in_model(self.reaction2, self.model)

        # Test metabolites
        metabolite_in_model(self.metabolite, self.model)
        metabolite_in_model(self.metabolite2, self.model, valid=False)

        # Test evidences
        evidence_in_model(self.evidence, self.model)

        # Test model test
        case_in_model(self.testcase, self.model)

        # Test references
        reference_in_model(self.reference, self.model)
        reference_in_model(self.reference2, self.model)

        # Test connections
        # Reference <-> Evidence
        reference_in_item(self.reference, self.evidence)
        # Reference2 <-> Testcase
        reference_in_item(self.reference2, self.testcase)

        # Gene1 <-> Reaction1
        gene_in_reaction(self.gene, self.reaction)
        gene_in_reaction(self.gene2, self.reaction2)

        # Metabolite1 <-> Reaction1
        metabolite_in_reaction(self.metabolite, self.reaction)
        metabolite_in_reaction(self.metabolite2, self.reaction2, valid=False)

        # Evidence <-> Gene1/Reaction
        item_in_evidence(self.gene, self.evidence)
        item_in_evidence(self.reaction, self.evidence)

    def test_delete_reaction1(self):
        ####
        # Delete reaction
        # Check:
        #   - gene present but removed from reaction1
        #   - metabolite present but removed from reaction1
        #   - reaction deleted
        #   - evidence deleted
        #   - testcase deleted
        #   - reference present but removed from evidence
        #   - reference2 present but removed from testcase
        ####

        # Action
        self.model.gem_remove_reactions((self.reaction,))

        # Test genes
        gene_in_model(self.gene, self.model)
        gene_in_model(self.gene2, self.model)

        # Test reactions
        reaction_in_model(self.reaction, self.model, valid=False)
        reaction_in_model(self.reaction2, self.model)

        # Test metabolites
        metabolite_in_model(self.metabolite, self.model)
        metabolite_in_model(self.metabolite2, self.model)

        # Test model test
        case_in_model(self.testcase, self.model, valid=False)

        # Test references
        reference_in_model(self.reference, self.model)
        reference_in_model(self.reference2, self.model)

        # Test connections
        # Reference <-> Evidence
        reference_in_item(self.reference, self.evidence, valid=False)
        reference_in_item(self.reference2, self.testcase, valid=False)

        # Gene1 <-> Reaction1
        gene_in_reaction(self.gene, self.reaction, valid=False)
        gene_in_reaction(self.gene2, self.reaction2)

        # Metabolite1 <-> Reaction1
        # Check metabolite is still in reaction, but reaction not in metabolite
        assert self.metabolite in self.reaction.metabolites
        assert self.reaction not in self.metabolite.reactions
        metabolite_in_reaction(self.metabolite2, self.reaction2)

        # Evidence <-> Gene1/Reaction
        item_in_evidence(self.gene, self.evidence, valid=False)
        item_in_evidence(self.reaction, self.evidence, valid=False)

        # Check evidence is removed when reference deleted
        del self.evidence
        gc.collect()
        assert len(self.model.all_evidences) == 0

    def test_deletion_reaction2(self):
        # Check:
        #   - reaction2 removed
        #   - test case removed
        #   - reference removed from testcase
        #   - gene2 removed from reaction

        # Action
        self.model.gem_remove_reactions((self.reaction2,))

        # Test genes
        gene_in_model(self.gene, self.model)
        gene_in_model(self.gene2, self.model)

        # Test reactions
        reaction_in_model(self.reaction, self.model)
        reaction_in_model(self.reaction2, self.model, valid=False)

        # Test metabolites
        metabolite_in_model(self.metabolite, self.model)
        metabolite_in_model(self.metabolite2, self.model)

        # Test evidences
        evidence_in_model(self.evidence, self.model)

        # Test model test
        case_in_model(self.testcase, self.model, valid=False)

        # Test references
        reference_in_model(self.reference, self.model)
        reference_in_model(self.reference2, self.model)

        # Test connections
        # Reference <-> Evidence
        reference_in_item(self.reference, self.evidence)
        # Reference2 <-> Testcase
        reference_in_item(self.reference2, self.testcase, valid=False)

        # Gene1 <-> Reaction1
        gene_in_reaction(self.gene, self.reaction)
        gene_in_reaction(self.gene2, self.reaction2, valid=False)

        # Metabolite1 <-> Reaction1
        metabolite_in_reaction(self.metabolite, self.reaction)
        # Check metabolite still in reaction, but reaction not in metabolite
        assert self.metabolite2 in self.reaction2.metabolites
        assert self.reaction2 not in self.metabolite2.reactions

        # Evidence <-> Gene1/Reaction
        item_in_evidence(self.gene, self.evidence)
        item_in_evidence(self.reaction, self.evidence)

    def test_delete_gene1(self):
        # Test gene deletion
        # Check:
        #   - Gene removed from model
        #   - Evidence removed from model

        # Action
        self.model.gem_remove_genes((self.gene,))

        # Test genes
        gene_in_model(self.gene, self.model, valid=False)
        gene_in_model(self.gene2, self.model)

        # Test reactions
        reaction_in_model(self.reaction, self.model)
        reaction_in_model(self.reaction2, self.model)

        # Test metabolites
        metabolite_in_model(self.metabolite, self.model)
        metabolite_in_model(self.metabolite2, self.model)

        # Test model test
        case_in_model(self.testcase, self.model)

        # Test references
        reference_in_model(self.reference, self.model)
        reference_in_model(self.reference2, self.model)

        # Test connections
        # Reference <-> Evidence
        reference_in_item(self.reference, self.evidence, valid=False)
        # Reference2 <-> Testcase
        reference_in_item(self.reference2, self.testcase)

        # Gene1 <-> Reaction1
        gene_in_reaction(self.gene, self.reaction, valid=False)
        gene_in_reaction(self.gene2, self.reaction2)

        # Metabolite1 <-> Reaction1
        metabolite_in_reaction(self.metabolite, self.reaction)
        metabolite_in_reaction(self.metabolite2, self.reaction2)

        # Evidence <-> Gene1/Reaction
        item_in_evidence(self.gene, self.evidence, valid=False)
        item_in_evidence(self.reaction, self.evidence, valid=False)

        # Check evidence is removed when reference deleted
        del self.evidence
        gc.collect()
        assert len(self.model.all_evidences) == 0

    def test_delete_gene2(self):
        # Test removal of gene2
        # Check:
        #   - Gene2 removed from model
        #   - Gene2 removed from reaction2
        #   - Testcase deleted from model
        #   - Reference2 removed from testcase

        # Action
        self.model.gem_remove_genes((self.gene2,))

        # Test genes
        gene_in_model(self.gene, self.model)
        gene_in_model(self.gene2, self.model, valid=False)

        # Test reactions
        reaction_in_model(self.reaction, self.model)
        reaction_in_model(self.reaction2, self.model)

        # Test metabolites
        metabolite_in_model(self.metabolite, self.model)
        metabolite_in_model(self.metabolite2, self.model)

        # Test evidences
        evidence_in_model(self.evidence, self.model)

        # Test model test
        case_in_model(self.testcase, self.model, valid=False)

        # Test references
        reference_in_model(self.reference, self.model)
        reference_in_model(self.reference2, self.model)

        # Test connections
        # Reference <-> Evidence
        reference_in_item(self.reference, self.evidence)
        # Reference2 <-> Testcase
        reference_in_item(self.reference2, self.testcase, valid=False)

        # Gene1 <-> Reaction1
        gene_in_reaction(self.gene, self.reaction)
        gene_in_reaction(self.gene2, self.reaction2, valid=False)

        # Metabolite1 <-> Reaction1
        metabolite_in_reaction(self.metabolite, self.reaction)
        metabolite_in_reaction(self.metabolite2, self.reaction2)

        # Evidence <-> Gene1/Reaction
        item_in_evidence(self.gene, self.evidence)
        item_in_evidence(self.reaction, self.evidence)

    def test_delete_testcase(self):
        # Action
        self.model.gem_remove_tests((self.testcase,))

        # Test genes
        gene_in_model(self.gene, self.model)
        gene_in_model(self.gene2, self.model)

        # Test reactions
        reaction_in_model(self.reaction, self.model)
        reaction_in_model(self.reaction2, self.model)

        # Test metabolites
        metabolite_in_model(self.metabolite, self.model)
        metabolite_in_model(self.metabolite2, self.model)

        # Test evidences
        evidence_in_model(self.evidence, self.model)

        # Test model test
        case_in_model(self.testcase, self.model, valid=False)

        # Test references
        reference_in_model(self.reference, self.model)
        reference_in_model(self.reference2, self.model)

        # Test connections
        # Reference <-> Evidence
        reference_in_item(self.reference, self.evidence)
        # Reference2 <-> Testcase
        reference_in_item(self.reference2, self.testcase, valid=False)

        # Gene1 <-> Reaction1
        gene_in_reaction(self.gene, self.reaction)
        gene_in_reaction(self.gene2, self.reaction2)

        # Metabolite1 <-> Reaction1
        metabolite_in_reaction(self.metabolite, self.reaction)
        metabolite_in_reaction(self.metabolite2, self.reaction2)

        # Evidence <-> Gene1/Reaction
        item_in_evidence(self.gene, self.evidence)
        item_in_evidence(self.reaction, self.evidence)

    def test_delete_referenec(self):
        # Action
        self.model.gem_remove_references((self.reference,))

        # Test genes
        gene_in_model(self.gene, self.model)
        gene_in_model(self.gene2, self.model)

        # Test reactions
        reaction_in_model(self.reaction, self.model)
        reaction_in_model(self.reaction2, self.model)

        # Test metabolites
        metabolite_in_model(self.metabolite, self.model)
        metabolite_in_model(self.metabolite2, self.model)

        # Test evidences
        evidence_in_model(self.evidence, self.model)

        # Test model test
        case_in_model(self.testcase, self.model)

        # Test references
        reference_in_model(self.reference, self.model, valid=False)
        reference_in_model(self.reference2, self.model)

        # Test connections
        # Reference <-> Evidence
        reference_in_item(self.reference, self.evidence, valid=False)
        # Reference2 <-> Testcase
        reference_in_item(self.reference2, self.testcase)

        # Gene1 <-> Reaction1
        gene_in_reaction(self.gene, self.reaction)
        gene_in_reaction(self.gene2, self.reaction2)

        # Metabolite1 <-> Reaction1
        metabolite_in_reaction(self.metabolite, self.reaction)
        metabolite_in_reaction(self.metabolite2, self.reaction2)

        # Evidence <-> Gene1/Reaction
        item_in_evidence(self.gene, self.evidence)
        item_in_evidence(self.reaction, self.evidence)

    def test_delete_reference2(self):
        # Action
        self.model.gem_remove_references((self.reference2,))

        # Test genes
        gene_in_model(self.gene, self.model)
        gene_in_model(self.gene2, self.model)

        # Test reactions
        reaction_in_model(self.reaction, self.model)
        reaction_in_model(self.reaction2, self.model)

        # Test metabolites
        metabolite_in_model(self.metabolite, self.model)
        metabolite_in_model(self.metabolite2, self.model)

        # Test evidences
        evidence_in_model(self.evidence, self.model)

        # Test model test
        case_in_model(self.testcase, self.model)

        # Test references
        reference_in_model(self.reference, self.model)
        reference_in_model(self.reference2, self.model, valid=False)

        # Test connections
        # Reference <-> Evidence
        reference_in_item(self.reference, self.evidence)
        # Reference2 <-> Testcase
        reference_in_item(self.reference2, self.testcase, valid=False)

        # Gene1 <-> Reaction1
        gene_in_reaction(self.gene, self.reaction)
        gene_in_reaction(self.gene2, self.reaction2)

        # Metabolite1 <-> Reaction1
        metabolite_in_reaction(self.metabolite, self.reaction)
        metabolite_in_reaction(self.metabolite2, self.reaction2)

        # Evidence <-> Gene1/Reaction
        item_in_evidence(self.gene, self.evidence)
        item_in_evidence(self.reaction, self.evidence)


class TestCompartment:

    @pytest.fixture(autouse=True)
    def init_objects(self):
        self.compartment1 = Compartment("test_abbrev", "name")
        self.compartment2 = Compartment("test_abbrev", "name")
        self.empty_compartment = Compartment()

    def test__init_(self):
        """ Test that compartment is initialized to None """
        assert self.empty_compartment.id is None
        assert self.empty_compartment.name is None
        assert self.compartment1.id == "test_abbrev"
        assert self.compartment1.name == "name"

    def test_get_values(self):
        """ Test that get values returns a tuple (abbreviation, name) """
        assert self.empty_compartment.get_values() == (None, None)
        assert self.compartment1.get_values() == ("test_abbrev", "name")

    def test__eq__(self):
        """ Test equality function """
        assert self.compartment1 == self.compartment2
        assert self.compartment1 != self.empty_compartment
        assert self.compartment1 is not self.compartment2
        assert ("test_abbrev", "name") == self.compartment1


class TestCleanupDict:

    @pytest.fixture(autouse=True)
    def setup_dict(self):
        self.cleandict = CleaningDict()

    def test_empty_dit(self):
        assert len(self.cleandict) == 0
        assert isinstance(self.cleandict["test"], set)

    def test_addition_deletion(self):
        reaction = Reaction("test")
        subsystem = "subsystem"
        assert len(self.cleandict) == 0

        # Add reaction
        self.cleandict[subsystem].add(reaction)

        # Test addition
        assert len(self.cleandict) == 1
        assert reaction in self.cleandict[subsystem]

        # Remove reaction
        self.cleandict.remove_reaction(subsystem, reaction)
        assert len(self.cleandict) == 0

    def test_removal_with_mutliple_entries(self):
        reaction1 = Reaction("test1")
        reaction2 = Reaction("test2")
        subsystem = "test subsystem"
        self.cleandict[subsystem].add(reaction1)
        self.cleandict[subsystem].add(reaction2)

        # Test addition
        assert len(self.cleandict) == 1
        assert len(self.cleandict[subsystem]) == 2
        assert reaction1 in self.cleandict[subsystem]
        assert reaction2 in self.cleandict[subsystem]

        # Remove reaction1
        self.cleandict.remove_reaction(subsystem, reaction1)
        assert len(self.cleandict) == 1
        assert len(self.cleandict[subsystem]) == 1
        assert reaction2 in self.cleandict[subsystem]

        # Remove reaction2
        self.cleandict.remove_reaction(subsystem, reaction2)
        assert len(self.cleandict) == 0
