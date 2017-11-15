from unittest.mock import Mock

from GEMEditor.model.classes.cobra import Metabolite, Model
from GEMEditor.model.display.metabolite import MetaboliteAttributesDisplayWidget
from PyQt5 import QtTest, QtCore


class TestMetaboliteAttributesDisplayWidget:

    def test_setting_item(self):
        metabolite = Metabolite("test_id", "H2O", "Test metabolie", -5, "m")
        model = Model()

        widget = MetaboliteAttributesDisplayWidget()

        # Test prestate
        assert widget.iDLineEdit.text() == ""
        assert widget.nameLineEdit.text() == ""
        assert widget.compartmentComboBox.currentText() == ""
        assert widget.chargeSpinBox.value() == 0
        assert widget.formulaLineEdit.text() == ""

        widget.set_item(metabolite, model)

        assert widget.iDLineEdit.text() == metabolite.id
        assert widget.nameLineEdit.text() == metabolite.name
        assert widget.compartmentComboBox.currentText() == metabolite.compartment
        assert widget.chargeSpinBox.value() == metabolite.charge
        assert widget.formulaLineEdit.text() == metabolite.formula

        assert widget.valid_inputs() is True
        assert widget.content_changed is False

        widget.set_item(None, model)

        assert widget.iDLineEdit.text() == ""
        assert widget.nameLineEdit.text() == ""
        assert widget.compartmentComboBox.currentText() == ""
        assert widget.chargeSpinBox.value() == 0.
        assert widget.formulaLineEdit.text() == ""

        assert widget.valid_inputs() is False
        assert widget.content_changed is False

    def test_save_state(self):

        metabolite = Metabolite()
        model = Model()

        widget = MetaboliteAttributesDisplayWidget()

        widget.set_item(metabolite, model)

        new_id = "New id"
        new_name = "New name"
        new_charge = 3.
        new_compartment = "m"
        new_formula = "H2O"

        widget.iDLineEdit.setText(new_id)
        widget.nameLineEdit.setText(new_name)
        widget.chargeSpinBox.setValue(new_charge)
        widget.compartmentComboBox.addItem(new_compartment)
        widget.compartmentComboBox.setCurrentIndex(widget.compartmentComboBox.count()-1)
        widget.formulaLineEdit.setText(new_formula)

        widget.save_state()

        assert metabolite.id == new_id
        assert metabolite.name == new_name
        assert metabolite.charge == new_charge
        assert metabolite.compartment == new_compartment
        assert metabolite.formula == new_formula

    def test_changed_triggered_by_idchange(self):

        widget = MetaboliteAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.iDLineEdit, "A")
        assert mock.test.called is True

    def test_changed_triggered_by_name_change(self):
        widget = MetaboliteAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.nameLineEdit, "A")
        assert mock.test.called is True

    def test_changed_triggered_by_formula_change(self):
        widget = MetaboliteAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.formulaLineEdit, "A")
        assert mock.test.called is True

    def test_changed_triggered_by_charge_change(self):
        widget = MetaboliteAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.formulaLineEdit, "3")
        assert mock.test.called is True

    def test_changed_triggered_by_compartment_change(self):
        widget = MetaboliteAttributesDisplayWidget()
        mock = Mock()
        widget.compartmentComboBox.addItem("m")
        widget.compartmentComboBox.setCurrentIndex(-1)
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClick(widget.compartmentComboBox, QtCore.Qt.Key_Down)
        assert mock.test.called is True

    def test_valid_input(self):
        # Note: The compartment needs to be set as valid input
        metabolite = Metabolite(id="test", compartment="m")
        model = Model()

        widget = MetaboliteAttributesDisplayWidget()

        widget.set_item(metabolite, model)
        assert widget.valid_inputs() is True
        widget.iDLineEdit.clear()
        assert widget.valid_inputs() is False