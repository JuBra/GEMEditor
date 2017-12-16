from collections import OrderedDict
from unittest.mock import Mock

import pytest
from GEMEditor.model.classes.annotation import Annotation
from GEMEditor.model.classes.cobra import Reaction, Metabolite, Gene, Compartment
from GEMEditor.model.classes.evidence import Evidence
from GEMEditor.model.classes.modeltest import ModelTest
from GEMEditor.model.classes.reference import Reference, Author
from GEMEditor.model.display.tables import *
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication

# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestCompartmentTable:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.table = CompartmentTable()

    def test_setup(self):
        # Test header settings
        for i, text in enumerate(self.table.header):
            assert self.table.horizontalHeaderItem(i).text() == text

        assert self.table.rowCount() == 0

    def test_row_from_item(self):
        return_value = self.table.row_from_item(Compartment("c", "cytoplasm"))
        assert return_value[0].text() == "c"
        assert return_value[1].text() == "cytoplasm"

    def test_item_from_row(self):
        self.table.appendRow(self.table.row_from_item(Compartment("c", "cytoplasm")))
        assert self.table.rowCount() == 1
        assert self.table.item_from_row(0) == Compartment("c", "cytoplasm")
        assert self.table.get_items() == [Compartment("c", "cytoplasm")]


class TestReactionTable:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.table = ReactionTable()
        self.test_id = "test_id"
        self.test_name = "test_name"
        self.test_subsystem = "test_subsystemm"
        self.test_ub = 1500.5
        self.test_lb = 500.5
        self.test_obj_coeff = 0.
        self.test_item = Reaction(id=self.test_id,
                                  name=self.test_name,
                                  subsystem=self.test_subsystem,
                                  upper_bound=self.test_ub,
                                  lower_bound=self.test_lb)

    def test_setup(self):
        # Test header settings
        for i, text in enumerate(self.table.header):
            assert self.table.horizontalHeaderItem(i).text() == text

        assert self.table.rowCount() == 0

    def test_row_from_item(self):
        return_values = self.table.row_from_item(self.test_item)

        assert return_values[0].text() == self.test_id
        assert return_values[1].text() == self.test_name
        # Fromula not set
        assert return_values[2].text() == self.test_item.build_reaction_string()
        assert return_values[3].text() == self.test_subsystem
        assert return_values[4].text() == str(self.test_lb)
        assert return_values[5].text() == str(self.test_ub)
        assert float(return_values[6].text()) == self.test_obj_coeff

    def test_update_row_(self):
        assert self.table.rowCount() == 0
        self.table.update_row_from_item(self.test_item)
        assert self.table.rowCount() == 1
        assert self.table.item(0, 0).text() == self.test_id
        assert self.table.item(0, 1).text() == self.test_name
        assert self.table.item(0, 2).text() == self.test_item.build_reaction_string()
        assert self.table.item(0, 3).text() == self.test_subsystem
        assert self.table.item(0, 4).text() == str(self.test_lb)
        assert self.table.item(0, 5).text() == str(self.test_ub)
        assert float(self.table.item(0, 6).text()) == self.test_obj_coeff

    def test_item_from_row(self):
        self.table.update_row_from_item(self.test_item)
        assert self.table.rowCount() == 1
        assert self.table.item_from_row(0) is self.test_item


class TestMetaboliteTable:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.table = MetaboliteTable()

        self.test_id = "Test id"
        self.test_name = "test_name"
        self.test_formula = "H2O"
        self.test_compartment = "test compartment"
        self.test_charge = -2
        self.metabolite = Metabolite(id=self.test_id,
                                     name=self.test_name,
                                     formula=self.test_formula,
                                     compartment=self.test_compartment,
                                     charge=self.test_charge)

    def test_setup(self):
        # Test header settings
        for i, text in enumerate(self.table.header):
            assert self.table.horizontalHeaderItem(i).text() == text

        assert self.table.rowCount() == 0

    def test_row_from_item(self):
        return_value = self.table.row_from_item(self.metabolite)
        for x in return_value:
            assert isinstance(x, LinkedItem)
            assert x.link is self.metabolite

        assert len(return_value) == len(self.table.header)
        assert return_value[0].text() == self.test_id
        assert return_value[1].text() == self.test_name
        assert return_value[2].text() == self.test_formula
        assert return_value[3].text() == str(self.test_charge)
        assert return_value[4].text() == self.test_compartment

    def test_update_row_from_item(self):
        self.table.update_row_from_item(self.metabolite)

        assert self.table.rowCount() == 1
        assert self.table.item(0, 0).text() == self.test_id
        assert self.table.item(0, 1).text() == self.test_name
        assert self.table.item(0, 2).text() == self.test_formula
        assert self.table.item(0, 3).text() == str(self.test_charge)
        assert self.table.item(0, 4).text() == self.test_compartment

    def test_item_from_row(self):
        self.table.update_row_from_item(self.metabolite)
        assert self.table.rowCount() == 1
        assert self.table.item_from_row(0) == self.metabolite


