import pytest
from GEMEditor.model.classes.cobra import Model
from GEMEditor.rw import *
from GEMEditor.rw.model import parse_model_info, setup_sbml3_model
from PyQt5.QtWidgets import QApplication
from lxml.etree import Element


# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestModelIO:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.test_id = "test_id"
        self.test_name = "test_name"
        self.model = Model(id_or_model=self.test_id,
                           name=self.test_name)

    def test_setup_items(self):
        assert self.model.id == self.test_id
        assert self.model.name == self.test_name

    def test_setup_sbml3_model(self):
        root = Element("root")
        new_node = setup_sbml3_model(root, self.model)

        assert len(root) == 1
        model_node = root.find(sbml3_model)
        assert model_node is not None
        assert new_node is model_node

        assert model_node.get("id") == self.test_id
        assert model_node.get("name") == self.test_name

    def test_write_parse_consistency(self):
        root = Element("root")
        setup_sbml3_model(root, self.model)

        new_model = Model()
        parse_model_info(None, new_model, root[0], None)

        assert new_model.id == self.model.id
        assert new_model.name == self.model.name
