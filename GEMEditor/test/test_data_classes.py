import pytest
from unittest.mock import Mock, patch, PropertyMock, call
from GEMEditor.data_classes import Annotation, Reference, Author, ModelTest, Outcome, ReactionSetting, \
    CleaningDict, ModelStats, GeneSetting
from GEMEditor.cobraClasses import Reaction, Gene, Compartment


class TestAnnotation:

    @pytest.fixture(autouse=True)
    def init_objects(self):
        self.annotation1 = Annotation("test_collection", "test_id")
        self.annotation2 = Annotation("test_collection", "test_id")
        self.empty_annotation = Annotation()

    def test_init_(self):
        """ Test that collection and identifier is initialized to None """
        assert self.empty_annotation.collection is None
        assert self.empty_annotation.identifier is None
        assert self.empty_annotation.type == "is"
        assert self.annotation1.collection == "test_collection"
        assert self.annotation1.identifier == "test_id"
        assert self.annotation1.type == "is"

    def test__hash_(self):
        """ Test that annotations containing the same information
        return the same value by __hash__()"""

        assert self.annotation1 is not self.annotation2
        assert self.annotation1.__hash__() == self.annotation2.__hash__()
        assert self.annotation1.__hash__() != self.empty_annotation.__hash__()

    def test_annotation_eq1(self):
        """ Test equality of annotations """
        assert self.annotation1 == self.annotation2
        assert self.annotation1 is not self.annotation2

    def test_annotation_eq2(self):
        """ Test not equality if type is different """

        assert Annotation("a", "a", "is") != Annotation("a", "a", "has")
        assert Annotation("a", "a", "is").__hash__() != Annotation("a", "a", "has").__hash__()

    def test_annotation_ex2(self):
        """ Test class is checked for in annotation equality """

        class Mock:
            def __init__(self, collection=None, identifier=None, type="is"):
                self.collection = collection
                self.identifier = identifier
                self.type = type

        mock = Mock("test_collection", "test_id")
        assert self.annotation1 != mock
        assert self.annotation1.collection == mock.collection
        assert self.annotation1.identifier == mock.identifier

    def test_prevent_setting_of_variables(self):
        """ Test that collection and identifier cannot be set
         in order to assure hash stability """
        with pytest.raises(AttributeError):
            self.annotation1.collection = "test"
        with pytest.raises(AttributeError):
            self.annotation1.identifier = "bla"


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


class TestReference:

    @pytest.fixture(autouse=True)
    def init_objects(self):
        self.reference1 = Reference("test_abbrev", "name")
        self.reference2 = Reference("test_abbrev", "name")
        self.empty_reference = Reference()

    def test___init__(self):
        """ Test the default values of empty reference """
        assert self.empty_reference.authors == []
        assert self.empty_reference.pmid == ""
        assert self.empty_reference.pmc == ""
        assert self.empty_reference.abstract == ""
        assert self.empty_reference.doi == ""
        assert self.empty_reference.title == ""
        assert self.empty_reference.year == ""
        assert self.empty_reference.url == ""
        assert self.empty_reference.journal == ""

    def test_author_string1(self):
        """ Check that empty string is returned if no author is set """
        assert self.empty_reference.reference_string() == ""

    def test_author_string2(self):
        """ Test correct string for single author """
        self.empty_reference.authors = [Author("Family", "First", "Initials")]
        self.empty_reference.year = "2015"
        assert self.empty_reference.reference_string() == "Family Initials, 2015"

    def test_author_string3(self):
        """ Test correct string for two authors """
        self.empty_reference.authors = [Author("FamilyFirst", "", "InitialsFirst"),
                                        Author("FamilySecond", "", "InitialsSecond")]

        self.empty_reference.year = "2015"
        expected = "FamilyFirst InitialsFirst and FamilySecond InitialsSecond, 2015"
        assert self.empty_reference.reference_string() == expected

    def test_author_string4(self):
        """ Test correct string for 3 authors """
        self.empty_reference.authors = [Author("Family1", "", "Initials1"),
                                        Author("Family2", "", "Initials2"),
                                        Author("Family3", "", "Initials3")]
        self.empty_reference.year = "2015"
        expected = "Family1 Initials1 et al., 2015"
        assert self.empty_reference.reference_string() == expected

    def test_annotation_property(self):
        reference = Reference()
        reference.pmc = "1234"
        reference.pmid = "54321"
        reference.doi = "5555"

        assert Annotation("pubmed", reference.pmid) in reference.annotation
        assert Annotation("pmc", reference.pmc) in reference.annotation
        assert Annotation("doi", reference.doi) in reference.annotation