class TestGeneTable:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.table = GeneTable()

        self.test_id = "Test id"
        self.test_name = "test_name"
        self.test_genome = "test_genome"
        self.gene = Gene(id=self.test_id,
                         name=self.test_name,
                         genome=self.test_genome)

    def test_setup(self):
        # Test header settings
        for i, text in enumerate(self.table.header):
            assert self.table.horizontalHeaderItem(i).text() == text

        assert self.table.rowCount() == 0

    def test_row_from_item(self):
        return_value = self.table.row_from_item(self.gene)
        for x in return_value:
            assert isinstance(x, LinkedItem)
            assert x.link is self.gene

        assert len(return_value) == len(self.table.header)
        assert return_value[0].text() == self.test_id
        assert return_value[1].text() == self.test_name
        assert return_value[2].text() == self.test_genome

    def test_update_row_from_item(self):
        self.table.update_row_from_item(self.gene)

        assert self.table.rowCount() == 1
        assert self.table.item(0, 0).text() == self.test_id
        assert self.table.item(0, 1).text() == self.test_name
        assert self.table.item(0, 2).text() == self.test_genome

    def test_item_from_row(self):
        self.table.update_row_from_item(self.gene)
        assert self.table.item_from_row(0) is self.gene


class TestOutcomeTable:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.table = OutcomesTable()

        self.reaction1 = Reaction(id="test_reaction1")
        self.outcome1_value = 1.5
        self.outcome1_operator = "greater than"
        self.outcome1 = Outcome(reaction=self.reaction1,
                                value=self.outcome1_value,
                                operator=self.outcome1_operator)

        self.reaction2 = Reaction(id="test_reaction2")
        self.outcome2_value = 100.5
        self.outcome2_operator = "less than"
        self.outcome2 = Outcome(reaction=self.reaction2,
                                value=self.outcome2_value,
                                operator=self.outcome2_operator)

    def test_setup(self):
        assert self.table.rowCount() == 0

        for i, text in enumerate(self.table.header):
            assert self.table.horizontalHeaderItem(i).text() == text

        assert self.outcome1.reaction is self.reaction1
        assert self.outcome1.value == self.outcome1_value
        assert isinstance(self.outcome1.value, float)
        assert self.outcome1.operator == self.outcome1_operator

        assert self.outcome2.reaction is self.reaction2
        assert self.outcome2.value == self.outcome2_value
        assert isinstance(self.outcome2_value, float)
        assert self.outcome2.operator == self.outcome2_operator

    def test_row_from_item(self):
        return_value = self.table.row_from_item(self.outcome1)

        assert len(return_value) == len(self.table.header)
        assert return_value[0].text() == self.reaction1.id
        assert isinstance(return_value[0], LinkedItem)
        assert return_value[0].link is self.reaction1

        assert return_value[1].text() == self.outcome1_operator
        assert return_value[2].data(2) == self.outcome1_value

    def test_update_row_from_item(self):
        assert self.table.rowCount() == 0
        self.table.update_row_from_item(self.outcome1)
        assert self.table.rowCount() == 1

        assert self.table.item(0).link == self.reaction1
        assert self.table.item(0).text() == self.reaction1.id
        assert self.table.item(0, 1).text() == self.outcome1_operator
        assert self.table.item(0, 2).text() == str(self.outcome1_value)
        assert self.table.item(0, 2).data(2) == self.outcome1_value

    def test_item_from_row(self):
        self.table.update_row_from_item(self.outcome1)
        assert self.table.rowCount() == 1

        test_outcome = self.table.item_from_row(0)
        assert test_outcome.reaction is self.reaction1
        assert test_outcome.value == self.outcome1_value
        assert test_outcome.operator == self.outcome1_operator

    def test_get_items(self):
        self.table.update_row_from_item(self.outcome1)

        items = self.table.get_items()
        assert len(items) == 1
        outcome = items[0]
        assert outcome.reaction is self.reaction1
        assert outcome.value == self.outcome1_value
        assert outcome.operator == self.outcome1_operator
        assert outcome is not self.outcome1

    def test_populate_table(self):
        self.table.populate_table([self.outcome1, self.outcome2])

        assert self.table.rowCount() == 2
        assert self.table.item(0, 0).link is self.reaction1
        assert self.table.item(1, 0).link is self.reaction2


