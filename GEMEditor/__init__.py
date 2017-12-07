import re
import configparser
import logging
import platform
import sys
from cobra import __version__ as cobra_version
from escher import __version__ as escher_version
from pandas import __version__ as pandas_version
from numpy import __version__ as numpy_version
from networkx import __version__ as networkx_version
from sqlalchemy import __version__ as sqlalchemy_version
from lxml.etree import __version__ as lxml_version
from os.path import join, abspath, dirname
from PyQt5 import QtCore
from collections import namedtuple

# Only log versions once
VERSIONS_LOGGED = False

# Setup logger
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')

# Add handlers
file_handler = logging.FileHandler("GEMEditor.log", mode="w", delay=True)
LOGGER.addHandler(file_handler)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
LOGGER.addHandler(stream_handler)
stream_handler.setFormatter(formatter)


# Setup information
config = configparser.ConfigParser()
config.read(abspath(join(dirname(abspath(__file__)), "GEMEditor.cfg")))
__version__ = config.get("DEFAULT", "version")
__versionlookup__ = config.get("DEFAULT", "version_lookup")
__projectpage__ = config.get("DEFAULT", "project_url")
__citation__ = "Brandl J, Andersen MR, unpublished"


database_path = abspath(join(dirname(abspath(__file__)), "database", "modelling.db"))
regex_formula = r"^([A-Z][a-z]?\d*)*$"
formula_validator = re.compile(regex_formula)


GlobalSetting = namedtuple("GlobalSetting", ["string", "default_value"])


# Default program settings #

# Standard prefix for metabolite ids added from the database
DB_NEW_MET_PREFIX = "New"

# Standard prefix for reaction ids added from the database
DB_NEW_REACT_PREFIX = "New"

# Use the name for the new metabolite from database
DB_GET_MET_NAME = True

# Use the name for the new reaction from database
DB_GET_REACT_NAME = True

# Use the formula and charge from the database
DB_GET_FL_AND_CH = True


def log_package_versions():
    """ Log the versions of all dependencies """

    global VERSIONS_LOGGED

    if not VERSIONS_LOGGED:
        # Log information about system and software used
        LOGGER.info("====== VERSION INFO ======")
        LOGGER.info("Operating system: {0!s} {1!s}".format(platform.system(), platform.release()))
        LOGGER.info("Python version: {0!s}".format(sys.version))
        LOGGER.info("GEMEditor version: {0!s}".format(__version__))

        # Log information about dependencies
        packages = {"COBRApy": cobra_version,
                    "Escher": escher_version,
                    "PyQt5": QtCore.PYQT_VERSION_STR,
                    "Pandas": pandas_version,
                    "Numpy": numpy_version,
                    "Networkx": networkx_version,
                    "SQLAlchemy": sqlalchemy_version,
                    "Lxml": lxml_version}

        for pkg, version in sorted(packages.items()):
            LOGGER.info("{0} version: {1!s}".format(pkg, version))

        VERSIONS_LOGGED = True
