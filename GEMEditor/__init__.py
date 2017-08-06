from os.path import join, abspath, dirname, isfile
from PyQt5 import QtCore, QtSql
from PyQt5.QtWidgets import QProgressDialog, QMessageBox
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


def use_database(func):
    """ Decorator for functions using the sqlite database

    Parameters
    ----------
    func :

    Returns
    -------

    """
    def wrapper(*args, **kwargs):
        db = setup_database()

        if db is None:
            return
        elif not db.open():
            QMessageBox.critical(None, "Could not open database",
                                       "There has been an error connecting to the database.\n"
                                       "{}".format(db.lastError().text()),
                                       QMessageBox.Close)
            return

        # Add progress to the positional arguments
        args = args+(db,)
        return_value = func(*args, **kwargs)
        db.close()
        return return_value
    return wrapper


def setup_database():
    """ Open the SQLITE database containing the MetaNetX mappings

    Returns
    -------
    db : QtSql.QSqlDatabase or None
    """

    # Check that SQLITE driver is installed
    if not QtSql.QSqlDatabase.isDriverAvailable('QSQLITE'):
        QMessageBox.critical(None, "Database driver missing!",
                                   "It appears that the sqlite database driver is missing.\n "
                                   "Please install it in order to use this function!",
                                   QMessageBox.Close)
        return

    # Check that the database is found
    if not isfile(database_path):
        QMessageBox.critical(None, "Database not found!",
                                   "The database has not been found at the expected location:"
                                   "\n{}".format(database_path),
                                   QMessageBox.Close)
        return

    # Set up database
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(database_path)
    db.setConnectOptions("QSQLITE_OPEN_READONLY=1")
    return db