class TestReactionSettingsTable:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.table = ReactionSettingsTable()

        self.reaction1 = Reaction(id="test_reaction1")
        self.setting1_upper_bound = 1000.5
        self.setting1_lower_bound = 0.5
        self.setting1_objective = 1.5
        self.setting1 = ReactionSetting(reaction=self.reaction1,
                                        upper_bound=self.setting1_upper_bound,
                                        lower_bound=self.setting1_lower_bound,
                                        objective_coefficient=self.setting1_objective)

        self.reaction2 = Reaction(id="test_reaction2")
        self.setting2_upper_bound = 0.1
        self.setting2_lower_bound = 0.1
        self.setting2_objective = 0.5
        self.setting2 = ReactionSetting(reaction=self.reaction2,
                                        upper_bound=self.setting2_upper_bound,
                                        lower_bound=self.setting2_lower_bound,
                                        objective_coefficient=self.setting2_objective)

    def test_setup(self):

        assert self.table.rowCount() == 0

        for i, text in enumerate(self.table.header):
            assert self.table.horizontalHeaderItem(i).text() == text

        assert self.setting1.reaction is self.reaction1
        assert self.setting1.lower_bound == self.setting1_lower_bound
        assert isinstance(self.setting1.lower_bound, float)
        assert self.setting1.upper_bound == self.setting1_upper_bound
        assert isinstance(self.setting1.upper_bound, float)
        assert self.setting1.objective_coefficient == self.setting1_objective
        assert isinstance(self.setting1.lower_bound, float)

        assert self.setting2.reaction is self.reaction2
        assert self.setting2.lower_bound == self.setting2_lower_bound
        assert isinstance(self.setting2.lower_bound, float)
        assert self.setting2.upper_bound == self.setting2_upper_bound
        assert isinstance(self.setting2.upper_bound, float)
        assert self.setting2.objective_coefficient == self.setting2_objective
        assert isinstance(self.setting2.lower_bound, float)

    def test_row_from_item(self):
        return_value = self.table.row_from_item(self.setting1)

        assert len(return_value) == len(self.table.header)
        assert return_value[0].text() == self.reaction1.id
        assert isinstance(return_value[0], LinkedItem)
        assert return_value[0].link is self.reaction1

        assert return_value[1].data(2) == self.setting1_lower_bound
        assert return_value[2].data(2) == self.setting1_upper_bound
        assert return_value[3].data(2) == self.setting1_objective

    def test_update_row_from_item(self):
        assert self.table.rowCount() == 0
        self.table.update_row_from_item(self.setting1)
        assert self.table.rowCount() == 1

        assert self.table.item(0).link is self.reaction1
        assert self.table.item(0).text() == self.reaction1.id
        assert self.table.item(0, 1).text() == str(self.setting1_lower_bound)
        assert self.table.item(0, 2).text() == str(self.setting1_upper_bound)
        assert self.table.item(0, 3).text() == str(self.setting1_objective)

    def test_item_from_row(self):
        self.table.update_row_from_item(self.setting1)
        assert self.table.rowCount() == 1

        test_setting = self.table.item_from_row(0)
        assert test_setting.reaction is self.reaction1
        assert test_setting.lower_bound == self.setting1_lower_bound
        assert test_setting.upper_bound == self.setting1_upper_bound
        assert test_setting.objective_coefficient == self.setting1.objective_coefficient

    def test_get_items(self):
        self.table.update_row_from_item(self.setting1)

        items = self.table.get_items()
        assert len(items) == 1
        outcome = items[0]
        assert outcome.reaction is self.reaction1
        assert outcome.upper_bound == self.setting1_upper_bound
        assert outcome.lower_bound == self.setting1_lower_bound
        assert outcome.objective_coefficient is not self.setting1_objective

    def test_get_item_correct_order_bounds(self):
        input = ReactionSetting(self.reaction1, upper_bound=200., lower_bound=400.)
        self.table.update_row_from_item(input)

        setting = self.table.get_items().pop()
        assert setting.reaction == self.reaction1
        assert setting.lower_bound == 200.
        assert setting.upper_bound == 400.

    def test_populate_table(self):
        self.table.populate_table([self.setting1, self.setting2])

        assert self.table.rowCount() == 2
        assert self.table.item(0, 0).link is self.reaction1
        assert self.table.item(1, 0).link is self.reaction2


