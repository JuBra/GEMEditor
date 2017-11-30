import os
import GEMEditor
import pytest
from unittest.mock import Mock
from GEMEditor.main import MainWindow
from GEMEditor.model.classes.cobra import Model
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from GEMEditor.base.test.fixtures import progress_not_cancelled

# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])
app.setOrganizationName("GEMEditorTesting")
app_name = "GEMEditorTesting"
app.setApplicationName(app_name)


# Todo: Add test for new version dialog
# @pytest.mark.usefixtures("monkeypatch_QMessageBox_Yes", "monkeypatch_qdesktopservices_openurl")
# def test_show_new_version_dialog(self, main_window):
#     assert QtGui.QDesktopServices.openUrl.called is False
#     assert QMessageBox.question.called is False
#     main_window.show_newversion_dialog()
#     assert QMessageBox.question.called is True
#     assert QtGui.QDesktopServices.openUrl.called is True

# Todo: Add test for new version dialog
# @pytest.mark.usefixtures("monkeypatch_QMessageBox_No", "monkeypatch_qdesktopservices_openurl")
# def test_show_new_version_dialog(self, main_window):
#     assert QtGui.QDesktopServices.openUrl.called is False
#     assert QMessageBox.question.called is False
#     main_window.show_newversion_dialog()
#     assert QMessageBox.question.called is True
#     assert QtGui.QDesktopServices.openUrl.called is False


@pytest.fixture()
def no_update_check(monkeypatch):
    # Prevent main window of checking if a new version is available
    monkeypatch.setattr("GEMEditor.main.MainWindow._check_updates", Mock())


@pytest.fixture()
def openfilename_xml(monkeypatch, tmpdir):
    path = str(tmpdir.mkdir("xml"))+"abs.xml"
    monkeypatch.setattr("PyQt5.QtWidgets.QFileDialog.getOpenFileName", Mock(return_value=(path, ".xml")))
    return path


@pytest.fixture()
def openfilename_empty(monkeypatch):
    monkeypatch.setattr("PyQt5.QtWidgets.QFileDialog.getOpenFileName", Mock(return_value=("", None)))


@pytest.fixture()
def QMessageBox_Yes(monkeypatch):
    monkeypatch.setattr(QMessageBox, "question", Mock(return_value=QMessageBox.Yes))


@pytest.fixture()
def QMessageBox_No(monkeypatch):
    monkeypatch.setattr(QMessageBox, "question", Mock(return_value=QMessageBox.No))


@pytest.fixture()
def editmodeldialog_true(monkeypatch):
    monkeypatch.setattr("GEMEditor.model.edit.model.EditModelDialog.exec_", Mock(return_value=True))


@pytest.fixture()
def editmodeldialog_false(monkeypatch):
    monkeypatch.setattr("GEMEditor.model.edit.model.EditModelDialog.exec_", Mock(return_value=False))


@pytest.fixture()
def read_sbml3_none(monkeypatch):
    monkeypatch.setattr("GEMEditor.rw.sbml3.read_sbml3_model", Mock(return_value=None))


@pytest.fixture()
def read_sbml3_model(monkeypatch):
    monkeypatch.setattr("GEMEditor.rw.sbml3.read_sbml3_model", Mock(return_value=Model("test")))


@pytest.fixture()
def mock_write_sbml3(monkeypatch):
    monkeypatch.setattr("GEMEditor.rw.sbml3.write_sbml3_model", Mock())


@pytest.fixture()
def mock_settings(monkeypatch):
    monkeypatch.setattr("GEMEditor.main.Settings.value", Mock())
    monkeypatch.setattr("GEMEditor.main.Settings.setValue", Mock())
    monkeypatch.setattr("GEMEditor.main.Settings.sync", Mock())
    return GEMEditor.main.Settings


@pytest.fixture()
def getsavefilename_empty(monkeypatch):
    monkeypatch.setattr("PyQt5.QtWidgets.QFileDialog.getSaveFileName", Mock(return_value=("", None)))


@pytest.fixture()
def getsavefilename_xml(monkeypatch, tmpdir):
    path = str(tmpdir.mkdir("xml"))+".xml"
    monkeypatch.setattr("PyQt5.QtWidgets.QFileDialog.getSaveFileName", Mock(return_value=(path, "*.xml")))
    return path

@pytest.fixture()
def parser_model(monkeypatch):
    model = Model()
    monkeypatch.setattr("GEMEditor.rw.parsers.BaseParser.parse", Mock(return_value=model))
    return model

@pytest.fixture()
def parser_none(monkeypatch):
    monkeypatch.setattr("GEMEditor.rw.parsers.BaseParser.parse", Mock(return_value=None))

@pytest.fixture()
def main_window(no_update_check):
    return MainWindow()


