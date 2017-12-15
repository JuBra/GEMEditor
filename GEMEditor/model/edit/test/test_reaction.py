from unittest.mock import Mock
from GEMEditor.model.classes.cobra import Reaction, Model
from GEMEditor.model.edit.reaction import EditReactionDialog, SetFluxValueDialog
from PyQt5.QtWidgets import QApplication, QDialogButtonBox
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestReactionInputDialog:

    def test_button_disabled_upon_init(self):
        dialog = EditReactionDialog()
        assert dialog.buttonBox.button(QDialogButtonBox.Save).isEnabled() is False

    def test_set_item_passed_to_all_children(self):
        dialog = EditReactionDialog()
        metabolite = Reaction()
        model = Model()

        dialog.attributeWidget.set_item = Mock()
        for i in range(dialog.tabWidget.count()):
            dialog.tabWidget.widget(i).set_item = Mock()

        # Test pre state
        assert dialog.attributeWidget.set_item.called is False
        for i in range(dialog.tabWidget.count()):
            assert dialog.tabWidget.widget(i).set_item.called is False

        dialog.set_item(metabolite, model)

        # Test post state
        dialog.attributeWidget.set_item.assert_called_once_with(metabolite, model)
        for i in range(dialog.tabWidget.count()):
            dialog.tabWidget.widget(i).set_item.assert_called_once_with(metabolite, model)

    def test_save_state_passed_to_all_children(self):
        dialog = EditReactionDialog()

        dialog.attributeWidget.save_state = Mock()
        for i in range(dialog.tabWidget.count()):
            dialog.tabWidget.widget(i).save_state = Mock()

        # Test pre state
        assert dialog.attributeWidget.save_state.called is False
        for i in range(dialog.tabWidget.count()):
            assert dialog.tabWidget.widget(i).save_state.called is False

        dialog.save_state()

        # Test post state
        assert dialog.attributeWidget.save_state.called is True
        for i in range(dialog.tabWidget.count()):
            assert dialog.tabWidget.widget(i).save_state.called is True


class TestSetFluxValueDialog:

    def test_setup(self):
        dialog = SetFluxValueDialog()
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True
        assert dialog.fluxValueDoubleSpinBox.value() == 0.
        assert dialog.deviationInput.value() == 1
        assert dialog.checkBox.isChecked() is True

    def test_returning_value(self):
        dialog = SetFluxValueDialog()
        value = 5.5
        QTest.keyClicks(dialog.fluxValueDoubleSpinBox, str(value))
        assert dialog.fluxValueDoubleSpinBox.value() == value
        assert dialog.checkBox.isChecked() is True
        assert dialog.deviationInput.value() == 1
        return_value = dialog.user_input
        assert return_value[0] == value
        assert return_value[1] == 1

    def test_deviation_is_zero_if_checkbox_unchecked(self):
        dialog = SetFluxValueDialog()
        assert dialog.checkBox.isChecked() is True
        assert dialog.user_input[1] == 1

        QTest.mouseClick(dialog.checkBox, Qt.LeftButton)

        assert dialog.checkBox.isChecked() is False
        assert dialog.user_input[1] == 0

    def test_changing_deviation(self):
        dialog = SetFluxValueDialog()
        assert dialog.checkBox.isChecked() is True
        assert dialog.user_input[1] == 1

        dialog.deviationInput.clear()
        value = 5
        QTest.keyClicks(dialog.deviationInput, str(value))
        assert dialog.user_input[1] == value
        assert dialog.checkBox.isChecked() is True