class TestModelTestsTable:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.table = ModelTestTable()
        self.reaction1 = Reaction("test")
        self.reaction2 = Reaction("test2")
        self.outcome = Outcome(reaction=self.reaction1,
                               value=0.,
                               operator="greater than")
        self.setting = ReactionSetting(reaction=self.reaction2,
                                       upper_bound=1000.,
                                       lower_bound=0.,
                                       objective_coefficient=0.)
        self.model_test = ModelTest(description="test case")
        self.model_test.add_outcome(self.outcome)
        self.model_test.add_setting(self.setting)

    def test_setup(self):
        assert isinstance(self.model_test, ModelTest)
        assert self.setting in self.model_test.reaction_settings
        assert self.outcome in self.model_test.outcomes

    def test_row_from_item(self):
        return_values = self.table.row_from_item(self.model_test)
        assert len(return_values) == len(self.table.header) == 2
        table_item = return_values[0]
        assert table_item.text() == self.model_test.description
        assert table_item.link is self.model_test

    def test_update_row_from_item(self):
        self.table.update_row_from_item(self.model_test)
        assert self.table.rowCount() == 1
        assert self.table.item(0, 0).text() == self.model_test.description
        assert self.table.item(0, 0).link is self.model_test

    def test_item_from_row(self):
        self.table.update_row_from_item(self.model_test)
        assert self.table.rowCount() == 1
        return_item = self.table.item_from_row(0)
        assert return_item is self.model_test


class TestAnnotationTable:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.table = AnnotationTable()
        self.collection = "test collection"
        self.identifier = "test identifier"
        self.type = "is"
        self.annotation = Annotation(collection=self.collection,
                                     identifier=self.identifier,
                                     type=self.type)

    def test_setup(self):
        assert issubclass(AnnotationTable, ElementTable)
        assert len(self.table.header) > 0
        assert self.table.rowCount() == 0
        assert self.annotation.type == self.type
        assert self.annotation.collection == self.collection
        assert self.annotation.identifier == self.identifier

    def test_row_from_item(self):
        return_values = self.table.row_from_item(self.annotation)
        assert len(return_values) == len(self.table.header)
        assert isinstance(return_values[0], LinkedItem)
        assert return_values[0].link is self.annotation
        assert return_values[0].text() == self.collection
        assert isinstance(return_values[1], LinkedItem)
        assert return_values[1].link is self.annotation
        assert return_values[1].text() == self.identifier

    def test_update_row_from_item(self):
        self.table.update_row_from_item(self.annotation)

        assert self.table.rowCount() == 1
        assert self.table.item(0, 0).text() == self.annotation.collection
        assert self.table.item(0, 0).link is self.annotation
        assert self.table.item(0, 1).text() == self.annotation.identifier
        assert self.table.item(0, 1).link is self.annotation

    def test_item_from_row(self):
        self.table.update_row_from_item(self.annotation)
        assert self.table.rowCount() == 1
        assert self.table.item_from_row(0) is self.annotation


class TestAuthorTable:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.table = AuthorTable()

        self.firstname = "test firstname"
        self.lastname = "test lastname"
        self.initials = "test initials"

        self.author = Author(lastname=self.lastname,
                             firstname=self.firstname,
                             initials=self.initials)

    def test_setup(self):
        assert issubclass(AuthorTable, ElementTable)
        assert self.table.rowCount() == 0

        assert self.author.firstname == self.firstname
        assert self.author.lastname == self.lastname
        assert self.author.initials == self.initials

    def test_row_from_item(self):
        return_values = self.table.row_from_item(self.author)
        for x in return_values:
            assert isinstance(x, LinkedItem)
        assert len(return_values) == len(self.table.header)
        assert return_values[0].link is self.author
        assert return_values[0].text() == self.lastname
        assert return_values[1].link is self.author
        assert return_values[1].text() == self.firstname
        assert return_values[2].link is self.author
        assert return_values[2].text() == self.initials

    def test_update_row_from_item(self):
        self.table.update_row_from_item(self.author)

        assert self.table.rowCount() == 1
        assert self.table.item(0, 0).text() == self.lastname
        assert self.table.item(0, 1).text() == self.firstname
        assert self.table.item(0, 2).text() == self.initials

    def test_item_from_row(self):
        self.table.update_row_from_item(self.author)
        assert self.table.rowCount() == 1
        assert self.table.item_from_row(0) is self.author


