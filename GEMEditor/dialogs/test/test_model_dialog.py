import pytest
from GEMEditor.dialogs.model import AddCompartmentDialog, EditModelDialog
from GEMEditor.cobraClasses import Model, Metabolite
from GEMEditor.widgets.tables import CompartmentTable
from PyQt5 import QtTest, QtCore
from PyQt5.QtWidgets import QApplication, QDialogButtonBox, QToolTip, QWidget, QProgressDialog
from unittest.mock import Mock, MagicMock


# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


def lenmock(n):
    mock = MagicMock()
    mock.__len__.return_value = n
    return mock


class TestAddCompartmentDialog:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.model = Model("Test")
        self.comp1_abbreviation = "c"
        self.comp1_name = "Cytoplasm"
        self.comp2_abbreviation = "e"
        self.comp2_name = "Extracellular"
        self.model.gem_compartments[self.comp1_abbreviation] = self.comp1_name
        self.compartment_table = CompartmentTable()
        self.compartment_table.populate_table(self.model.gem_compartments.items())

        self.wrong_format_abbreviation = "ca"

    @pytest.fixture()
    def patch_tooltip(self, monkeypatch):
        monkeypatch.setattr("PyQt5.QToolTip.showText", Mock())

    def test_setup(self):
        dialog = AddCompartmentDialog(self.compartment_table)

        assert dialog.abbreviationInput.text() == ""
        assert dialog.nameInput.text() == ""
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False

        assert self.compartment_table.findItems(self.comp1_abbreviation, QtCore.Qt.MatchExactly, 0) != []

    def test_setting_new_compartment(self):
        dialog = AddCompartmentDialog(self.compartment_table)

        QtTest.QTest.keyClicks(dialog.abbreviationInput, self.comp2_abbreviation)
        QtTest.QTest.keyClicks(dialog.nameInput, self.comp2_name)

        assert dialog.abbreviationInput.text() == self.comp2_abbreviation
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True
        assert dialog.nameInput.text() == self.comp2_name
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True

    @pytest.mark.usefixtures("patch_tooltip")
    def test_setting_exising_abbreviation(self):
        dialog = AddCompartmentDialog(self.compartment_table)
        assert QToolTip.showText.called is False

        QtTest.QTest.keyClicks(dialog.abbreviationInput, self.comp1_abbreviation)
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False
        assert QToolTip.showText.called is True
        assert dialog.abbreviationInput.toolTip() == dialog.existing_msg.format(self.comp1_abbreviation)

    @pytest.mark.usefixtures("patch_tooltip")
    def test_wrong_format_abbreviation(self):
        dialog = AddCompartmentDialog(self.compartment_table)
        assert QToolTip.showText.called is False

        QtTest.QTest.keyClicks(dialog.abbreviationInput, self.wrong_format_abbreviation)
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False
        assert QToolTip.showText.called is True
        assert dialog.abbreviationInput.toolTip() == dialog.wrong_format_msg

    def test_getting_compartment(self):
        dialog = AddCompartmentDialog(self.compartment_table)
        QtTest.QTest.keyClicks(dialog.abbreviationInput, self.comp2_abbreviation)
        QtTest.QTest.keyClicks(dialog.nameInput, self.comp2_name)

        assert dialog.get_compartment == (self.comp2_abbreviation, self.comp2_name)


class TestEditModelSettings:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.test_id = "Test_id"
        self.test_name = "Test_name"
        self.model = Model(self.test_id, self.test_name)
        self.parent = QWidget()
        self.comp1_name = "Cytoplasm"
        self.comp1_id = "c"
        self.new_comp_id = "n"
        self.new_comp_name = "Nucleus"
        self.model.gem_compartments[self.comp1_id] = self.comp1_name
        self.metabolite = Metabolite("test", compartment=self.comp1_id)
        self.model.add_metabolites([self.metabolite])

        self.dialog = EditModelDialog(parent=self.parent, model=self.model)

    @pytest.fixture()
    def patch_progress(self, monkeypatch):
        monkeypatch.setattr("PyQt5.QProgressDialog", Mock())
        monkeypatch.setattr("PyQt5.QApplication.processEvents", Mock())


    def test_setup(self):
        assert self.model.name == self.test_name
        assert self.model.id == self.test_id
        assert self.comp1_id in self.model.gem_compartments
        assert self.model.gem_compartments[self.comp1_id] == self.comp1_name

        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False
        assert self.dialog.modelNameInput.text() == self.test_name
        assert self.dialog.modelIdInput.text() == self.test_id
        assert self.dialog.compartmentTable.rowCount() == 1

        assert self.metabolite in self.model.metabolites

    def test_change_name(self):
        QtTest.QTest.keyClicks(self.dialog.modelNameInput, "1")
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True
        assert self.dialog.input_changed() is True

    def test_change_id(self):
        QtTest.QTest.keyClicks(self.dialog.modelIdInput, "1")
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True
        assert self.dialog.input_changed() is True

    def test_add_compartment(self):
        row_count = self.dialog.compartmentTable.rowCount()
        self.dialog.compartmentTable.update_row_from_item((self.new_comp_id, self.new_comp_name))
        assert self.dialog.compartmentTable.rowCount() == row_count + 1
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True
        assert self.dialog.input_changed() is True

    def test_compartment_deletion(self):
        assert self.dialog.compartmentTable.rowCount() == 1
        self.dialog.compartmentTableView.selectRow(0)
        QtTest.QTest.mouseClick(self.dialog.deleteCompartmentButton, QtCore.Qt.LeftButton)
        assert self.dialog.compartmentTable.rowCount() == 0

    def test_change_compartment_name(self):
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False
        self.dialog.compartmentTable.item(0, 1).setText(self.new_comp_name)
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True

    def test_save_changes_id(self):
        QtTest.QTest.keyClicks(self.dialog.modelIdInput, self.test_id)
        self.dialog.save_changes()
        assert self.model.id == self.test_id + self.test_id

    def test_save_changes_name(self):
        QtTest.QTest.keyClicks(self.dialog.modelNameInput, self.test_name)
        self.dialog.save_changes()
        assert self.model.name == self.test_name + self.test_name

    def test_save_changes_compartment_addition(self):
        self.dialog.compartmentTable.update_row_from_item((self.new_comp_id, self.new_comp_name))
        assert self.dialog.compartmentTable.rowCount() == 2
        self.dialog.save_changes()
        assert self.model.gem_compartments == {self.comp1_id: self.comp1_name,
                                               self.new_comp_id: self.new_comp_name}
        assert self.metabolite in self.model.metabolites

    @pytest.mark.usefixtures("patch_progress")
    def test_save_changes_compartment_deletion(self):
        self.dialog.compartmentTable.setRowCount(0)
        assert self.metabolite in self.model.metabolites
        assert QProgressDialog.called is False
        assert QApplication.processEvents.called is False
        self.dialog.save_changes()
        assert QProgressDialog.called is True
        assert QApplication.processEvents.called is True
        assert self.model.gem_compartments == {}
        assert self.metabolite not in self.model.metabolites

    def test_save_changed_compartment_name(self):
        self.dialog.compartmentTable.item(0, 1).setText(self.new_comp_name)
        assert self.dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True
        self.dialog.save_changes()
        assert self.model.gem_compartments == {self.comp1_id: self.new_comp_name}

