import sys
import logging
import platform
import argparse
from PyQt5 import QtWidgets, QtGui, QtCore
from GEMEditor import log_package_versions, LOGGER
from GEMEditor.main import MainWindow


class MainApp(QtWidgets.QApplication):

    def __init__(self, *args):
        super(MainApp, self).__init__(*args)
        self.setOrganizationName("DTU Systemsbiology")
        self.setApplicationName("GEM Editor")
        self.setup_icon()
        LOGGER.debug("Main application setup successful.")

    def setup_icon(self):
        # Application icon in multiple sizes
        icon = QtGui.QIcon()
        for size in (16, 24, 32, 48, 256):
            icon.addFile(':/app_icon{0!s}'.format(size),
                         QtCore.QSize(size, size))
        self.setWindowIcon(icon)

    def exec_(self):
        LOGGER.debug("Executing main application..")
        super(MainApp, self).exec_()


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--debug", action='store_true')
    argparser.add_argument("--file")
    arguments = argparser.parse_args()

    # Check for debug mode
    if arguments.debug:
        log_package_versions()
    else:
        logging.disable(logging.DEBUG)

    # Set up application
    LOGGER.debug("Setting up application..")
    app = MainApp(sys.argv)

    # Setup main window
    mainwindow = MainWindow()
    if arguments.file:
        mainwindow.open_model(filename=arguments.file)
    mainwindow.showMaximized()

    # Execute
    app.exec_()


if __name__ == "__main__":
    # Set application id for windows in order to get right task bar icon
    if platform.system() == "Windows":
        import ctypes

        myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # Run
    main()
    LOGGER.debug("Application closed. Goodbye!")