class TestStoichiometryTable:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.table = StoichiometryTable()

        self.met1_id = "test id"
        self.metabolite1 = Metabolite(id=self.met1_id)
        self.met2_id = "test_id2"
        self.metabolite2 = Metabolite(id=self.met2_id)
        self.met2_coefficient = 1.
        self.met1_coefficient = -1.

        self.stoichiometry = OrderedDict(((self.metabolite1, self.met1_coefficient),
                                         (self.metabolite2, self.met2_coefficient)))

    def test_setup(self):
        assert issubclass(StoichiometryTable, ElementTable)
        assert self.table.rowCount() == 0
        items = list(self.stoichiometry.items())
        assert items[0] == (self.metabolite1, self.met1_coefficient)
        assert items[1] == (self.metabolite2, self.met2_coefficient)

    def test_row_from_item(self):
        return_value = self.table.row_from_item((self.metabolite1, self.met1_coefficient))

        assert len(return_value) == len(self.table.header)
        item1 = return_value[0]
        assert isinstance(item1, LinkedItem)
        assert item1.link is self.metabolite1
        assert item1.text() == self.metabolite1.id
        item2 = return_value[1]
        assert isinstance(item2, LinkedItem)
        assert item2.link is self.metabolite1
        assert item2.data(2) == self.met1_coefficient

    def test_update_row_from_item(self):
        self.table.update_row_from_item((self.metabolite1, self.met1_coefficient))

        assert self.table.rowCount() == 1
        assert self.table.item(0, 0).link is self.metabolite1
        assert self.table.item(0, 0).text() == self.metabolite1.id
        assert self.table.item(0, 1).link is self.metabolite1
        assert self.table.item(0, 1).data(2) == self.met1_coefficient

    def test_table_population(self):
        self.table.populate_table(self.stoichiometry.items())
        assert self.table.rowCount() == 2
        assert self.table.item(0, 0).link is self.metabolite1
        assert self.table.item(0, 0).text() == self.metabolite1.id
        assert self.table.item(1, 0).link is self.metabolite2
        assert self.table.item(1, 0).text() == self.metabolite2.id

        assert self.table.item(0, 1).link is self.metabolite1
        assert self.table.item(0, 1).data(2) == self.met1_coefficient
        assert self.table.item(1, 1).link is self.metabolite2
        assert self.table.item(1, 1).data(2) == self.met2_coefficient

    def test_get_items(self):
        self.table.populate_table(self.stoichiometry.items())
        new_dictionary = self.table.get_items()
        assert new_dictionary == self.stoichiometry

    def test_get_items_empty_table(self):
        assert self.table.get_items() == {}

    def test_get_items_changed_entries(self):
        self.table.update_row_from_item((self.metabolite1, self.met1_coefficient))
        assert self.table.item(0, 0).link is self.metabolite1
        assert self.table.item(0, 1).data(2) == self.met1_coefficient

        new_value = 50.
        self.table.item(0, 1).setData(50., 2)
        assert self.table.item(0, 1).data(2) == new_value
        items = self.table.get_items()
        assert len(items) == 1
        assert list(items.keys())[0] is self.metabolite1
        assert list(items.values())[0] == new_value

    def test_item_from_row(self):
        self.table.populate_table(self.stoichiometry.items())
        assert self.table.item_from_row(0) is self.metabolite1
        assert self.table.item_from_row(1) is self.metabolite2


