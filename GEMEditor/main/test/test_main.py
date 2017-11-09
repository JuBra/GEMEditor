import pytest
from GEMEditor.main import MainWindow
from GEMEditor.cobraClasses import Model
import GEMEditor
from unittest.mock import Mock
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog, QProgressDialog


# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])
app.setOrganizationName("GEMEditorTesting")
app_name = "GEMEditorTesting"
app.setApplicationName(app_name)


@pytest.fixture()
def set_email(monkeypatch):
    def f(*args, **kwargs):
        return "test@testmail.com"
    monkeypatch.setattr(QtCore.QSettings, "value", f)


@pytest.fixture()
def monkeypatch_settings(monkeypatch):
    monkeypatch.setattr(QtCore.QSettings, "setValue", Mock())
    monkeypatch.setattr(QtCore.QSettings, "sync", Mock())


@pytest.fixture()
def monkeypatch_check_updates(monkeypatch):
    monkeypatch.setattr("GEMEditor.main.MainWindow.check_updates", Mock())


@pytest.fixture()
def monkeypatch_check_email(monkeypatch):
    monkeypatch.setattr("GEMEditor.main.MainWindow.check_email", Mock())


@pytest.fixture()
def main_window(monkeypatch):
    monkeypatch.setattr("GEMEditor.main.MainWindow.check_updates", Mock())
    monkeypatch.setattr("GEMEditor.main.MainWindow.check_email", Mock())
    return MainWindow()


@pytest.fixture()
def monkeypatched_close_model(main_window):
    main_window.save_table_headers = Mock()
    main_window.modelLoaded = Mock()
    main_window.set_model = Mock()
    return main_window


@pytest.fixture()
def monkeypatch_QMessageBox_Yes(monkeypatch):
    monkeypatch.setattr(QMessageBox, "question", Mock(return_value=QMessageBox.Yes))


@pytest.fixture()
def monkeypatch_QMessageBox_No(monkeypatch):
    monkeypatch.setattr(QMessageBox, "question", Mock(return_value=QMessageBox.No))


@pytest.fixture()
def monkeypatch_editsettingsdialog(monkeypatch):
    monkeypatch.setattr("GEMEditor.main.settings.EditSettingsDialog.exec_", Mock())


@pytest.fixture()
def monkeypatch_setwindowtitle(monkeypatch):
    monkeypatch.setattr("GEMEditor.main.MainWindow.set_window_title", Mock())

@pytest.fixture()
def monkeypatch_about_dialog(monkeypatch):
    monkeypatch.setattr("GEMEditor.main.about.AboutDialog.exec_", Mock())

@pytest.fixture()
def monkeypatch_qdesktopservices_openurl(monkeypatch):
    monkeypatch.setattr("PyQt5.QtGui.QDesktopServices.openUrl", Mock())

@pytest.fixture()
def monkeypatch_editmodeldialog_return_true(monkeypatch):
    monkeypatch.setattr("GEMEditor.dialogs.model.EditModelDialog.exec_", Mock(return_value=True))

@pytest.fixture()
def monkeypatch_editmodeldialog_return_false(monkeypatch):
    monkeypatch.setattr("GEMEditor.dialogs.model.EditModelDialog.exec_", Mock(return_value=False))

@pytest.fixture()
def monkeypatch_getopenfilename_return_empty_string(monkeypatch):
    monkeypatch.setattr("PyQt5.QtWidgets.QFileDialog.getOpenFileName", Mock(return_value=("", None)))

@pytest.fixture()
def monkeypatch_getopenfilename_return_xml_path(monkeypatch, tmpdir):
    path = tmpdir.mkdir("xml")
    monkeypatch.setattr("PyQt5.QtWidgets.QFileDialog.getOpenFileName", Mock(return_value=(str(path), ".xml")))

@pytest.fixture()
def monkeypatch_getsavefilename_return_empty_string(monkeypatch):
    monkeypatch.setattr("PyQt5.QtWidgets.QFileDialog.getSaveFileName", Mock(return_value=("", None)))

@pytest.fixture()
def monkeypatch_getsavefilename_return_xml_path(monkeypatch, tmpdir):
    path = tmpdir.mkdir("xml")
    monkeypatch.setattr("PyQt5.QtWidgets.QFileDialog.getSaveFileName", Mock(return_value=(str(path)+".xml", "*.xml")))

@pytest.fixture()
def monkeypatch_qsettings_complete(monkeypatch):
    monkeypatch.setattr("PyQt5.QtCore.QSettings", Mock())
    monkeypatch.setattr("GEMEditor.main.MainWindow.set_window_title", Mock())