class TestAuthor:

    def test_setup(self):
        author = Author("lastname", "firstname", "initials")
        assert author.lastname == "lastname"
        assert author.firstname == "firstname"
        assert author.initials == "initials"
        assert Author() == ("", "", "")

    def test_author_str(self):
        """ Check author_str property returns the proper value"""
        assert Author(lastname="Last", initials="P", firstname="").display_str == "Last P"
        assert Author("Last", "", "").display_str == "Last"


class TestModelTest:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.test = ModelTest()
        self.outcome1 = Outcome()
        self.reaction_setting = ReactionSetting()
        self.gene_setting = GeneSetting()
        self.reference1 = Reference()

    def test_setup(self):
        assert self.test.description == ""
        assert self.test.outcomes == []
        assert self.test.reaction_settings == []
        assert self.test.gene_settings == []
        assert len(self.test.references) == 0

    def test_add_outcomes(self):
        self.test.add_outcome(self.outcome1)
        assert self.outcome1 in self.test.outcomes

    def test_add_reaction_setting(self):
        self.test.add_setting(self.reaction_setting)
        assert self.reaction_setting in self.test.reaction_settings

    def test_add_gene_setting(self):
        self.test.add_setting(self.gene_setting)
        assert self.gene_setting in self.test.gene_settings

    def test_add_reference(self):
        self.test.add_reference(self.reference1)
        assert self.reference1 in self.test.references

    def test_clear_all(self):
        self.test.add_outcome(self.outcome1)
        self.test.add_reference(self.reference1)
        self.test.add_setting(self.reaction_setting)

        self.test.clear_all()
        assert len(self.test.outcomes) == 0
        assert len(self.test.gene_settings) == 0
        assert len(self.test.reaction_settings) == 0
        assert len(self.test.references) == 0


class TestOutcomes:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.outcome = Outcome()
        self.solution = Mock()

    def test_setup(self):
        assert self.outcome.reaction is None
        assert self.outcome.value is None
        assert self.outcome.operator is None

    def test_check_solution(self):
        reaction_id = "test_id"
        reaction = Reaction(reaction_id)
        self.solution.x_dict = {reaction_id: 5.}

        new_outcome = Outcome(reaction,
                              value=0.,
                              operator="greater than")
        assert new_outcome.check_solution(self.solution) is True
        self.solution.x_dict = {reaction_id: 0.}
        assert new_outcome.check_solution(self.solution) is False

        new_outcome.operator = "less than"
        assert new_outcome.check_solution(self.solution) is False
        new_outcome.value = 10.
        assert new_outcome.check_solution(self.solution) is True

        new_outcome.operator = ""
        assert new_outcome.check_solution(self.solution) is False

    def test_empty_outcome_is_not_valid(self):
        assert self.outcome.is_valid() is False

    def test_no_operator_set_is_invalid(self):
        self.outcome.reaction = Reaction()
        self.outcome.value = 0.

        assert self.outcome.operator is None
        assert self.outcome.is_valid() is False

    @pytest.mark.parametrize("parameters", [(Reaction(), 0., "greater than", True),
                                            (None, 0., "greater than", False),
                                            (Reaction(), None, "greater than", False),
                                            (Reaction(), 0., None, False),
                                            (None, None, None, False)])
    def test_outcome_is_valid(self, parameters):
        outcome = Outcome(reaction=parameters[0],
                          value=parameters[1],
                          operator=parameters[2])

        assert outcome.is_valid() is parameters[3]


