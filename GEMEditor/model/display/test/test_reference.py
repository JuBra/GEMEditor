from unittest.mock import Mock
from GEMEditor.model.classes import ModelTest, Model, Reference
from GEMEditor.model.display.reference import ReferenceDisplayWidget
from PyQt5 import QtTest, QtCore
from PyQt5.QtWidgets import QWidget


class TestReferenceDisplayWidget:

    def test_setting_item(self):
        parent = QWidget()
        widget = ReferenceDisplayWidget(parent)
        test = ModelTest()
        model = Model()

        widget.dataTable.populate_table = Mock()

        widget.set_item(test, model)

        widget.dataTable.populate_table.assert_called_once_with(test.references)
        assert widget.model is model
        assert widget.item is test

    def test_saving_items(self):

        parent = QWidget()
        widget = ReferenceDisplayWidget(parent)
        test = ModelTest()
        reference = Reference()
        test.add_reference(reference)

        model = Model()

        widget.set_item(test, model)

        new_test = ModelTest()
        widget.item = new_test

        assert len(new_test.references) == 0
        widget.save_state()
        assert len(new_test.references) == 1

        new_reference = list(new_test.references)[0]

        assert new_reference is reference

    def test_addition_emits_changed(self):
        parent = QWidget()
        widget = ReferenceDisplayWidget(parent)
        test = ModelTest()
        reference = Reference()
        test.add_reference(reference)
        model = Model()

        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.dataTable.update_row_from_item(Reference())
        assert detector.test.called is True
        assert widget.content_changed is True

    def test_deletion_emits_changed(self):
        parent = QWidget()
        widget = ReferenceDisplayWidget(parent)
        test = ModelTest()
        reference = Reference()
        test.add_reference(reference)
        model = Model()

        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.tableView.selectRow(0)
        QtTest.QTest.mouseClick(widget.button_del_item, QtCore.Qt.LeftButton)
        assert widget.dataTable.rowCount() == 0
        assert detector.test.called is True
        assert widget.content_changed is True