class TestReferenceTable:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.table = ReferenceTable()

        self.author1 = Author(lastname="FirstLast",
                              firstname="FirstFirst",
                              initials="FirstInitials")

        self.author2 = Author(lastname="SecondLast",
                              firstname="SecondFirst",
                              initials="SecondInitials")

        self.pmid = "123456"
        self.pmc = "PMC12345"
        self.url = "http://www.google.com"
        self.journal = "Test journal"
        self.year = "1987"
        self.title = "Test title"
        self.doi = "Test doi"

        self.reference = Reference(pmid=self.pmid,
                                   pmc=self.pmc,
                                   doi=self.doi,
                                   url=self.url,
                                   year=self.year,
                                   title=self.title,
                                   journal=self.journal,
                                   authors=[self.author1, self.author2])

    def test_setup(self):
        assert issubclass(ReferenceTable, ElementTable)
        assert self.table.rowCount() == 0
        assert self.reference.pmid == self.pmid
        assert self.reference.pmc == self.pmc
        assert self.reference.doi == self.doi
        assert self.reference.url == self.url
        assert self.reference.year == self.year
        assert self.reference.title == self.title
        assert self.reference.journal == self.journal
        assert self.reference.authors[0] is self.author1
        assert self.reference.authors[1] is self.author2

    def test_row_from_item(self):
        return_value = self.table.row_from_item(self.reference)

        assert len(return_value) == len(self.table.header)
        for x in return_value:
            assert isinstance(x, LinkedItem)
            assert x.link is self.reference

        assert return_value[0].text() == self.reference.reference_string()
        assert return_value[1].text() == self.title
        assert return_value[2].text() == self.journal
        assert return_value[3].text() == self.year
        assert return_value[4].text() == self.pmid
        assert return_value[5].text() == self.pmc
        assert return_value[6].text() == self.doi
        assert return_value[7].text() == self.url

    def test_update_row_from_item(self):
        assert self.table.rowCount() == 0
        self.table.update_row_from_item(self.reference)
        assert self.table.rowCount() == 1

        assert self.table.item(0, 0).text() == self.reference.reference_string()
        assert self.table.item(0, 1).text() == self.title
        assert self.table.item(0, 2).text() == self.journal
        assert self.table.item(0, 3).text() == self.year
        assert self.table.item(0, 4).text() == self.pmid
        assert self.table.item(0, 5).text() == self.pmc
        assert self.table.item(0, 6).text() == self.doi
        assert self.table.item(0, 7).text() == self.url

    def test_get_item_from_row(self):
        self.table.update_row_from_item(self.reference)
        assert self.table.item_from_row(0) is self.reference

    def test_get_items(self):
        self.table.update_row_from_item(self.reference)
        assert self.table.get_items() == [self.reference]


