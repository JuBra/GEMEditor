from GEMEditor.dialogs.results import ResultDialog
from PyQt5 import QtTest, QtCore
from PyQt5.QtWidgets import QApplication
from GEMEditor.cobraClasses import Reaction
from unittest.mock import Mock, call
import sys
import pytest

app = QApplication(sys.argv)


@pytest.fixture()
def monkeypatch_qsettings_complete(monkeypatch):
    monkeypatch.setattr("PyQt5.QtCore.QSettings", Mock())

@pytest.fixture()
def monkeypatch_qsettings_value(monkeypatch):
    monkeypatch.setattr("PyQt5.QtCore.QSettings.value", Mock(return_value="test_return"))

@pytest.fixture()
def monkeypatch_proxymodel_setfilterfixedstring(monkeypatch):
    monkeypatch.setattr("PyQt5.QSortFilterProxyModel.setFilterFixedString", Mock())


class TestResultDialog:

    @pytest.mark.usefixtures("monkeypatch_proxymodel_setfilterfixedstring")
    def test_typing_search_field_changes_filterstring(self):
        """ Check that the filter string entered into the search input is set
        to the filtersortproxy model """
        dialog = ResultDialog()
        QtTest.QTest.keyClicks(dialog.searchInput, "Test")
        dialog.proxyModel.setFilterFixedString.assert_called_with("Test")

    def test_populate_table(self):
        dialog = ResultDialog()
        dialog.add_item_to_table = Mock()

        test_list = [Reaction("id1"), Reaction("id2")]
        test_solution = {"id1": 0.,
                         "id2": 2.}
        dialog.populate_table(test_list, test_solution)
        dialog.add_item_to_table.assert_has_calls([call(test_list[0], 0., row=0),
                                                   call(test_list[1], 2., row=1)])

    @pytest.mark.usefixtures("monkeypatch_qsettings_complete")
    def test_save_header(self):
        """ Test that save header """
        dialog = ResultDialog()
        assert QtCore.QSettings.return_value.setValue.called is False
        dialog.save_header_state()
        assert QtCore.QSettings.return_value.setValue.call_args[0][0] == dialog.__class__.__name__+"DataViewHeader"
        assert QtCore.QSettings.return_value.setValue.call_args[0][1] == dialog.dataView.horizontalHeader().saveState()

    @pytest.mark.usefixtures("monkeypatch_qsettings_value")
    def test_restore_header(self):
        """ Test that save header """
        dialog = ResultDialog()
        dialog.dataView.horizontalHeader = Mock()
        assert QtCore.QSettings.value.called is False
        dialog.restore_header_state()
        QtCore.QSettings.value.assert_called_with(dialog.__class__.__name__+"DataViewHeader")
        dialog.dataView.horizontalHeader.return_value.restoreState.assert_called_with("test_return")

    @pytest.mark.usefixtures("monkeypatch_qsettings_value")
    def test_restore_header(self):
        """ Test that save header """
        dialog = ResultDialog()
        dialog.dataView.horizontalHeader = Mock()
        QtCore.QSettings.value.return_value = None
        assert QtCore.QSettings.value.called is False
        dialog.restore_header_state()
        QtCore.QSettings.value.assert_called_with(dialog.__class__.__name__+"DataViewHeader")
        assert dialog.dataView.horizontalHeader.return_value.restoreState.called is False








