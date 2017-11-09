from GEMEditor.dialogs.mock import MockSelectionDialog

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