class TestElementTable:

    @pytest.fixture(autouse=True)
    def setup_table(self):
        self.item1_text = "test text1"
        self.item1_obj = Metabolite(id=self.item1_text)
        self.item2_text = "test text2"
        self.item2_obj = Metabolite(id=self.item2_text)

        self.expected_items = [LinkedItem(text=self.item1_text,
                                          link=self.item1_obj),
                               LinkedItem(text=self.item2_text,
                                          link=self.item2_obj)]
        self.table = ElementTable()
        self.table.row_from_item = Mock(return_value=self.expected_items)

    def test_setup(self):
        assert self.table.rowCount() == 0

        self.table.row_from_item("test")
        assert self.table.row_from_item.call_count == 1
        assert self.table.row_from_item.call_args[0] == ("test",)

    def test_update_row_from_item(self):
        self.table.update_row_from_item(0)

        assert self.table.rowCount() == 1
        assert self.table.item(0, 0).text() == self.item1_text
        assert self.table.item(0, 0).link == self.item1_obj
        assert self.table.item(0, 1).text() == self.item2_text
        assert self.table.item(0, 1).link == self.item2_obj
        assert self.table.row_from_item.call_count == 1
        assert self.table.row_from_item.call_args[0] == (0,)

    def test_update_row_from_empty_item(self):
        with pytest.raises(TypeError):
            self.table.update_row_from_item()

    @pytest.mark.parametrize("index", [0, 1, 999])
    def test_update_row_with_index(self, index):
        self.table.update_row_from_item(0, row_index=index)
        assert self.table.rowCount() == 1
        assert self.table.item(0, 0).text() == self.item1_text
        assert self.table.item(0, 0).link == self.item1_obj
        assert self.table.item(0, 1).text() == self.item2_text
        assert self.table.item(0, 1).link == self.item2_obj

    def test_update_row_with_specific_index(self):
        self.table.appendRow([LinkedItem(), LinkedItem()])
        self.table.appendRow([LinkedItem(), LinkedItem()])

        assert self.table.rowCount() == 2
        self.table.update_row_from_item(0, 1)
        assert self.table.rowCount() == 2
        assert self.table.item(1, 0).text() == self.item1_text
        assert self.table.item(1, 0).link == self.item1_obj
        assert self.table.item(1, 1).text() == self.item2_text
        assert self.table.item(1, 1).link == self.item2_obj

        assert self.table.item(0, 0).text() == ""
        assert self.table.item(0, 0).link is None
        assert self.table.item(0, 1).text() == ""
        assert self.table.item(0, 1).link is None

    def test_item_from_row(self):
        self.table.update_row_from_item(0)
        assert self.table.rowCount() == 1
        assert self.table.item_from_row(0) is self.item1_obj

    def test_item_from_row_exeeding_rowcount(self):
        self.table.update_row_from_item(0)
        assert self.table.rowCount() == 1
        with pytest.raises(AttributeError):
            assert self.table.item_from_row(500)

    def test_update_row_from_row_data_no_index(self):
        with pytest.raises(TypeError):
            self.table.update_row_from_rowdata(self.expected_items)

    def test_update_row_from_row_data_zero_index(self):
        self.table.update_row_from_rowdata(self.expected_items, 0)
        assert self.table.rowCount() == 1
        assert self.table.item(0, 0).text() == self.item1_text
        assert self.table.item(0, 0).link is self.item1_obj
        assert self.table.item(0, 1).text() == self.item2_text
        assert self.table.item(0, 1).link is self.item2_obj

    def test_update_row_from_row_data_exceeding_index(self):
        assert self.table.rowCount() == 0
        self.table.update_row_from_rowdata(self.expected_items, 1)
        assert self.table.rowCount() == 2

    def test_clear_information(self):
        self.table.update_row_from_item(0)
        assert self.table.rowCount() == 1
        self.table.clear_information()
        assert self.table.rowCount() == 0

    @pytest.fixture()
    def setup_multiple_rows(self):
        for i in range(10):
            self.table.appendRow([LinkedItem(text=str(i), link=i)])

    @pytest.mark.usefixtures("setup_multiple_rows")
    def test_setup_multiple_rows(self):
        assert self.table.rowCount() == 10
        for i in range(self.table.rowCount()):
            assert self.table.item(i).text() == str(i)
            assert self.table.item(i).link == i

    @pytest.mark.usefixtures("setup_multiple_rows")
    def test_delete_rows_first_three(self):
        self.table.delete_rows([2, 1, 0])
        assert self.table.rowCount() == 7
        for i in range(7):
            assert self.table.item(i).text() == str(i+3)
            assert self.table.item(i).link == i+3

    @pytest.mark.usefixtures("setup_multiple_rows")
    def test_delete_rows_last_three(self):
        self.table.delete_rows([9, 7, 8])
        assert self.table.rowCount() == 7
        for i in range(7):
            assert self.table.item(i).text() == str(i)
            assert self.table.item(i).link == i

    @pytest.mark.usefixtures("setup_multiple_rows")
    def test_delete_rows_exceeding_number(self):
        assert self.table.rowCount() == 10
        self.table.delete_rows([11, 200, 500])
        assert self.table.rowCount() == 10

    @pytest.mark.usefixtures("setup_multiple_rows")
    def test_delete_rows_wrong_type(self):
        assert self.table.rowCount() == 10
        with pytest.raises(TypeError):
            self.table.delete_rows([None])

    def test_get_id(self):
        self.table.update_row_from_item(0)
        assert self.table.rowCount() == 1
        assert self.table.get_id(0) == self.item1_text

    def test_get_id_exceeding_index(self):
        with pytest.raises(AttributeError):
            self.table.get_id(100)

    def test_update_row_from_link(self):
        self.table.appendRow([LinkedItem(link="wohoo"),
                              LinkedItem()])
        assert self.table.rowCount() == 1
        self.table.update_row_from_link(0)
        assert self.table.rowCount() == 1
        assert self.table.item(0, 0).text() == self.item1_text
        assert self.table.item(0, 0).link is self.item1_obj
        assert self.table.item(0, 1).text() == self.item2_text
        assert self.table.item(0, 1).link is self.item2_obj
        assert self.table.row_from_item.call_count == 1
        assert self.table.row_from_item.call_args[0] == ("wohoo",)

    def test_update_row_from_link_exceeding_index(self):
        with pytest.raises(AttributeError):
            self.table.update_row_from_link(100)

    @pytest.mark.usefixtures("setup_multiple_rows")
    def test_get_items(self):
        assert self.table.rowCount() == 10
        assert self.table.get_items() == list(range(10))

    def test_get_items_empty_list(self):
        assert self.table.rowCount() == 0
        assert self.table.get_items() == []

    def test_populate_table(self):
        items = ["a", "b", "c"]
        self.table.populate_table(items)
        assert self.table.rowCount() == 3
        assert self.table.row_from_item.call_count == 3
        for i, x in enumerate(self.table.row_from_item.call_args_list):
            args = x[0]
            assert len(args) == 1
            assert args[0] == items[i]

        for i in range(3):
            assert self.table.item(0, 0).text() == self.item1_text
            assert self.table.item(0, 0).link is self.item1_obj
            assert self.table.item(0, 1).text() == self.item2_text
            assert self.table.item(0, 1).link is self.item2_obj

    @pytest.mark.usefixtures("setup_multiple_rows")
    def test_update_row_from_id(self):
        assert self.table.item(2, 0).text() == "2"
        assert self.table.item(2, 0).link == 2
        self.table.update_row_from_id("2", 0)

        assert self.table.item(2, 0).text() == self.item1_text
        assert self.table.item(2, 0).link is self.item1_obj
        assert self.table.row_from_item.call_count == 1
        # [0][0][0] equates to the first item the args of the first call object
        assert self.table.row_from_item.call_args_list[0][0][0] == 2

    @pytest.mark.usefixtures("setup_multiple_rows")
    def test_update_row_from_id_wrong_column(self):
        assert self.table.item(2, 0).text() == "2"
        assert self.table.item(2, 0).link == 2
        self.table.update_row_from_id("2", 1)

        assert self.table.item(2, 0).text() == "2"
        assert self.table.item(2, 0).link == 2

    def test_get_item_to_row_mapping(self):
        self.table.appendRow(self.expected_items)
        additional_item = Metabolite("test")
        self.table.appendRow([LinkedItem("test", additional_item),
                              LinkedItem("None", None)])

        assert self.table.rowCount() == 2
        assert self.table.get_item_to_row_mapping() == {additional_item: 1,
                                                        self.item1_obj: 0}


