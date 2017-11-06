import logging
from PyQt5 import QtCore
from configparser import ConfigParser
from urllib.request import urlopen, URLError, HTTPError
from distutils.version import StrictVersion
from GEMEditor import __versionlookup__, __version__


LOGGER = logging.getLogger(__name__)


class UpdateCheck(QtCore.QObject):
    """ Check for updates of GEM Editor in a secondary thread to not block gui

        finished is emitted if either the check is done or there has been an error
        new_version is emitted if a new version has been found
    """

    finished = QtCore.pyqtSignal()
    new_version = QtCore.pyqtSignal()

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.current_version = None

    @QtCore.pyqtSlot()
    def check_for_updates(self):
        LOGGER.debug("Checking for updates..")
        # Check if there is a new version
        try:
            url_object = urlopen(__versionlookup__)
        except HTTPError:
            LOGGER.exception("Check for Update unsuccessful:")
            self.finished.emit()
            return
        except URLError:
            LOGGER.debug("Check for updates failed. No internet connection?")
            self.finished.emit()
            return

        # Read config file
        LOGGER.debug("Parsing config file..")
        url_data = url_object.read().decode('utf-8')
        config = ConfigParser()
        config.read_string(url_data)

        # Get version in Git repository
        self.current_version = config.get("DEFAULT", "version")
        LOGGER.debug("Remote version: {0!s}".format(self.current_version))
        LOGGER.debug("Local version: {0!s}".format(__version__))

        if StrictVersion(self.current_version) > StrictVersion(__version__):
            LOGGER.info("A new version is available!")
            self.new_version.emit()
        else:
            LOGGER.debug("Installation is up-to-date!")

        self.finished.emit()
