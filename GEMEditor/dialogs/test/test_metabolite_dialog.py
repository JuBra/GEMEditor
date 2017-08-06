import sys
from GEMEditor.dialogs.metabolite import MetaboliteEditDialog
from GEMEditor.cobraClasses import Metabolite, Model
from PyQt5.QtWidgets import QApplication, QDialogButtonBox
from unittest.mock import Mock


app = QApplication(sys.argv)


class TestMetaboliteEditDialog:

    def test_button_disabled_upon_init(self):
        dialog = MetaboliteEditDialog()
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False

    def test_set_item_passed_to_all_children(self):
        dialog = MetaboliteEditDialog()
        metabolite = Metabolite()
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
        dialog = MetaboliteEditDialog()

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