@pytest.mark.usefixtures("progress_not_cancelled")
class TestOpenModel:

    @pytest.mark.usefixtures("openfilename_empty")
    def test_model_not_read_if_user_aborts_file_selection(self, main_window, mock_settings):
        main_window.set_model = Mock()
        main_window.open_model()
        assert main_window.set_model.called is False
        assert mock_settings.setValue.called is False

    def test_open_model_close_accepted_xml_path(self, main_window, openfilename_xml, mock_settings, parser_model):
        main_window.set_model = Mock()
        main_window.open_model()
        mock_settings.setValue.assert_called_with("LastPath", os.path.dirname(openfilename_xml))
        main_window.set_model.assert_called_with(parser_model, openfilename_xml)

    def test_no_model_set_with_parsing_error(self, main_window, openfilename_xml, mock_settings, parser_none):
        main_window.set_model = Mock()
        main_window.open_model()
        assert main_window.set_model.called is False
        assert mock_settings.setValue.called is False

    @pytest.mark.usefixtures("read_sbml3_none")
    def test_open_model_close_cancelled(self, main_window, mock_settings):
        main_window.close_model = Mock(return_value=False)
        main_window.open_model()
        assert main_window.close_model.called is True
        assert GEMEditor.rw.sbml3.read_sbml3_model.called is False
        assert mock_settings.setValue.called is False


class TestModelCreate:

    @pytest.mark.usefixtures("editmodeldialog_true")
    def test_createmodel_accept_editmodel_dialog(self, main_window):
        main_window.set_model = Mock()
        main_window._set_model_loaded = Mock()
        main_window.close_model = Mock(return_value=True)
        assert GEMEditor.model.edit.model.EditModelDialog.exec_.called is False

        main_window.new_model()
        assert GEMEditor.model.edit.model.EditModelDialog.exec_.called is True
        assert main_window.set_model.called is True
        main_window._set_model_loaded.assert_called_once_with(True)

    @pytest.mark.usefixtures("editmodeldialog_false")
    def test_createmodel_cancel_editmodel_dialog(self, main_window):
        main_window.set_model = Mock()
        main_window._set_model_loaded = Mock()
        main_window.close_model = Mock(return_value=True)
        assert GEMEditor.model.edit.model.EditModelDialog.exec_.called is False

        main_window.new_model()
        assert GEMEditor.model.edit.model.EditModelDialog.exec_.called is True
        assert main_window.set_model.called is False
        assert main_window._set_model_loaded.called is False

    @pytest.mark.usefixtures("editmodeldialog_false")
    def test_createmodel_cancel_editmodel_dialog(self, main_window):
        main_window.set_model = Mock()
        main_window._set_model_loaded = Mock()
        main_window.close_model = Mock(return_value=False)
        assert GEMEditor.model.edit.model.EditModelDialog.exec_.called is False

        main_window.new_model()
        assert GEMEditor.model.edit.model.EditModelDialog.exec_.called is False
        assert main_window.set_model.called is False
        assert main_window._set_model_loaded.called is False


class TestSetModel:

    def test_set_model(self, main_window):
        assert main_window.model is None
        assert main_window.model_path is None
        for i in range(main_window.tabWidget.count()):
            main_window.tabWidget.widget(i).set_model = Mock()

        model = Model("id_1")
        model_path = "model_path"
        main_window.set_model(model, model_path)
        assert main_window.model is model
        assert main_window.model_path == model_path
        for i in range(main_window.tabWidget.count()):
            assert main_window.tabWidget.widget(i).set_model.called


class TestModelSave:

    @pytest.mark.usefixtures("mock_write_sbml3", "getsavefilename_empty")
    def test_saving_file_user_cancelled(self, main_window, mock_settings):
        main_window.save_model()
        mock_settings.value.assert_called_with("LastPath")
        assert QFileDialog.getSaveFileName.called is True
        assert GEMEditor.rw.sbml3.write_sbml3_model.called is False
        assert mock_settings.setValue.called is False

    @pytest.mark.usefixtures("mock_write_sbml3")
    def test_saving_file_user_accepted(self, main_window, getsavefilename_xml, mock_settings):
        model = Model()
        main_window.model = model
        main_window.save_model()
        GEMEditor.rw.sbml3.write_sbml3_model.assert_called_with(getsavefilename_xml, model)
        mock_settings.setValue.assert_called_with("LastPath", os.path.dirname(getsavefilename_xml))


