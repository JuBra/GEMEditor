from GEMEditor.dialogs.mock import MockSelectionDialog, MockModelTestDialog
from GEMEditor.cobraClasses import Reaction, Model
from GEMEditor.data_classes import Outcome, ReactionSetting, ModelTest


class TestMockDialog:

    def test_return_status_code(self):
        dialog = MockSelectionDialog()
        assert dialog.exec_() == 1

    def test_return_modification_status_code(self):
        dialog = MockSelectionDialog(return_value=0)
        assert dialog.exec_() == 0

    def test_return_empty_list(self):
        dialog = MockSelectionDialog()
        assert dialog.selected_items() == []

    def test_return_list_item(self):
        dialog = MockSelectionDialog(return_items=1)
        assert dialog.selected_items() == [1]

    def test_return_input_list(self):
        dialog = MockSelectionDialog(return_items=[1, 2, 3])
        assert dialog.selected_items() == [1, 2, 3]


class TestMockModelTestDialog:

    def test_status_code_accept(self):
        dialog = MockModelTestDialog()
        assert dialog.exec_() == 1

    def test_status_code_cancel(self):
        dialog = MockModelTestDialog(return_value=0)
        assert dialog.exec_() == 0

    def test_setting_of_example_item(self):
        reaction1 = Reaction(id="test_id1")
        reaction2 = Reaction(id="Test_id2")
        description = "Test 123"
        outcome = Outcome(reaction1, 0., "greater than")
        setting = ReactionSetting(reaction2, upper_bound=1000., lower_bound=0., objective_coefficient=0.)

        example_item = ModelTest(description=description)
        example_item.add_outcome(outcome)
        example_item.add_setting(setting)

        model = Model()

        dialog = MockModelTestDialog(example_item=example_item)
        empty_textcase = ModelTest()
        dialog.set_test(empty_textcase, model)

        assert empty_textcase.outcomes == example_item.outcomes
        assert empty_textcase.settings == example_item.settings
        assert empty_textcase.description == example_item.description

