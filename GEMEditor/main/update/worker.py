import logging
import json
from PyQt5 import QtCore
from urllib.request import urlopen, URLError, HTTPError
from distutils.version import StrictVersion
from GEMEditor import __versionlookup__, __version__


LOGGER = logging.getLogger(__name__)


class Signals(QtCore.QObject):
    """ Container for signals

    QRunnable is not derived from QObject
    and therefore can not have signals

    """

    new_version = QtCore.pyqtSignal(str)

    def __init__(self):
        super(Signals, self).__init__()


class UpdateCheck(QtCore.QRunnable):
    """ Worker to be run in a QThreadpool

        Checks if a new version of GEMEditor
        is available.

    """

    def __init__(self, *args):
        super(UpdateCheck, self).__init__(*args)
        self.signals = Signals()

    def run(self):
        LOGGER.debug("Checking for updates..")
        # Check if there is a new version
        try:
            request = urlopen(__versionlookup__)
            url_data = request.read().decode('utf-8')
        except HTTPError:
            LOGGER.exception("Check for Update unsuccessful:")
            return
        except URLError:
            LOGGER.debug("Check for updates failed. No internet connection?")
            return

        # Read config file
        try:
            json_data = json.loads(url_data)
        except json.JSONDecodeError:
            LOGGER.exception("Invalid json returned by pypi.")
            return

        # Extract version
        try:
            remote_version = json_data["info"]["version"]
        except:
            LOGGER.exception("Unexpected json structure from pypi.")
            return
        else:
            LOGGER.debug("Remote version: {0!s}".format(remote_version))
            LOGGER.debug("Local version: {0!s}".format(__version__))

        # Compare Versions
        if StrictVersion(remote_version) > StrictVersion(__version__):
            LOGGER.info("A new version is available!")
            self.signals.new_version.emit(remote_version)
        else:
            LOGGER.debug("Installation is up-to-date!")
