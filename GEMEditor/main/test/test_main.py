import pytest
import os
from GEMEditor.main import MainWindow
from GEMEditor.base.test.fixtures import progress_not_cancelled
from GEMEditor.base.classes import Settings
from GEMEditor.cobraClasses import Model
import GEMEditor
from unittest.mock import Mock
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog


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
    monkeypatch.setattr("GEMEditor.main.MainWindow.check_updates", Mock())


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
def main_window(no_update_check):
    return MainWindow()


@pytest.mark.usefixtures("progress_not_cancelled")
class TestOpenModel:

    @pytest.mark.usefixtures("read_sbml3_none", "openfilename_empty")
    def test_model_not_read_if_user_aborts_file_selection(self, main_window, mock_settings):
        main_window.closeModel = Mock(return_value=True)
        main_window.set_model = Mock()
        main_window.modelLoaded = Mock()
        main_window.openModel()
        assert GEMEditor.rw.sbml3.read_sbml3_model.called is False
        assert main_window.set_model.called is False
        assert main_window.modelLoaded.called is False
        assert mock_settings.setValue.called is False

    @pytest.mark.usefixtures("read_sbml3_none")
    def test_open_model_close_accepted_xml_path(self, main_window, openfilename_xml, mock_settings):
        main_window.closeModel = Mock(return_value=True)
        main_window.set_model = Mock()
        main_window.modelLoaded = Mock()
        main_window.openModel()
        assert GEMEditor.rw.sbml3.read_sbml3_model.called is True
        mock_settings.setValue.assert_called_with("LastPath", os.path.dirname(openfilename_xml))
        assert main_window.set_model.called is False
        assert main_window.modelLoaded.called is False

    @pytest.mark.usefixtures("read_sbml3_model")
    def test_open_model_close_accepted_xml_path2(self, main_window, openfilename_xml, mock_settings):
        main_window.closeModel = Mock(return_value=True)
        main_window.set_model = Mock()
        main_window.modelLoaded = Mock()
        main_window.openModel()
        mock_settings.setValue.assert_called_with("LastPath", os.path.dirname(openfilename_xml))
        assert QFileDialog.getOpenFileName.called is True
        assert GEMEditor.rw.sbml3.read_sbml3_model.called is True
        assert main_window.set_model.called is True
        assert main_window.modelLoaded.called is True

    @pytest.mark.usefixtures("read_sbml3_none")
    def test_open_model_close_cancelled(self, main_window, mock_settings):
        main_window.closeModel = Mock(return_value=False)
        main_window.openModel()
        assert main_window.closeModel.called is True
        assert GEMEditor.rw.sbml3.read_sbml3_model.called is False
        assert mock_settings.setValue.called is False


class TestModelCreate:

    @pytest.mark.usefixtures("editmodeldialog_true")
    def test_createmodel_accept_editmodel_dialog(self, main_window):
        main_window.set_model = Mock()
        main_window.modelLoaded = Mock()
        main_window.closeModel = Mock(return_value=True)
        assert GEMEditor.model.edit.model.EditModelDialog.exec_.called is False

        main_window.createModel()
        assert GEMEditor.model.edit.model.EditModelDialog.exec_.called is True
        assert main_window.set_model.called is True
        main_window.modelLoaded.assert_called_once_with(True)

    @pytest.mark.usefixtures("editmodeldialog_false")
    def test_createmodel_cancel_editmodel_dialog(self, main_window):
        main_window.set_model = Mock()
        main_window.modelLoaded = Mock()
        main_window.closeModel = Mock(return_value=True)
        assert GEMEditor.model.edit.model.EditModelDialog.exec_.called is False

        main_window.createModel()
        assert GEMEditor.model.edit.model.EditModelDialog.exec_.called is True
        assert main_window.set_model.called is False
        assert main_window.modelLoaded.called is False

    @pytest.mark.usefixtures("editmodeldialog_false")
    def test_createmodel_cancel_editmodel_dialog(self, main_window):
        main_window.set_model = Mock()
        main_window.modelLoaded = Mock()
        main_window.closeModel = Mock(return_value=False)
        assert GEMEditor.model.edit.model.EditModelDialog.exec_.called is False

        main_window.createModel()
        assert GEMEditor.model.edit.model.EditModelDialog.exec_.called is False
        assert main_window.set_model.called is False
        assert main_window.modelLoaded.called is False


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
        main_window.saveModel()
        mock_settings.value.assert_called_with("LastPath")
        assert QFileDialog.getSaveFileName.called is True
        assert GEMEditor.rw.sbml3.write_sbml3_model.called is False
        assert mock_settings.setValue.called is False

    @pytest.mark.usefixtures("mock_write_sbml3")
    def test_saving_file_user_accepted(self, main_window, getsavefilename_xml, mock_settings):
        model = Model()
        main_window.model = model
        main_window.saveModel()
        GEMEditor.rw.sbml3.write_sbml3_model.assert_called_with(getsavefilename_xml, model)
        mock_settings.setValue.assert_called_with("LastPath", os.path.dirname(getsavefilename_xml))


class TestModelEdit:

    @pytest.mark.usefixtures("editmodeldialog_true")
    def test_editmodelsettings_cancelled(self, main_window):
        main_window.set_model = Mock()
        main_window.set_window_title = Mock()
        main_window.model = Model("test_id")
        assert main_window.set_model.called is False
        assert main_window.set_window_title.called is False

        main_window.editModelsettings()
        assert main_window.set_model.called is True
        assert main_window.set_window_title.called is True

    @pytest.mark.usefixtures("editmodeldialog_false")
    def test_editmodelsettings_cancelled(self, main_window):
        main_window.set_model = Mock()
        main_window.set_window_title = Mock()
        main_window.model = Model("test_id")
        assert main_window.set_model.called is False
        assert main_window.set_window_title.called is False

        main_window.editModelsettings()
        assert main_window.set_model.called is False
        assert main_window.set_window_title.called is False


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
        # -> MetaNetX
        assert not main_window.menuSimulation.isEnabled()

        main_window.modelLoaded(True)

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
        assert main_window.menuSimulation.isEnabled()
        # -> Help
        assert main_window.menuHelp.isEnabled()
        for action in main_window.menuHelp.actions():
            assert action.isEnabled()


class TestModelClosing:

    @pytest.fixture()
    def mock_close_model(self, main_window):
        main_window.save_table_headers = Mock()
        main_window.modelLoaded = Mock()
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
        assert main_window.closeModel() is True
        assert main_window.save_table_headers.called is False
        assert main_window.modelLoaded.called is False
        assert main_window.set_model.called is False

    @pytest.mark.usefixtures("QMessageBox_Yes")
    def test_close_model_model_accept(self, mock_close_model):
        main_window = mock_close_model
        main_window.model = Model()
        assert main_window.closeModel() is True
        assert main_window.save_table_headers.call_count == 1
        main_window.modelLoaded.assert_called_once_with(False)
        main_window.set_model.assert_called_once_with(None, None)

    @pytest.mark.usefixtures("QMessageBox_No")
    def test_close_model_model_cancel(self, mock_close_model):
        main_window = mock_close_model
        main_window.model = Model()
        assert main_window.closeModel() is False
        assert main_window.save_table_headers.called is False
        assert main_window.modelLoaded.called is False
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

