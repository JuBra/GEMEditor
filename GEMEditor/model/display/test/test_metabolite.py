from unittest.mock import Mock
from GEMEditor.model.classes.cobra import Metabolite, Model
from GEMEditor.model.display.metabolite import MetaboliteAttributesDisplayWidget
from PyQt5 import QtTest, QtCore, QtGui
from PyQt5.QtWidgets import QApplication

# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


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
        model.add_metabolites((metabolite,))
        model.setup_metabolite_table()

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

    def test_changing_id(self):
        metabolite = Metabolite(compartment="m")
        model = Model()

        widget = MetaboliteAttributesDisplayWidget()
        widget.set_item(metabolite, model)
        assert widget._id_valid is False

        QtTest.QTest.keyClick(widget.iDLineEdit, "V")
        assert widget._id_valid is True

        QtTest.QTest.keyClick(widget.iDLineEdit, "a")
        assert widget._id_valid is True

        QtTest.QTest.keyClick(widget.iDLineEdit, "#")
        assert widget._id_valid is False

    def test_changing_formula(self):
        metabolite = Metabolite(id="m1", compartment="m")
        model = Model()

        widget = MetaboliteAttributesDisplayWidget()
        widget.set_item(metabolite, model)
        assert widget._id_valid is True

        # Check empty formula is valid
        assert widget._formula_valid is True

        QtTest.QTest.keyClick(widget.formulaLineEdit, "C")
        assert widget._formula_valid is True

        QtTest.QTest.keyClick(widget.formulaLineEdit, "2")
        assert widget._formula_valid is True

        QtTest.QTest.keyClick(widget.formulaLineEdit, "(")
        assert widget._formula_valid is False
