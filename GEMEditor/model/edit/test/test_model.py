from unittest.mock import Mock, MagicMock

import pytest
from GEMEditor.model.classes.cobra import Model, Metabolite, Compartment
from GEMEditor.model.display.tables import CompartmentTable
from GEMEditor.model.edit.model import AddCompartmentDialog, EditModelDialog
from PyQt5 import QtTest, QtCore
from PyQt5.QtWidgets import QApplication, QDialogButtonBox, QToolTip, QWidget

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
        self.c1 = Compartment(id="c", name="Cytoplasm")
        self.c2 = Compartment(id="e", name="Extracellular")
        self.model.gem_compartments[self.c1.id] = self.c1
        self.compartment_table = CompartmentTable()
        self.compartment_table.populate_table(self.model.gem_compartments.values())
        self.wrong_format_abbreviation = "ca"

    @pytest.fixture()
    def patch_tooltip(self, monkeypatch):
        monkeypatch.setattr("PyQt5.QtWidgets.QToolTip.showText", Mock())

    def test_setup(self):
        dialog = AddCompartmentDialog(self.compartment_table)

        assert dialog.input_id.text() == ""
        assert dialog.input_name.text() == ""
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False

        assert self.compartment_table.findItems(self.c1.id, QtCore.Qt.MatchExactly, 0) != []

    def test_setting_new_compartment(self):
        dialog = AddCompartmentDialog(self.compartment_table)

        QtTest.QTest.keyClicks(dialog.input_id, self.c2.id)
        QtTest.QTest.keyClicks(dialog.input_name, self.c2.name)

        assert dialog.input_id.text() == self.c2.id
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True
        assert dialog.input_name.text() == self.c2.name
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is True

    @pytest.mark.usefixtures("patch_tooltip")
    def test_setting_exising_abbreviation(self):
        dialog = AddCompartmentDialog(self.compartment_table)
        assert QToolTip.showText.called is False

        QtTest.QTest.keyClicks(dialog.input_id, self.c1.id)
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False
        assert QToolTip.showText.called is True
        assert dialog.input_id.toolTip() == dialog.existing_msg.format(self.c1.id)

    @pytest.mark.usefixtures("patch_tooltip")
    def test_wrong_format_abbreviation(self):
        dialog = AddCompartmentDialog(self.compartment_table)
        assert QToolTip.showText.called is False

        QtTest.QTest.keyClicks(dialog.input_id, self.wrong_format_abbreviation)
        assert dialog.buttonBox.button(QDialogButtonBox.Ok).isEnabled() is False
        assert QToolTip.showText.called is True
        assert dialog.input_id.toolTip() == dialog.wrong_format_msg

    def test_getting_compartment(self):
        dialog = AddCompartmentDialog(self.compartment_table)
        QtTest.QTest.keyClicks(dialog.input_id, self.c2.id)
        QtTest.QTest.keyClicks(dialog.input_name, self.c2.name)

        assert dialog.get_compartment == Compartment(self.c2.id, self.c2.name)


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
        self.new_comp = Compartment(self.new_comp_id, self.new_comp_name)
        self.comp1 = Compartment(self.comp1_id, self.comp1_name)
        self.model.gem_compartments[self.comp1_id] = self.comp1
        self.metabolite = Metabolite("test", compartment=self.comp1_id)
        self.model.add_metabolites([self.metabolite])
        self.model.setup_tables()
        self.dialog = EditModelDialog(model=self.model)

    @pytest.fixture()
    def patch_progress(self, monkeypatch):
        monkeypatch.setattr("PyQt5.QtWidgets.QProgressDialog", Mock())
        monkeypatch.setattr("PyQt5.QtWidgets.QApplication.processEvents", Mock())

    def test_setup(self):
        assert self.model.name == self.test_name
        assert self.model.id == self.test_id
        assert self.comp1_id in self.model.gem_compartments
        assert self.model.gem_compartments[self.comp1_id] == self.comp1

        assert self.dialog.buttonBox.button(QDialogButtonBox.Save).isEnabled() is False
        assert self.dialog.input_name.text() == self.test_name
        assert self.dialog.input_id.text() == self.test_id
        assert self.dialog.compartmentTable.rowCount() == 1

        assert self.metabolite in self.model.metabolites

    def test_change_in_id_enables_button(self):
        model = Model()
        model.gem_compartments["c"] = Compartment("c", "Cytoplasm")
        dialog = EditModelDialog(model=model)
        save_button = dialog.buttonBox.button(QDialogButtonBox.Save)

        # Change id
        assert save_button.isEnabled() is False
        QtTest.QTest.keyClick(dialog.input_id, "M")
        assert save_button.isEnabled() is True

        # Undo change
        QtTest.QTest.keyClick(dialog.input_id, QtCore.Qt.Key_Backspace)
        assert save_button.isEnabled() is False

    def test_change_in_name_enables_button(self):
        model = Model()
        model.gem_compartments["c"] = Compartment("c", "Cytoplasm")
        dialog = EditModelDialog(model=model)
        save_button = dialog.buttonBox.button(QDialogButtonBox.Save)

        # Change id
        assert save_button.isEnabled() is False
        QtTest.QTest.keyClicks(dialog.input_name, "M")
        assert save_button.isEnabled() is True

        # Undo change
        QtTest.QTest.keyClick(dialog.input_name, QtCore.Qt.Key_Backspace)
        assert save_button.isEnabled() is False

    def test_add_compartment(self):
        row_count = self.dialog.compartmentTable.rowCount()
        self.dialog._add_new_compartment_to_table(self.new_comp)
        assert self.dialog.compartmentTable.rowCount() == row_count + 1
        assert self.dialog.buttonBox.button(QDialogButtonBox.Save).isEnabled() is True
        assert self.dialog.input_changed() is True

    def test_compartment_deletion(self):
        assert self.dialog.compartmentTable.rowCount() == 1
        self.dialog.compartmentTableView.selectRow(0)
        QtTest.QTest.mouseClick(self.dialog.button_del_compartment, QtCore.Qt.LeftButton)
        assert self.dialog.compartmentTable.rowCount() == 0

    def test_change_compartment_name(self):
        assert self.dialog.buttonBox.button(QDialogButtonBox.Save).isEnabled() is False
        self.dialog.compartmentTable.item(0, 1).setText(self.new_comp_name)
        assert self.dialog.buttonBox.button(QDialogButtonBox.Save).isEnabled() is True

    def test_save_changes_id(self):
        QtTest.QTest.keyClicks(self.dialog.input_id, self.test_id)
        self.dialog.save_changes()
        assert self.model.id == self.test_id + self.test_id

    def test_save_changes_name(self):
        QtTest.QTest.keyClicks(self.dialog.input_name, self.test_name)
        self.dialog.save_changes()
        assert self.model.name == self.test_name + self.test_name

    def test_save_changes_compartment_addition(self):
        self.dialog._add_new_compartment_to_table(self.new_comp)
        assert self.dialog.compartmentTable.rowCount() == 2
        self.dialog.save_changes()
        assert self.model.gem_compartments == {self.comp1_id: self.comp1,
                                               self.new_comp_id: self.new_comp}
        assert self.metabolite in self.model.metabolites

    def test_save_changes_compartment_deletion(self):
        self.dialog.compartmentTable.setRowCount(0)
        assert self.metabolite in self.model.metabolites
        self.dialog.save_changes()
        assert self.model.gem_compartments == {}
        assert self.metabolite not in self.model.metabolites

    def test_save_changed_compartment_name(self):
        self.dialog.compartmentTable.item(0, 1).setText(self.new_comp_name)
        assert self.dialog.buttonBox.button(QDialogButtonBox.Save).isEnabled() is True
        self.dialog.save_changes()
        assert self.model.gem_compartments[self.comp1_id].name == self.new_comp_name

    def test_save_changed_compartment_id(self):
        new_id = "z"
        self.dialog.compartmentTable.item(0, 0).setText(new_id)
        self.dialog.save_changes()
        assert "z" in self.model.gem_compartments
        assert self.metabolite.compartment == new_id
        assert self.model.gem_compartments[new_id] is self.comp1
        assert self.comp1.name == self.comp1_name

