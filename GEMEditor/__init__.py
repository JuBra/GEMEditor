from os.path import join, abspath, dirname, isfile
from PyQt5 import QtCore, QtSql
from PyQt5.QtWidgets import QProgressDialog, QMessageBox
from collections import namedtuple
import re
import configparser

config = configparser.ConfigParser()
config.read(abspath(join(dirname(abspath(__file__)), "GEMEditor.cfg")))

# Set information
__version__ = config.get("DEFAULT", "version")
__versionlookup__ = config.get("DEFAULT", "version_lookup")
__projectpage__ = config.get("DEFAULT", "project_url")

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


# Values stored in settings #

# Version number the user does not want to update to.
# Do not inform the user if the latest version on pypi has this number
VERSION_IGNORED = "IgnoreVersion"


def use_progress(func):
    """ Decorator function to use on methods to display a progress window

    Parameters
    ----------
    func : func

    Returns
    -------
    wrapper : decorated function
    """
    def wrapper(*args, **kwargs):
        progress = QProgressDialog()
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.setAutoClose(False)
        # Add progress to the positional arguments
        args = args+(progress,)
        return_value = func(*args, **kwargs)
        progress.close()
        return return_value
    return wrapper
