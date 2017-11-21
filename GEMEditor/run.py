import sys
import logging
import platform
try:
    from PyQt5 import QtCore, QtGui
except ImportError:
    link = "https://www.riverbankcomputing.com/software/pyqt/download"
    msg = "Please make sure PyQt5 and SIP is installed in order to use this software!\nGet them from: {0}".format(link)
    import webbrowser
    try:
        from tkinter import *
    except ImportError:
        try:
            from Tkinter import *
        except ImportError:
            print(msg)
            webbrowser.open(link)
            sys.exit()
    v = Tk()
    w = Message(v, text=msg)
    w.pack()
    webbrowser.open(link)
    mainloop()
    sys.exit()

from GEMEditor.main import MainWindow
from cobra import __version__ as cobra_version
from GEMEditor import __version__ as gem_version
from escher import __version__ as escher_version
from PyQt5.QtWidgets import QApplication

if platform.system() == "Windows":
    # Set application id for windows in order to get right task bar icon
    import ctypes
    myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


def main(args):
    logger = logging.getLogger("GEMEditor")
    handler = logging.FileHandler("GEMEditor.log", mode="w")
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    logger.addHandler(handler)
    handler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    if not "--debug" in args:
        logging.disable(logging.DEBUG)

    # Log information about system and software used
    logger.info("Operating system: {0!s} {1!s}".format(platform.system(), platform.release()))
    logger.info("Python version: {0!s}".format(sys.version))
    logger.info("GEMEditor version: {0!s}".format(gem_version))
    logger.info("Cobrapy version: {0!s}".format(cobra_version))
    logger.info("Escher version: {0!s}".format(escher_version))

    #Set up application
    logger.debug("Setting up application..")
    app = QApplication(args)
    app.setOrganizationName("DTU Systemsbiology")
    app.setApplicationName("GEM Editor")
    app_icon = QtGui.QIcon()
    app_icon.addFile(':/app_icon16', QtCore.QSize(16, 16))
    app_icon.addFile(':/app_icon24', QtCore.QSize(24, 24))
    app_icon.addFile(':/app_icon32', QtCore.QSize(32, 32))
    app_icon.addFile(':/app_icon48', QtCore.QSize(48, 48))
    app_icon.addFile(':/app_icon256', QtCore.QSize(256, 256))
    app.setWindowIcon(app_icon)
    logger.debug("Application setup successful.")

    # # Setup splashscreen
    # splash = QtGui.QSplashScreen()
    # pixmap = QtGui.QPixmap(":/splashscreen")
    # painter = QtGui.QPainter(pixmap)
    # painter.setPen(QtGui.QPen(QtCore.Qt.darkYellow))
    # painter.setFont(QtGui.QFont("Arial"))
    # painter.drawText(QtCore.QPoint(pixmap.height()-180, pixmap.width()-115), "Version: {0}".format(__version__))
    # splash.setPixmap(pixmap)
    # splash.show()
    # # Prevent python to crash on exit
    # painter.end()

    # Setup main window
    logger.debug("Setting up main window..")
    # Note: Pass in None to avoid error object deletion error when closing
    mainwindow = MainWindow(None)
    mainwindow.showMaximized()
    logger.debug("Mainwindow setup successful.")
    #splash.finish(mainwindow)

    # Execute
    logger.debug("Executing application..")
    app.exec_()
    logger.debug("Appliation closed. Goodbye!")

if __name__ == "__main__":
    main(sys.argv)