class TestModelEdit:

    @pytest.mark.usefixtures("editmodeldialog_true")
    def test_editmodelsettings_cancelled(self, main_window):
        main_window.set_model = Mock()
        main_window.update_window_title = Mock()
        main_window.model = Model("test_id")
        assert main_window.set_model.called is False
        assert main_window.update_window_title.called is False

        main_window.edit_model()
        assert main_window.set_model.called is True
        assert main_window.update_window_title.called is True

    @pytest.mark.usefixtures("editmodeldialog_false")
    def test_editmodelsettings_cancelled(self, main_window):
        main_window.set_model = Mock()
        main_window.update_window_title = Mock()
        main_window.model = Model("test_id")
        assert main_window.set_model.called is False
        assert main_window.update_window_title.called is False

        main_window.edit_model()
        assert main_window.set_model.called is False
        assert main_window.update_window_title.called is False


class TestModelLoaded:

    def test_model_loaded(self, main_window):
        model = Model("test_id")
        main_window.model = model
        main_window = MainWindow()

        # Check active actions/menus
        # -> File
        assert main_window.menuFile.isEnabled()
        assert main_window.actionOpenModel.isEnabled()
        assert main_window.actionNewModel.isEnabled()
        assert main_window.actionLoadTestModel.isEnabled()
        assert main_window.actionCloseEditor.isEnabled()
        # -> Edit
        assert main_window.menuEdit.isEnabled()
        for action in main_window.menuEdit.actions():
            assert action.isEnabled()
        # -> Help
        assert main_window.menuHelp.isEnabled()
        for action in main_window.menuHelp.actions():
            assert action.isEnabled()

        # Check inactive actions/menus
        # -> File
        assert not main_window.actionSaveModel.isEnabled()
        assert not main_window.actionCloseModel.isEnabled()
        # -> Model
        assert not main_window.menuModel.isEnabled()
        # -> Metanetx
        assert not main_window.menuMetaNetX.isEnabled()

        main_window._set_model_loaded(True)

        # Check active actions/menus
        # -> File
        assert main_window.menuFile.isEnabled()
        for action in main_window.menuFile.actions():
            assert action.isEnabled()
        # -> Edit
        assert main_window.menuEdit.isEnabled()
        for action in main_window.menuEdit.actions():
            assert action.isEnabled()
        # -> Model
        assert main_window.menuModel.isEnabled()
        # -> MetaNetX
        assert main_window.menuMetaNetX.isEnabled()
        # -> Help
        assert main_window.menuHelp.isEnabled()
        for action in main_window.menuHelp.actions():
            assert action.isEnabled()


class TestModelClosing:

    @pytest.fixture()
    def mock_close_model(self, main_window):
        main_window.save_table_headers = Mock()
        main_window._set_model_loaded = Mock()
        main_window.set_model = Mock()
        return main_window

    @pytest.mark.usefixtures("QMessageBox_Yes")
    def test_return_true_if_yes_selected(self, main_window):
        main_window.model = Model()
        assert main_window.check_model_closing() is True

    @pytest.mark.usefixtures("QMessageBox_No")
    def test_return_false_if_no_selected(self, main_window):
        main_window.model = Model()
        assert main_window.check_model_closing() is False

    def test_close_model_none(self, mock_close_model):
        main_window = mock_close_model
        assert main_window.model is None
        assert main_window.close_model() is True
        assert main_window.save_table_headers.called is False
        assert main_window._set_model_loaded.called is False
        assert main_window.set_model.called is False

    @pytest.mark.usefixtures("QMessageBox_Yes")
    def test_close_model_model_accept(self, mock_close_model):
        main_window = mock_close_model
        main_window.model = Model()
        assert main_window.close_model() is True
        assert main_window.save_table_headers.call_count == 1
        main_window._set_model_loaded.assert_called_once_with(False)
        main_window.set_model.assert_called_once_with(None, None)

    @pytest.mark.usefixtures("QMessageBox_No")
    def test_close_model_model_cancel(self, mock_close_model):
        main_window = mock_close_model
        main_window.model = Model()
        assert main_window.close_model() is False
        assert main_window.save_table_headers.called is False
        assert main_window._set_model_loaded.called is False
        assert main_window.set_model.called is False


class TestMainEditSettings:

    @pytest.fixture(autouse=True)
    def patch_dialog(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.main.EditSettingsDialog.exec_", Mock())

    def test_showing_settings_dialog(self, main_window):
        assert GEMEditor.main.EditSettingsDialog.exec_.called is False
        main_window.actionEditSettings.trigger()
        assert GEMEditor.main.EditSettingsDialog.exec_.called is True


class TestMainAbout:

    @pytest.fixture(autouse=True)
    def patch_dialog(self, monkeypatch):
        monkeypatch.setattr("GEMEditor.main.AboutDialog.exec_", Mock())

    def test_showing_about_dialog(self, main_window):
        assert GEMEditor.main.AboutDialog.exec_.called is False
        main_window.actionAbout.trigger()
        assert GEMEditor.main.AboutDialog.exec_.called is True

