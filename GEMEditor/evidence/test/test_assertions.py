import pytest
from GEMEditor.model.classes.cobra import Reaction, Gene, Metabolite, Compartment
from GEMEditor.model.classes.evidence import Evidence


class TestAssertionCatalyzingReaction:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.reaction = Reaction("r1")
        self.gene = Gene("g1")
        self.evidence = Evidence(entity=self.gene, target=self.reaction, assertion="Catalyzing reaction")

    def test_valid_if_gene_in_reaction(self):
        self.reaction.add_child(self.gene)

        assert self.evidence.is_valid() is True

    def test_invalid_if_gene_not_in_reaction(self):
        assert self.evidence.is_valid() is False

    def test_gene_needed(self):
        evidence = Evidence(entity=self.gene, assertion="Catalyzing reaction")
        assert evidence.is_valid() is None

    def test_reaction_needed(self):
        evidence = Evidence(target=self.reaction, assertion="Catalyzing reaction")
        assert evidence.is_valid() is None

    def test_fix_gene_added(self):
        assert self.gene not in self.reaction.genes

        status = self.evidence.fix()

        assert status is True
        assert self.gene in self.reaction.genes


class TestAssertionNotCatalyzingReaction:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.reaction = Reaction("r1")
        self.gene = Gene("g1")
        self.evidence = Evidence(entity=self.gene, target=self.reaction, assertion="Not catalyzing reaction")

    def test_invalid_if_gene_in_reaction(self):
        self.reaction.add_child(self.gene)
        assert self.evidence.is_valid() is False

    def test_valid_if_gene_not_in_reaction(self):
        assert self.evidence.is_valid() is True

    def test_gene_needed(self):
        evidence = Evidence(entity=self.gene, assertion="Not catalyzing reaction")
        assert evidence.is_valid() is None

    def test_reaction_needed(self):
        evidence = Evidence(target=self.reaction, assertion="Not catalyzing reaction")
        assert evidence.is_valid() is None

    def test_fix_remove_gene_from_reaction(self):
        self.reaction.add_child(self.gene)

        assert self.evidence.is_valid() is False

        status = self.evidence.fix()
        assert status is True
        assert self.gene not in self.reaction.genes


class TestAssertionReversible:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.reaction = Reaction("r1")
        self.evidence = Evidence(entity=self.reaction, assertion="Reversible")

    def test_valid_if_reaction_reversible(self):
        self.reaction.lower_bound = -1000.
        self.reaction.upper_bound = 1000.

        assert self.evidence.is_valid() is True

    def test_not_valid_if_irreversible(self):
        self.reaction.lower_bound = 0.
        self.reaction.upper_bound = 1000.

        assert self.evidence.is_valid() is False

        self.reaction.lower_bound = -1000.
        self.reaction.upper_bound = 0.

        assert self.evidence.is_valid() is False

    def test_reaction_needed(self):
        evidence = Evidence(assertion="Reversible")

        assert evidence.is_valid() is None

    def test_fix_reaction(self):
        self.reaction.lower_bound = 0.
        self.reaction.upper_bound = 0.

        status = self.evidence.fix()

        assert status is True
        assert self.reaction.lower_bound == -1000.
        assert self.reaction.upper_bound == 1000.


class TestAssertionIrreversible:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.reaction = Reaction("r1")
        self.evidence = Evidence(entity=self.reaction, assertion="Irreversible")

    def test_not_valid_if_reaction_reversible(self):
        self.reaction.lower_bound = -1000.
        self.reaction.upper_bound = 1000.

        assert self.evidence.is_valid() is False

    def test_valid_if_irreversible(self):
        self.reaction.lower_bound = 0.
        self.reaction.upper_bound = 1000.

        assert self.evidence.is_valid() is True

        self.reaction.lower_bound = -1000.
        self.reaction.upper_bound = 0.

        assert self.evidence.is_valid() is True

    def test_reaction_needed(self):
        evidence = Evidence(assertion="Irreversible")

        assert evidence.is_valid() is None

    def test_fix_reaction(self):
        self.reaction.lower_bound = -1000.
        self.reaction.upper_bound = 1000.

        status = self.evidence.fix()

        assert status is True
        assert self.reaction.lower_bound == 0.
        assert self.reaction.upper_bound == 1000.

    def test_fix_nonstandard_boundary_kept(self):
        self.reaction.lower_bound = -1000.
        self.reaction.upper_bound = 500.

        status = self.evidence.fix()

        assert status is True
        assert self.reaction.lower_bound == 0.
        assert self.reaction.upper_bound == 500.


