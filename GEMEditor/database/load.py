import logging
import sqlite3
import pandas as pd
from PyQt5 import QtCore


LOGGER = logging.getLogger(__name__)

MNX_SETTINGS = {"sep": "\t", "comment": "#",
                "index_col": False, "dtype": str}

# Resource ids
RES_INCHIS = 16
RES_MNXMET = 1


class ProgressSignals(QtCore.QObject):

    labelChanged = QtCore.pyqtSlot(str)
    valueChanged = QtCore.pyqtSlot(int)
    rangeChanged = QtCore.pyqtSlot(int, int)

    def __init__(self):
        super(ProgressSignals, self).__init__()

    def new_label(self, label):
        LOGGER.debug(label)
        self.labelChanged.emit(label)

    def new_range(self, lower, upper):
        self.rangeChanged.emit(lower, upper)

    def new_value(self, value):
        self.valueChanged.emit(value)


class MetaNetXLoader(QtCore.QRunnable):

    def __init__(self, files, path):
        super(MetaNetXLoader, self).__init__()
        self._files = files
        self._path = path
        self._cancelled = False

        self.signals = ProgressSignals()

    def run(self):
        cnx = sqlite3.connect(self._path)
        self._load_metabolites(cnx)
        cnx.close()

    @QtCore.pyqtSlot()
    def set_cancelled(self):
        self._cancelled = True

    def _load_metabolites(self, cnx):
        """ Load the metabolite entries to database

        Parameters
        ----------
        cnx: sqlite3.Connection
            Connection to the database

        Returns
        -------
        bool:
            True if metabolites were loaded, False otherwise
        """

        if self._cancelled:
            return False

        # Prepare updating
        self.signals.new_label("Parsing MetaNetX metabolites")
        df = pd.read_table(self._files["Metabolites"], **MNX_SETTINGS)
        self.signals.new_range(0, df.shape[0])

        # Load entries
        cursor = cnx.cursor()
        for i, row in enumerate(df.itertuples(index=False)):
            if self._cancelled:
                return False
            else:
                self.signals.new_value(i)

            mnx_id, description, formula, charge, _, inchi, _, _, _ = row
            cursor.execute("INSERT INTO metabolites VALUES (?, ?, ?, ?)", (i, description, formula, charge))
            cursor.execute("INSERT INTO metabolite_ids VALUES (NULL, ?, ?, ?)", (i, RES_MNXMET, mnx_id))
            cursor.execute("INSERT INTO metabolite_names VALUES (NULL, ?, ?)", (i, description))

            if inchi:
                cursor.execute("INSERT INTO metabolite_ids VALUES (NULL, ?, ?, ?)", (i, RES_INCHIS, inchi))

        # Commit entries
        cnx.commit()
