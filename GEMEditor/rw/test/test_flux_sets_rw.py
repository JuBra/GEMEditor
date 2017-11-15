import pytest
from GEMEditor.model.classes.cobra import Model, Reaction
from GEMEditor.model.classes.modeltest import ModelTest, ReactionSetting, Outcome
from GEMEditor.model.classes.reference import Reference
from GEMEditor.rw import *
from GEMEditor.rw.fluxset import add_tests_to_xml, parse_test_from_xml
from lxml.etree import Element


class TestTestCases:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.model = Model()
        self.testcase = ModelTest(description="test_description")

        self.reaction1 = Reaction(id="r1")
        self.testsetting1 = ReactionSetting(self.reaction1, upper_bound=1000.,
                                            lower_bound=0., objective_coefficient=0.)
        self.testcase.add_setting(self.testsetting1)

        self.reaction3 = Reaction(id="r3")
        self.outcome = Outcome(self.reaction3, value=100., operator="greater")
        self.testcase.add_outcome(self.outcome)

        self.reference = Reference(id="test_refid")
        self.testcase.add_reference(self.reference)

        self.model.add_reactions([self.reaction1, self.reaction3])
        self.model.references[self.reference.id] = self.reference

        self.model.tests.append(self.testcase)
        self.model.setup_tests_table()

        self.root = Element("root", nsmap={None: ge_ns})
        add_tests_to_xml(self.root, self.model)

    def test_setup_items(self):
        assert len(self.root) == 1

    def test_testcase_addition2(self):

        test_list_node = self.root.find(ge_listOfTests)
        assert test_list_node is not None
        assert len(test_list_node) == 1

        test_node = test_list_node.find(ge_testCase)
        assert test_node is not None
        assert test_node.get("description") == "test_description"
        assert len(test_node) == 3

        test_settings_list_node = test_node.find(ge_listOfSettings)
        assert test_settings_list_node is not None
        assert len(test_settings_list_node) == 1

        setting_node = test_settings_list_node.find(ge_reactionSetting)
        assert setting_node is not None
        assert setting_node.get("reactionId") == "R_r1"
        assert setting_node.get("upperBound") == "1000"
        assert setting_node.get("lowerBound") == "0"
        assert setting_node.get("objectiveCoefficient") == "0"

        test_outcomes_list_node = test_node.find(ge_listOfOutcomes)
        assert test_outcomes_list_node is not None
        assert len(test_outcomes_list_node) == 1

        outcome_node = test_outcomes_list_node.find(ge_outcome)
        assert outcome_node is not None
        assert outcome_node.get("reactionId") == "R_r3"
        assert outcome_node.get("value") == "100"
        assert outcome_node.get("operator") == "greater"

        test_references_list_node = test_node.find(ge_listOfReferenceLinks)
        assert test_references_list_node is not None
        assert len(test_references_list_node) == 1

        reference_node = test_references_list_node.find(ge_referenceLink)
        assert reference_node is not None
        assert reference_node.get("id") == "test_refid"

    def test_writing_empty_model(self):

        root = Element("root")
        model = Model()
        add_tests_to_xml(root, model)

        assert len(root) == 0

    def test_read_write_consistency(self):

        self.model.tests.clear()
        assert self.model.tests == []
        parse_test_from_xml(self.root, self.model)

        # Check that a test has been added to the model
        assert len(self.model.tests) == 1
        test = self.model.tests[0]
        assert test.description == "test_description"

        # Check that a setting has been added
        assert len(test.reaction_settings) == 1
        setting = test.reaction_settings[0]
        assert setting.upper_bound == 1000.
        assert setting.lower_bound == 0.
        assert setting.objective_coefficient == 0.
        assert setting.reaction.id == "r1"

        # Check that the outcome has been added
        assert len(test.outcomes) == 1
        outcome = test.outcomes[0]
        assert outcome.reaction.id == "r3"
        assert outcome.value == 100.
        assert outcome.operator == "greater"

        # Check that the reference has been added
        assert len(test.references) == 1
        assert self.reference in test.references