class TestSetting:

    def test_set_parameters(self):
        old_lb = -1000.
        old_ub = 1000.
        old_obj_value = 1.

        with patch('GEMEditor.cobraClasses.Reaction.objective_coefficient', new_callable=PropertyMock) as objective_coefficient:
            objective_coefficient.return_value = old_obj_value
            reaction = Reaction("test_id",
                                lower_bound=old_lb,
                                upper_bound=old_ub)

            new_lb = -500.
            new_ub = 500.
            new_obj_value = 0.
            setting = ReactionSetting(reaction, upper_bound=new_ub, lower_bound=new_lb, objective_coefficient=new_obj_value)

            assert reaction.upper_bound == old_ub
            assert reaction.lower_bound == old_lb
            assert reaction.objective_coefficient == old_obj_value

            setting.do()

            assert reaction.upper_bound == new_ub
            assert reaction.lower_bound == new_lb
            assert objective_coefficient.call_args == call(new_obj_value)
            objective_coefficient.return_value = new_obj_value

            setting.undo()
            assert reaction.upper_bound == old_ub
            assert reaction.lower_bound == old_lb
            assert objective_coefficient.call_args == call(old_obj_value)
            objective_coefficient.return_value = old_obj_value

            # Check that calling undo a second time does not change the value
            prior_call_count = objective_coefficient.call_count
            setting.undo()
            assert reaction.upper_bound == old_ub
            assert reaction.lower_bound == old_lb
            assert objective_coefficient.call_count == prior_call_count


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


class TestModelStats:

    def test_setup(self):
        modelstats = ModelStats()

        assert modelstats.reactions_total == 0
        assert modelstats.metabolites_total == 0
        assert modelstats.genes_total == 0

        assert modelstats.reactions_unique == 0
        assert modelstats.reactions_wo_genes == 0
        assert modelstats.reactions_annotated == 0
        assert modelstats.reactions_boundary == 0
        assert modelstats.reactions_transport == 0
        assert modelstats.reactions_unbalanced == 0

        assert modelstats.metabolites_annotated == 0
        assert modelstats.metabolites_unique == 0

        assert modelstats.genes_annotated == 0
        assert modelstats.genes_assigned == 0

    @pytest.mark.parametrize("total, unannotated, expected", [(1000, 100, 900), (100, 200, -100)])
    def test_reactions_annotated(self, total, unannotated, expected):
        modelstats = ModelStats()

        modelstats.reactions_total = total
        modelstats.list_unannotated_reactions[:] = list(range(unannotated))
        assert modelstats.reactions_annotated == expected

    @pytest.mark.parametrize("total, unannotated, expected", [(1000, 100, 900), (100, 200, -100)])
    def test_metabolites_annotated(self, total, unannotated, expected):
        modelstats = ModelStats()

        modelstats.metabolites_total = total
        modelstats.list_unannotated_metabolites[:] = list(range(unannotated))
        assert modelstats.metabolites_annotated == expected

    @pytest.mark.parametrize("total, unannotated, expected", [(1000, 100, 900), (100, 200, -100)])
    def test_genes_annotated(self, total, unannotated, expected):
        modelstats = ModelStats()

        modelstats.genes_total = total
        modelstats.list_unannotated_genes[:] = list(range(unannotated))
        assert modelstats.genes_annotated == expected

    @pytest.mark.parametrize("total, unassigned, expected", [(1000, 100, 900), (100, 200, -100)])
    def test_genes_assigned(self, total, unassigned, expected):
        modelstats = ModelStats()

        modelstats.genes_total = total
        modelstats.list_unassigned_genes[:] = list(range(unassigned))
        assert modelstats.genes_assigned == expected


class TestGeneCondition:

    def test_setting_resetting_boundaries(self):
        gene = Gene()
        reaction = Reaction(lower_bound=-1000., upper_bound=1000.)
        reaction.add_child(gene)
        gene.functional = True

        condition = GeneSetting(gene, False)

        assert gene.functional is True
        assert reaction.upper_bound == 1000.
        assert reaction.lower_bound == -1000.

        condition.do()

        assert gene.functional is False
        assert reaction.upper_bound == 0.
        assert reaction.lower_bound == 0.

        condition.undo()

        assert gene.functional is True
        assert reaction.upper_bound == 1000.
        assert reaction.lower_bound == -1000.

        # Check that calling undo second time does not change value
        condition.undo()

        assert gene.functional is True
        assert reaction.upper_bound == 1000.
        assert reaction.lower_bound == -1000.