class TestLinkedItem:

    def test_empty_setup(self):
        item = LinkedItem()
        assert issubclass(LinkedItem, QtGui.QStandardItem)
        assert item.link is None
        assert item.text() == ""

    def test_only_link(self):
        linked_obj = (1, 2, 3)
        item = LinkedItem(link=linked_obj)

        assert item.link is linked_obj
        assert item.text() == ""

    def test_only_text(self):
        text = "Test"
        item = LinkedItem(text=text)

        assert item.link is None
        assert item.text() == text

    def test_both(self):
        linked_obj = (1, 2, 3)
        text = "Test"
        item = LinkedItem(text=text, link=linked_obj)

        assert item.link is linked_obj
        assert item.text() == text


class TestEvidenceTable:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.table = EvidenceTable()

    def test_empty_table(self):
        assert issubclass(EvidenceTable, ElementTable)
        assert self.table.rowCount() == 0

        for i, text in enumerate(self.table.header):
            assert self.table.horizontalHeaderItem(i).text() == text

    def test_row_from_item(self):
        gene1 = Gene("test id1")
        reaction1 = Reaction("react1")
        evidence = Evidence(entity=gene1,
                            target=reaction1,
                            assertion="Catalyze reaction",
                            eco="ECO:001")

        return_values = self.table.row_from_item(evidence)
        assert len(return_values) == len(self.table.header)
        assert isinstance(return_values[0], LinkedItem)
        assert return_values[0].link is evidence
        assert return_values[0].text() == gene1.id
        assert return_values[1].text() == evidence.assertion
        assert return_values[2].text() == evidence.eco
        assert return_values[3].text() == str(evidence.link)
        assert return_values[4].text() == evidence.comment
        assert return_values[5].text() == ""

    def test_get_items(self):
        evidence1 = Evidence(entity=Gene("g1"))
        evidence2 = Evidence(entity=Gene("g2"))
        self.table.update_row_from_item(evidence1)
        self.table.update_row_from_item(evidence2)

        items = self.table.get_items()
        assert len(items) == 2
        assert items[0] is evidence1
        assert items[1] is evidence2


class TestGeneSettingsTable:

    def test_population_of_table(self):
        table = GeneSettingsTable()
        gene = Gene(id="test")
        setting = GeneSetting(gene, True)
        test = ModelTest()
        test.add_setting(setting)

        assert table.rowCount() == 0
        table.populate_table(test.gene_settings)
        assert table.rowCount() == 1
        assert table.item(0, 0).text() == gene.id
        assert table.item(0, 1).text() == "active"

    @pytest.mark.parametrize("activity", [True, False])
    def test_get_items(self, activity):
        table = GeneSettingsTable()
        gene = Gene(id="test")
        setting = GeneSetting(gene, activity)
        test = ModelTest()
        test.add_setting(setting)

        table.populate_table(test.gene_settings)

        new_setting = table.get_items()[0]
        assert setting == new_setting