@pytest.fixture()
def monkeypatch_progress(monkeypatch):
    monkeypatch.setattr("PyQt5.QtWidgets.QProgressDialog", Mock())

@pytest.fixture()
def mock_read_sbml3(monkeypatch):
    monkeypatch.setattr("GEMEditor.rw.sbml3.read_sbml3_model", Mock(return_value=None))

@pytest.fixture()
def mock_read_sbml3_return_model(monkeypatch):
    monkeypatch.setattr("GEMEditor.rw.sbml3.read_sbml3_model", Mock(return_value=Model("test")))

@pytest.fixture()
def mock_write_sbml3(monkeypatch):
    monkeypatch.setattr("GEMEditor.rw.sbml3.write_sbml3_model", Mock())


class TestMainWindow:

    def test_setup(self, main_window):
        assert main_window.model is None
        assert main_window.model_path is None
        assert main_window.thread is None
        assert main_window.worker is None

        assert main_window.check_updates.called is True
        assert main_window.check_email.called is True
        assert main_window.windowTitle() == app_name

        assert main_window.actionNewModel.isEnabled() is True
        assert main_window.actionOpenModel.isEnabled() is True
        assert main_window.actionLoadTestModel.isEnabled() is True
        assert main_window.actionSaveModel.isEnabled() is False
        assert main_window.actionCloseModel.isEnabled() is False
        assert main_window.actionCloseEditor.isEnabled() is True
        assert main_window.actionEditSettings.isEnabled() is True
        assert main_window.actionStatistics.isEnabled() is False

    @pytest.mark.usefixtures("monkeypatch_check_updates", "monkeypatch_editsettingsdialog")
    def test_check_email_none(self):
        main_window = MainWindow()
        # Check email already called upon MainWindow.__init__
        assert GEMEditor.main.settings.EditSettingsDialog.exec_.called is True
        previous_call_count = GEMEditor.main.settings.EditSettingsDialog.exec_.call_count

        assert QtCore.QSettings().value("Email") is None
        main_window.check_email()
        assert GEMEditor.main.settings.EditSettingsDialog.exec_.call_count == previous_call_count + 1

    @pytest.mark.usefixtures("monkeypatch_check_updates", "monkeypatch_editsettingsdialog", "set_email")
    def test_check_email_set(self):
        main_window = MainWindow()
        # Check email already called upon MainWindow.__init__
        assert GEMEditor.main.settings.EditSettingsDialog.exec_.called is False
        previous_call_count = GEMEditor.main.settings.EditSettingsDialog.exec_.call_count

        assert QtCore.QSettings().value("Email") is not None
        main_window.check_email()
        assert GEMEditor.main.settings.EditSettingsDialog.exec_.call_count == previous_call_count

    @pytest.mark.usefixtures("monkeypatch_about_dialog")
    def test_show_about_dialog(self, main_window):
        assert GEMEditor.main.about.AboutDialog.exec_.called is False
        main_window.showAbout()
        assert GEMEditor.main.about.AboutDialog.exec_.called is True

    @pytest.mark.usefixtures("monkeypatch_QMessageBox_Yes")
    def test_check_model_closing_accept(self, main_window):
        main_window.model = Model()
        assert main_window.check_model_closing() is True

    @pytest.mark.usefixtures("monkeypatch_QMessageBox_No")
    def test_check_model_closing_cancel(self, main_window):
        main_window.model = Model()
        assert main_window.check_model_closing() is False

    def test_close_model_none(self, monkeypatched_close_model):
        main_window = monkeypatched_close_model
        assert main_window.model is None
        assert main_window.closeModel() is True
        assert main_window.save_table_headers.called is False
        assert main_window.modelLoaded.called is False
        assert main_window.set_model.called is False

    @pytest.mark.usefixtures("monkeypatch_QMessageBox_Yes")
    def test_close_model_model_accept(self, monkeypatched_close_model):
        main_window = monkeypatched_close_model
        main_window.model = Model()
        assert main_window.closeModel() is True
        assert main_window.save_table_headers.call_count == 1
        main_window.modelLoaded.assert_called_once_with(False)
        main_window.set_model.assert_called_once_with(None, None)

    @pytest.mark.usefixtures("monkeypatch_QMessageBox_No")
    def test_close_model_model_cancel(self, monkeypatched_close_model):
        main_window = monkeypatched_close_model
        main_window.model = Model()
        assert main_window.closeModel() is False
        assert main_window.save_table_headers.called is False
        assert main_window.modelLoaded.called is False
        assert main_window.set_model.called is False

    @pytest.mark.usefixtures("monkeypatch_editsettingsdialog")
    def test_editsettings_dialog_shown(self, main_window):
        assert GEMEditor.main.settings.EditSettingsDialog.exec_.called is False
        main_window.editSettings()
        assert GEMEditor.main.settings.EditSettingsDialog.exec_.called is True

    @pytest.mark.usefixtures("monkeypatch_setwindowtitle")
    def test_model_loaded(self, main_window):
        model_id = "test_id"
        model = Model(model_id)
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

    def test_set_window_title_none(self, main_window):
        test_title = "XYZ"
        main_window.setWindowTitle(test_title)
        assert main_window.windowTitle() == test_title
        assert main_window.model is None

        main_window.set_window_title()
        assert main_window.windowTitle() == app_name

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

    @pytest.mark.usefixtures("monkeypatch_settings")
    def test_save_table_header(self, main_window):
        assert QtCore.QSettings.setValue.called is False
        assert QtCore.QSettings.sync.called is False
        main_window.save_table_headers()

        assert QtCore.QSettings.setValue.called is True
        assert QtCore.QSettings.setValue.call_count == 5
        assert QtCore.QSettings.sync.called is True
        assert QtCore.QSettings.sync.call_count == 1

    @pytest.mark.usefixtures("monkeypatch_QMessageBox_Yes", "monkeypatch_qdesktopservices_openurl")
    def test_show_new_version_dialog(self, main_window):
        assert QtGui.QDesktopServices.openUrl.called is False
        assert QMessageBox.question.called is False
        main_window.show_newversion_dialog()
        assert QMessageBox.question.called is True
        assert QtGui.QDesktopServices.openUrl.called is True

    @pytest.mark.usefixtures("monkeypatch_QMessageBox_No", "monkeypatch_qdesktopservices_openurl")
    def test_show_new_version_dialog(self, main_window):
        assert QtGui.QDesktopServices.openUrl.called is False
        assert QMessageBox.question.called is False
        main_window.show_newversion_dialog()
        assert QMessageBox.question.called is True
        assert QtGui.QDesktopServices.openUrl.called is False

    @pytest.mark.usefixtures("monkeypatch_editmodeldialog_return_true")
    def test_createmodel_accept_editmodel_dialog(self, main_window):
        main_window.set_model = Mock()
        main_window.modelLoaded = Mock()
        main_window.closeModel = Mock(return_value=True)
        assert GEMEditor.dialogs.model.EditModelDialog.exec_.called is False

        main_window.createModel()
        assert GEMEditor.dialogs.model.EditModelDialog.exec_.called is True
        assert main_window.set_model.called is True
        main_window.modelLoaded.assert_called_once_with(True)

    @pytest.mark.usefixtures("monkeypatch_editmodeldialog_return_false")
    def test_createmodel_cancel_editmodel_dialog(self, main_window):
        main_window.set_model = Mock()
        main_window.modelLoaded = Mock()
        main_window.closeModel = Mock(return_value=True)
        assert GEMEditor.dialogs.model.EditModelDialog.exec_.called is False

        main_window.createModel()
        assert GEMEditor.dialogs.model.EditModelDialog.exec_.called is True
        assert main_window.set_model.called is False
        assert main_window.modelLoaded.called is False

    @pytest.mark.usefixtures("monkeypatch_editmodeldialog_return_false")
    def test_createmodel_cancel_editmodel_dialog(self, main_window):
        main_window.set_model = Mock()
        main_window.modelLoaded = Mock()
        main_window.closeModel = Mock(return_value=False)
        assert GEMEditor.dialogs.model.EditModelDialog.exec_.called is False

        main_window.createModel()
        assert GEMEditor.dialogs.model.EditModelDialog.exec_.called is False
        assert main_window.set_model.called is False
        assert main_window.modelLoaded.called is False

    @pytest.mark.usefixtures("monkeypatch_editmodeldialog_return_true")
    def test_editmodelsettings_cancelled(self, main_window):
        main_window.set_model = Mock()
        main_window.set_window_title = Mock()
        main_window.model = Model("test_id")
        assert main_window.set_model.called is False
        assert main_window.set_window_title.called is False

        main_window.editModelsettings()
        assert main_window.set_model.called is True
        assert main_window.set_window_title.called is True

    @pytest.mark.usefixtures("monkeypatch_editmodeldialog_return_false")
    def test_editmodelsettings_cancelled(self, main_window):
        main_window.set_model = Mock()
        main_window.set_window_title = Mock()
        main_window.model = Model("test_id")
        assert main_window.set_model.called is False
        assert main_window.set_window_title.called is False

        main_window.editModelsettings()
        assert main_window.set_model.called is False
        assert main_window.set_window_title.called is False

    @pytest.mark.usefixtures("monkeypatch_qsettings_complete", "monkeypatch_progress", "mock_read_sbml3",
                             "monkeypatch_getopenfilename_return_empty_string")
    def test_open_model_close_accepted_empty_path(self, main_window):
        main_window.closeModel = Mock(return_value=True)
        main_window.set_model = Mock()
        main_window.modelLoaded = Mock()
        assert QtCore.QSettings.called is False
        main_window.openModel()
        assert QtCore.QSettings.called is True
        assert QFileDialog.getOpenFileName.called is True
        assert GEMEditor.rw.sbml3.read_sbml3_model.called is False
        assert QProgressDialog.called is False

    @pytest.mark.usefixtures("monkeypatch_qsettings_complete", "monkeypatch_progress", "mock_read_sbml3",
                             "monkeypatch_getopenfilename_return_xml_path", "monkeypatch_check_email", "monkeypatch_check_updates")
    def test_open_model_close_accepted_xml_path(self):
        main_window = MainWindow()
        main_window.closeModel = Mock(return_value=True)
        main_window.set_model = Mock()
        main_window.modelLoaded = Mock()
        previous_calls = QtCore.QSettings.call_count
        main_window.openModel()
        assert QtCore.QSettings.call_count == previous_calls + 1
        QtCore.QSettings.return_value.value.assert_called_with("LastPath")
        assert QtCore.QSettings.return_value.setValue.called is True
        assert QFileDialog.getOpenFileName.called is True
        assert QProgressDialog.called is True
        assert QProgressDialog.return_value.close.called is True
        assert GEMEditor.rw.sbml3.read_sbml3_model.called is True
        assert main_window.set_model.called is False
        assert main_window.modelLoaded.called is False

    @pytest.mark.usefixtures("monkeypatch_qsettings_complete", "monkeypatch_progress", "mock_read_sbml3_return_model",
                             "monkeypatch_getopenfilename_return_xml_path", "monkeypatch_check_email", "monkeypatch_check_updates")
    def test_open_model_close_accepted_xml_path2(self):
        main_window = MainWindow()
        main_window.closeModel = Mock(return_value=True)
        main_window.set_model = Mock()
        main_window.modelLoaded = Mock()
        previous_calls = QtCore.QSettings.call_count
        main_window.openModel()
        assert QtCore.QSettings.call_count == previous_calls + 1
        QtCore.QSettings.return_value.value.assert_called_with("LastPath")
        assert QtCore.QSettings.return_value.setValue.called is True
        assert QFileDialog.getOpenFileName.called is True
        assert QProgressDialog.called is True
        assert QProgressDialog.return_value.close.called is True
        assert GEMEditor.rw.sbml3.read_sbml3_model.called is True
        assert main_window.set_model.called is True
        assert main_window.modelLoaded.called is True

    @pytest.mark.usefixtures("monkeypatch_qsettings_complete", "mock_read_sbml3")
    def test_open_model_close_cancelled(self, main_window):
        main_window.closeModel = Mock(return_value=False)
        main_window.openModel()
        assert main_window.closeModel.called is True
        assert GEMEditor.rw.sbml3.read_sbml3_model.called is False

    @pytest.mark.usefixtures("monkeypatch_qsettings_complete", "mock_write_sbml3", "monkeypatch_check_updates",
                             "monkeypatch_check_email", "monkeypatch_getsavefilename_return_empty_string")
    def test_saving_file_user_cancelled(self):
        main_window = MainWindow()

        previous_calls = QtCore.QSettings.call_count
        main_window.saveModel()
        assert QtCore.QSettings.call_count == previous_calls + 1
        QtCore.QSettings.return_value.value.assert_called_with("LastPath")
        assert QFileDialog.getSaveFileName.called is True
        assert GEMEditor.rw.sbml3.write_sbml3_model.called is False
        assert QtCore.QSettings.setValue.called is False

    @pytest.mark.usefixtures("monkeypatch_qsettings_complete", "mock_write_sbml3", "monkeypatch_check_updates",
                             "monkeypatch_check_email", "monkeypatch_getsavefilename_return_xml_path")
    def test_saving_file_user_accepted(self):
        model = Model()
        main_window = MainWindow()
        main_window.model = model

        previous_calls = QtCore.QSettings.call_count
        main_window.saveModel()
        assert QtCore.QSettings.call_count == previous_calls + 1
        QtCore.QSettings.return_value.value.assert_called_with("LastPath")
        assert QFileDialog.getSaveFileName.called is True
        GEMEditor.rw.sbml3.write_sbml3_model.assert_called_with(QFileDialog.getSaveFileName.return_value[0],
                                                                model)
        #QtCore.QSettings.return_value.setValue.assert_called_with("LastPath", os.path.dirname(ecoli_sbml))
        # Todo: Reenable test
