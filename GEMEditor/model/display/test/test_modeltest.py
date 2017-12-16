from unittest.mock import Mock
from GEMEditor.model.classes.cobra import Model, Reaction, Gene
from GEMEditor.model.classes.modeltest import ModelTest, ReactionSetting, GeneSetting, Outcome
from GEMEditor.model.display.modeltest import ReactionSettingDisplayWidget, GeneSettingDisplayWidget, \
    OutcomeDisplayWidget
from PyQt5 import QtTest, QtCore
from PyQt5.QtWidgets import QWidget, QApplication

# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestReactionSettingDisplayWidget:

    def test_setting_item(self):
        parent = QWidget()
        widget = ReactionSettingDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        setting = ReactionSetting(reaction, 1000., -1000., 5.)
        model = Model()

        test.add_setting(setting)

        widget.dataTable.populate_table = Mock()

        widget.set_item(test, model)

        widget.dataTable.populate_table.assert_called_once_with(test.reaction_settings)
        assert widget.model is model
        assert widget.model_test is test

    def test_content_changed(self):
        parent = QWidget()
        widget = ReactionSettingDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        setting = ReactionSetting(reaction, 1000., -1000., 5.)
        model = Model()

        test.add_setting(setting)
        widget.set_item(test, model)

        assert widget.content_changed is False

    def test_saving_items(self):

        parent = QWidget()
        widget = ReactionSettingDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        setting = ReactionSetting(reaction, 1000., -1000., 5.)
        model = Model()

        test.add_setting(setting)
        widget.set_item(test, model)

        new_test = ModelTest()
        widget.model_test = new_test

        assert len(new_test.reaction_settings) == 0
        widget.save_state()
        assert len(new_test.reaction_settings) == 1

        new_setting = list(new_test.reaction_settings)[0]

        assert new_setting == setting
        assert new_setting is not setting

    def test_addition_emits_changed(self):
        parent = QWidget()
        widget = ReactionSettingDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        setting = ReactionSetting(reaction, 1000., -1000., 5.)
        model = Model()

        test.add_setting(setting)
        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.dataTable.update_row_from_item(ReactionSetting(Reaction(), 200., -200, 0.))
        assert detector.test.called is True
        assert widget.content_changed is True

    def test_modification_emits_changed(self):
        parent = QWidget()
        widget = ReactionSettingDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        setting = ReactionSetting(reaction, 1000., -1000., 5.)
        model = Model()

        test.add_setting(setting)
        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.dataTable.item(0, 1).setData(500, 2)
        assert detector.test.called is True
        assert widget.content_changed is True

    def test_deletion_emits_changed(self):
        parent = QWidget()
        widget = ReactionSettingDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        setting = ReactionSetting(reaction, 1000., -1000., 5.)
        model = Model()

        test.add_setting(setting)
        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.tableView.selectRow(0)
        QtTest.QTest.mouseClick(widget.button_del_item, QtCore.Qt.LeftButton)
        assert widget.dataTable.rowCount() == 0
        assert detector.test.called is True
        assert widget.content_changed is True


class TestGeneSettingDisplayWidget:

    def test_setting_item(self):
        parent = QWidget()
        widget = GeneSettingDisplayWidget(parent)
        test = ModelTest()
        gene = Gene()
        setting = GeneSetting(gene, False)
        model = Model()

        test.add_setting(setting)

        widget.dataTable.populate_table = Mock()

        widget.set_item(test, model)

        widget.dataTable.populate_table.assert_called_once_with(test.gene_settings)
        assert widget.model is model
        assert widget.model_test is test

    def test_saving_items(self):

        parent = QWidget()
        widget = GeneSettingDisplayWidget(parent)
        test = ModelTest()
        gene = Gene()
        setting = GeneSetting(gene, False)
        model = Model()

        test.add_setting(setting)
        widget.set_item(test, model)

        new_test = ModelTest()
        widget.model_test = new_test

        assert len(new_test.gene_settings) == 0
        widget.save_state()
        assert len(new_test.gene_settings) == 1

        new_setting = list(new_test.gene_settings)[0]

        assert new_setting == setting
        assert new_setting is not setting

    def test_addition_emits_changed(self):
        parent = QWidget()
        widget = GeneSettingDisplayWidget(parent)
        test = ModelTest()
        gene = Gene()
        setting = GeneSetting(gene, False)
        model = Model()

        test.add_setting(setting)
        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.dataTable.update_row_from_item(GeneSetting(Gene(), True))
        assert detector.test.called is True
        assert widget.content_changed is True

    def test_modification_emits_changed(self):
        parent = QWidget()
        widget = GeneSettingDisplayWidget(parent)
        test = ModelTest()
        gene = Gene()
        setting = GeneSetting(gene, True)
        model = Model()

        test.add_setting(setting)
        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.dataTable.item(0, 1).setText("inactive")
        assert detector.test.called is True
        assert widget.content_changed is True

    def test_deletion_emits_changed(self):
        parent = QWidget()
        widget = GeneSettingDisplayWidget(parent)
        test = ModelTest()
        gene = Gene()
        setting = GeneSetting(gene, False)
        model = Model()

        test.add_setting(setting)
        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.tableView.selectRow(0)
        QtTest.QTest.mouseClick(widget.button_del_item, QtCore.Qt.LeftButton)
        assert widget.dataTable.rowCount() == 0
        assert detector.test.called is True
        assert widget.content_changed is True


class TestOutcomeDisplayWidget:

    def test_setting_item(self):
        parent = QWidget()
        widget = OutcomeDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        outcome = Outcome(reaction, 0., "greater than")
        model = Model()

        test.add_outcome(outcome)

        widget.dataTable.populate_table = Mock()

        widget.set_item(test, model)

        widget.dataTable.populate_table.assert_called_once_with(test.outcomes)
        assert widget.model is model
        assert widget.model_test is test

    def test_saving_items(self):

        parent = QWidget()
        widget = OutcomeDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        outcome = Outcome(reaction, 0., "greater than")
        model = Model()

        test.add_outcome(outcome)
        widget.set_item(test, model)

        new_test = ModelTest()
        widget.model_test = new_test

        assert len(new_test.outcomes) == 0
        widget.save_state()
        assert len(new_test.outcomes) == 1

        new_setting = list(new_test.outcomes)[0]

        assert new_setting == outcome
        assert new_setting is not outcome

    def test_addition_emits_changed(self):

        parent = QWidget()
        widget = OutcomeDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        outcome = Outcome(reaction, 0., "greater than")
        model = Model()

        test.add_outcome(outcome)
        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.dataTable.update_row_from_item(Outcome(Reaction()))
        assert detector.test.called is True
        assert widget.content_changed is True

    def test_modification_emits_changed(self):

        parent = QWidget()
        widget = OutcomeDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        outcome = Outcome(reaction, 0., "greater than")
        model = Model()

        test.add_outcome(outcome)
        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.dataTable.item(0, 1).setText("less than")
        assert detector.test.called is True
        assert widget.content_changed is True

    def test_deletion_emits_changed(self):

        parent = QWidget()
        widget = OutcomeDisplayWidget(parent)
        test = ModelTest()
        reaction = Reaction()
        outcome = Outcome(reaction, 0., "greater than")
        model = Model()

        test.add_outcome(outcome)
        widget.set_item(test, model)

        detector = Mock()
        widget.changed.connect(detector.test)

        widget.tableView.selectRow(0)
        QtTest.QTest.mouseClick(widget.button_del_item, QtCore.Qt.LeftButton)
        assert widget.dataTable.rowCount() == 0
        assert detector.test.called is True
        assert widget.content_changed is True