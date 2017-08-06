from PyQt5 import QtSql
from PyQt5.QtWidgets import QMessageBox
from GEMEditor.base.dialogs import CustomStandardDialog
from GEMEditor import database_path


class DatabaseSelection(CustomStandardDialog):
    
    def __init__(self):
        super(DatabaseSelection, self).__init__()

        self.database = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.database.setDatabaseName(database_path)
        self.database.setConnectOptions("QSQLITE_OPEN_READONLY=1")

        if not self.database.open():
            QMessageBox.critical(None, self.tr("Cannot open database"),
                                       self.tr("Unable to establish a database connection.\n"
                                                     "Click Cancel to exit."),
                                       QMessageBox.Cancel)
            self.close()

    def closeEvent(self, QCloseEvent):
        """ Close database connection before closing """

        if self.database.isOpen():
            self.database.close()
        QCloseEvent.accept()


class AutoAnnotationSettingsDialog(CustomStandardDialog):

    def __init__(self):
        super(AutoAnnotationSettingsDialog, self).__init__()
