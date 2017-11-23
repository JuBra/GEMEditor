from unittest.mock import Mock
from PyQt5 import QtTest
from PyQt5.QtWidgets import QApplication
from GEMEditor.model.classes.cobra import Model, Gene
from GEMEditor.model.display.gene import GeneAttributesDisplayWidget


# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestGeneAttributesDisplayWidget:

    def test_setting_item(self):
        gene = Gene("test_id", "name", "genome")
        model = Model()

        widget = GeneAttributesDisplayWidget()

        # Test prestate
        assert widget.iDLineEdit.text() == ""
        assert widget.nameLineEdit.text() == ""
        assert widget.genomeLineEdit.text() == ""

        widget.set_item(gene, model)

        assert widget.iDLineEdit.text() == gene.id
        assert widget.nameLineEdit.text() == gene.name
        assert widget.genomeLineEdit.text() == gene.genome

        assert widget.valid_inputs() is True
        assert widget.content_changed is False

        widget.set_item(None, model)

        assert widget.iDLineEdit.text() == ""
        assert widget.nameLineEdit.text() == ""
        assert widget.genomeLineEdit.text() == ""

        assert widget.valid_inputs() is False
        assert widget.content_changed is False

    def test_save_state(self):

        gene = Gene()
        model = Model()

        widget = GeneAttributesDisplayWidget()

        widget.set_item(gene, model)

        new_id = "New id"
        new_name = "New name"
        new_genome = "New genome"

        widget.iDLineEdit.setText(new_id)
        widget.nameLineEdit.setText(new_name)
        widget.genomeLineEdit.setText(new_genome)

        widget.save_state()

        assert gene.id == new_id
        assert gene.name == new_name
        assert gene.genome == new_genome

    def test_changed_triggered_by_idchange(self):

        widget = GeneAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.iDLineEdit, "A")
        assert mock.test.called is True

    def test_changed_triggered_by_name_change(self):
        widget = GeneAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.nameLineEdit, "A")
        assert mock.test.called is True

    def test_changed_triggered_by_genome_change(self):
        widget = GeneAttributesDisplayWidget()
        mock = Mock()
        widget.changed.connect(mock.test)

        assert mock.test.called is False
        QtTest.QTest.keyClicks(widget.genomeLineEdit, "A")
        assert mock.test.called is True

    def test_valid_input(self):
        gene = Gene(id="test")
        model = Model()

        widget = GeneAttributesDisplayWidget()

        widget.set_item(gene, model)
        assert widget.valid_inputs() is True
        widget.iDLineEdit.clear()
        assert widget.valid_inputs() is False