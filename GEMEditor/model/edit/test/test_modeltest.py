from unittest.mock import Mock

import pytest
from GEMEditor.base.dialogs import CustomStandardDialog
from GEMEditor.dialogs.mock import MockSelectionDialog
from GEMEditor.model.classes.cobra import Reaction, Model
from GEMEditor.model.classes.modeltest import ModelTest, ReactionSetting, Outcome
from GEMEditor.model.edit.modeltest import EditModelTestDialog
from PyQt5 import QtTest
from PyQt5.QtWidgets import QApplication, QWidget, QDialogButtonBox

# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


@pytest.fixture()
def mock_standarddialog_func(monkeypatch):
    monkeypatch.setattr("GEMEditor.dialogs.standard.CustomStandardDialog.save_dialog_geometry", Mock())
    monkeypatch.setattr("GEMEditor.dialogs.standard.CustomStandardDialog.restore_dialog_geometry", Mock())


class TestEditModelTestDialog:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.parent = QWidget()
        self.dialog = EditModelTestDialog(self.parent)

        self.all_widgets = []

        for i in range(self.dialog.tabWidget.count()):
            self.all_widgets.append(self.dialog.tabWidget.widget(i))

        for i in range(self.dialog.tabWidget2.count()):
            self.all_widgets.append(self.dialog.tabWidget2.widget(i))

        self.all_widgets.append(self.dialog.commentWidget)

    # Todo: Fix tests i.e. make sure the dialog widgets are called
    # def test_set_item_called_in_all_widgets(self):
    #     for widget in self.all_widgets:
    #         widget.set_item = Mock()
    #
    #     test = ModelTest()
    #     model = Model()
    #
    #     self.dialog.set_test(test, model)
    #
    #     for widget in self.all_widgets:
    #         widget.set_item.assert_called_once()

    def test_save_state_called_in_all_widgets(self):

        for widget in self.all_widgets:
            widget.save_state = Mock()

        self.dialog.save_state()

        for widget in self.all_widgets:
            assert widget.save_state.call_count == 1

    def test_description_saved(self):

        test = ModelTest()
        model = Model()

        self.dialog.set_test(test, model)

        assert self.dialog.nameLineEdit.text() == ""

        new_description = "New id"
        QtTest.QTest.keyClicks(self.dialog.nameLineEdit, new_description)

        self.dialog.save_state()

        assert test.description == new_description

    def test_description_loaded(self):

        test = ModelTest(description="Test description")
        model = Model()

        self.dialog.set_test(test, model)

        assert self.dialog.nameLineEdit.text() == test.description