class TestAssertionPresent:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.reaction = Reaction("r1")
        self.evidence = Evidence(entity=self.reaction, assertion="Present")

    def test_valid_if_reaction_is_active(self):
        self.reaction.lower_bound = -1000.
        self.reaction.upper_bound = 0.

        assert self.evidence.is_valid() is True

        self.reaction.upper_bound = 1000.

        assert self.evidence.is_valid() is True

        self.reaction.lower_bound = 0.

        assert self.evidence.is_valid() is True

    def test_invalid_if_reaction_not_active(self):
        self.reaction.lower_bound = 0.
        self.reaction.upper_bound = 0.

        assert self.evidence.is_valid() is False

    def test_valid_if_metabolite_entity(self):
        self.evidence.set_entity(Metabolite("m1"))

        assert self.evidence.is_valid() is True

    def test_entity_needed(self):
        evidence = Evidence()

        assert evidence.is_valid() is None

    def test_fixing_not_implemented(self):
        self.reaction.lower_bound = 0
        self.reaction.upper_bound = 0
        self.evidence.fix()
        assert self.reaction.lower_bound == 0.
        assert self.reaction.upper_bound == 0.


class TestAssertionAbsent:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.reaction = Reaction("r1")
        self.evidence = Evidence(entity=self.reaction, assertion="Absent")

    def test_invalid_if_reaction_is_active(self):
        self.reaction.lower_bound = -1000.
        self.reaction.upper_bound = 0.

        assert self.evidence.is_valid() is False

        self.reaction.upper_bound = 1000.

        assert self.evidence.is_valid() is False

        self.reaction.lower_bound = 0.

        assert self.evidence.is_valid() is False

    def test_valid_if_reaction_not_active(self):
        self.reaction.lower_bound = 0.
        self.reaction.upper_bound = 0.

        assert self.evidence.is_valid() is True

    def test_invalid_if_metabolite_entity(self):
        self.evidence.set_entity(Metabolite("m1"))

        assert self.evidence.is_valid() is False

    def test_entity_needed(self):
        evidence = Evidence()

        assert evidence.is_valid() is None

    def test_fixing_not_implemented(self):
        self.reaction.lower_bound = -1000
        self.reaction.upper_bound = 1000
        result = self.evidence.fix()
        assert result is False
        assert self.reaction.lower_bound == -1000.
        assert self.reaction.upper_bound == 1000.


class TestAssertionLocalization:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.gene = Gene("g1")
        self.compartment = Compartment("c")
        self.metabolite1 = Metabolite("m1")
        self.metabolite2 = Metabolite("m2")
        self.reaction = Reaction("r1")
        self.reaction.add_metabolites({self.metabolite1: -1,
                                       self.metabolite2: 1})
        self.reaction.add_child(self.gene)

        self.evidence = Evidence(entity=self.gene, assertion="Localization",
                                 target=self.compartment)

    def test_valid_if_metabolites_in_same_compartment_as_gene(self):
        self.metabolite1.compartment = "c"
        self.metabolite2.compartment = "c"
        self.compartment.id = "c"

        assert self.evidence.is_valid() is True

    def test_invalid_if_metabolites_not_in_same_compartment(self):
        self.metabolite1.compartment = "e"
        self.metabolite2.compartment = "e"
        self.compartment.id = "c"

        assert self.evidence.is_valid() is False

    def test_invalid_if_any_reaction_not_in_same_compartment(self):
        self.metabolite1.compartment = "c"
        self.metabolite2.compartment = "c"
        self.compartment.id = "c"

        assert self.evidence.is_valid() is True

        met1 = Metabolite("m1")
        met2 = Metabolite("m2")
        react2 = Reaction("r2")
        react2.add_metabolites({met1: -1, met2: 1})
        react2.add_child(self.gene)

        assert self.evidence.is_valid() is False

    def test_error_if_gene_not_added_to_reaction(self):
        gene = Gene("g1")
        evidence = Evidence(entity=gene, assertion="Localization")

        assert evidence.is_valid() is None

    def test_entity_needed(self):
        evidence = Evidence(assertion="Localization")

        assert evidence.is_valid() is None

        evidence.set_entity(self.gene)

        assert evidence.is_valid() is None

        evidence.set_target(self.compartment)

        assert evidence.is_valid() is not None