class OldTests:

    def setup_items2(self):
        self.parent = QWidget()
        self.dialog = EditModelTestDialog(parent=self.parent)

        self.reaction1 = Reaction(id="react1")
        self.reaction2 = Reaction(id="react2")
        self.model = Model()

        self.setting1_upper_bound = 1000.5
        self.setting1_lower_bound = 0.5
        self.setting1_objective = 1.5

        self.setting1 = ReactionSetting(self.reaction1,
                                        upper_bound=self.setting1_upper_bound,
                                        lower_bound=self.setting1_lower_bound,
                                        objective_coefficient=self.setting1_objective)
        self.outcome1_value = 100.5
        self.outcome1_operator = "less than"
        self.outcome1 = Outcome(self.reaction2, value=self.outcome1_value, operator=self.outcome1_operator)
        self.test_name = "Test name"
        self.model_test = ModelTest(description=self.test_name)
        self.model_test.add_outcome(self.outcome1)
        self.model_test.add_setting(self.setting1)

    def test_setup(self):
        assert self.dialog.nameLineEdit.text() == ""
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False

    def test_activate_button_name_edit_non_valid_input(self):
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False

        QtTest.QTest.keyClicks(self.dialog.nameLineEdit, "New name")
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False

    def test_activate_button_name_edit_valid_input(self):
        self.dialog.set_test(self.model_test, self.model)
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False

        QtTest.QTest.keyClicks(self.dialog.nameLineEdit, "New name")
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True

    def test_set_test(self):
        self.dialog.set_test(self.model_test, self.model)
        assert self.dialog.model is self.model
        assert self.dialog.model_test is self.model_test

        assert self.dialog.outcomeTable.rowCount() == 1
        assert self.dialog.outcomeTable.item(0, 0).link is self.reaction2
        assert self.dialog.settingsTable.rowCount() == 1
        assert self.dialog.settingsTable.item(0, 0).link is self.reaction1
        assert self.dialog.nameLineEdit.text() == self.model_test.description

    def test_activate_button_condition_addition(self):
        self.dialog.set_test(self.model_test, self.model)
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False

        new_condition = ReactionSetting(self.reaction2, upper_bound=0., lower_bound=0., objective_coefficient=0.)
        self.dialog.settingsTable.update_row_from_item(new_condition)
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True

    def test_activate_button_condition_edit(self):
        self.dialog.set_test(self.model_test, self.model)
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False

        self.dialog.settingsTable.item(0, 1).setData(50., 2)
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True

    def test_activate_button_condition_deletion(self):
        new_condition = ReactionSetting(self.reaction2, upper_bound=0., lower_bound=0., objective_coefficient=0.)
        self.model_test.add_setting(new_condition)
        self.dialog.set_test(self.model_test, self.model)

        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False

        self.dialog.settingsTable.removeRow(1)
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True

    def test_activate_button_outcome_addition(self):
        self.dialog.set_test(self.model_test, self.model)
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False

        new_condition = Outcome(self.reaction1, value=0.1, operator="greater than")
        self.dialog.outcomeTable.update_row_from_item(new_condition)
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True

    def test_activate_button_outcome_edit(self):
        self.dialog.set_test(self.model_test, self.model)
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False

        self.dialog.outcomeTable.item(0, 2).setData(20., 2)
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True

    def test_activate_button_outcome_deletion(self):
        new_condition = Outcome(self.reaction1, value=0.1, operator="greater than")
        self.model_test.add_outcome(new_condition)
        self.dialog.set_test(self.model_test, self.model)
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False
        assert self.dialog.outcomeTable.rowCount() == 2

        self.dialog.outcomeTable.removeRow(1)
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True

    def test_toggle_setting_deletion_button_selection(self):
        self.dialog.set_test(self.model_test, self.model)
        assert self.dialog.button_del_condition.isEnabled() is False

        self.dialog.ConditionView.selectRow(0)
        assert self.dialog.button_del_condition.isEnabled() is True

    def test_toggle_outcome_deletion_button_selection(self):
        self.dialog.set_test(self.model_test, self.model)
        assert self.dialog.button_del_outcome.isEnabled() is False

        self.dialog.OutcomeView.selectRow(0)
        assert self.dialog.OutcomeView.get_selected_rows() == [0]
        assert self.dialog.button_del_outcome.isEnabled() is True

    def test_add_outcome_accepted(self):
        mock_dialog = MockSelectionDialog(return_items=[self.reaction1],
                                          return_value=1)

        assert self.dialog.outcomeTable.rowCount() == 0
        self.dialog.add_outcome(dialog=mock_dialog)
        assert self.dialog.outcomeTable.rowCount() == 1
        assert self.dialog.outcomeTable.item(0, 0).link is self.reaction1
        assert self.dialog.outcomeTable.item(0, 0).text() == self.reaction1.id
        assert self.dialog.outcomeTable.item(0, 1).text() == ""
        assert self.dialog.outcomeTable.item(0, 2).text() == ""

    def test_add_outcome_cancel(self):
        mock_dialog = MockSelectionDialog(return_items=[self.reaction1],
                                          return_value=0)

        assert self.dialog.outcomeTable.rowCount() == 0
        self.dialog.add_outcome(dialog=mock_dialog)
        assert self.dialog.outcomeTable.rowCount() == 0

    def test_add_multiple_ouctomes_accept(self):
        mock_dialog = MockSelectionDialog(return_items=[self.reaction1, self.reaction2],
                                          return_value=1)

        assert self.dialog.outcomeTable.rowCount() == 0
        self.dialog.add_outcome(dialog=mock_dialog)
        assert self.dialog.outcomeTable.rowCount() == 2
        assert self.dialog.outcomeTable.item(0, 0).link is self.reaction1
        assert self.dialog.outcomeTable.item(1, 0).link is self.reaction2

    def test_add_setting_accept(self):
        mock_dialog = MockSelectionDialog(return_items=[self.reaction1],
                                          return_value=1)

        assert self.dialog.settingsTable.rowCount() == 0
        self.dialog.add_setting(dialog=mock_dialog)
        assert self.dialog.settingsTable.rowCount() == 1
        assert self.dialog.settingsTable.item(0, 0).link is self.reaction1
        assert self.dialog.settingsTable.item(0, 0).text() == self.reaction1.id
        assert self.dialog.settingsTable.item(0, 1).data(2) == self.reaction1.lower_bound
        assert self.dialog.settingsTable.item(0, 2).data(2) == self.reaction1.upper_bound
        assert self.dialog.settingsTable.item(0, 3).data(2) == self.reaction1.objective_coefficient

    def test_add_setting_cancel(self):
        mock_dialog = MockSelectionDialog(return_items=[self.reaction1],
                                          return_value=0)

        assert self.dialog.settingsTable.rowCount() == 0
        self.dialog.add_setting(dialog=mock_dialog)
        assert self.dialog.settingsTable.rowCount() == 0

    def test_save_state(self):

        new_test = ModelTest()
        new_name = "test name"
        self.dialog.set_test(new_test, self.model)
        self.dialog.nameLineEdit.setText(new_name)

        self.dialog.settingsTable.update_row_from_item(self.setting1)
        self.dialog.outcomeTable.update_row_from_item(self.outcome1)
        self.dialog.save_state()

        assert new_test.description == new_name
        assert len(new_test.settings) == 1
        assert len(new_test.outcomes) == 1

        new_outcome = new_test.outcomes[0]
        assert new_outcome.value == self.outcome1_value
        assert new_outcome.operator == self.outcome1_operator
        assert new_outcome.reaction == self.reaction2

        new_setting = new_test.settings[0]
        assert new_setting.reaction == self.reaction1
        assert new_setting.lower_bound == self.setting1_lower_bound
        assert new_setting.upper_bound == self.setting1_upper_bound
        assert new_setting.objective_coefficient == self.setting1_objective

    def test_save_state_triggering(self):

        new_test = ModelTest()
        new_name = "test name"
        self.dialog.set_test(new_test, self.model)

        QtTest.QTest.keyClicks(self.dialog.nameLineEdit, new_name)
        self.dialog.accept()
        assert new_test.description == new_name

    @pytest.mark.usefixtures("mock_standarddialog_func")
    def test_save_restore_geometry(self):
        assert issubclass(EditModelTestDialog, CustomStandardDialog)
        assert CustomStandardDialog.restore_dialog_geometry.called is False
        dialog = EditModelTestDialog(self.parent)
        assert CustomStandardDialog.restore_dialog_geometry.called is True
        assert CustomStandardDialog.save_dialog_geometry.called is False
        dialog.reject()
        assert CustomStandardDialog.save_dialog_geometry.called is True
