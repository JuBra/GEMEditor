import logging
from PyQt5 import QtWidgets, QtGui
from GEMEditor.base.classes import ProgressDialog
from GEMEditor.rw.sbml3 import read_sbml3_model
from GEMEditor.rw.ui import Ui_ParserErrorDialog


LOGGER = logging.getLogger(__name__)


class ParserErrorDialog(QtWidgets.QDialog, Ui_ParserErrorDialog):
    """ Dialog showing the errors/warnings during parsing

    Parameters
    ----------
    parser: BaseParser
        Parser containing the error/warning logs

    """

    def __init__(self, parser):
        super(ParserErrorDialog, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Warning")
        self.set_parser(parser)

    def set_parser(self, parser):
        """ Set parser and update tables

        Parameters
        ----------
        parser: BaseParser
            Parser containing the errors/warnings

        """

        # Clear exisitng items
        self.list_errors.clear()
        self.list_warnings.clear()
        for idx in reversed(range(self.tabWidget.count())):
            self.tabWidget.removeTab(idx)

        # Add warnings
        if parser.warnings:
            self.label_icon.setPixmap(QtGui.QPixmap(":/important_yellow"))
            self.list_warnings.addItems(parser.warnings)
            self.tabWidget.addTab(self.tab_warnings,
                                  "Warnings ({0!s})".format(len(parser.warnings)))

        # Add errors
        if parser.errors:
            self.label_icon.setPixmap(QtGui.QPixmap(":/warning"))
            self.list_errors.addItems(parser.errors)
            self.tabWidget.insertTab(0, self.tab_errors,
                                     "Errors ({0!s})".format(len(parser.errors)))

        self.label_message.setText("<b>The following issues have been "
                                   "found while parsing: {}</b>".format(parser.path))


class BaseParser:
    """ Baseclass for model parsers

    Parameters
    ----------
    path: str
        Path to model file

    """

    def __init__(self, path):
        self.path = path
        self._errors = []
        self._warnings = []

    def _parse_file(self, path, progress):
        raise NotImplementedError

    def parse(self):
        """ Parse model from path
        """
        LOGGER.debug("Parsing model: '{0!s}'".format(self.path))
        with ProgressDialog(title="Loading model..") as progress:
            try:
                model = self._parse_file(self.path, progress)
            except:
                import traceback
                self._errors.append(str(traceback.format_exc()))
                return None
            else:
                return model

    @property
    def errors(self):
        return self._errors

    @property
    def warnings(self):
        return self._warnings

    def warn(self, warning):
        """ Keep track of warnings

        Parameters
        ----------
        warning: str
            Message that should be shown to user

        """
        self._warnings.append(warning)


class SBMLParser(BaseParser):

    def __init__(self, *args):
        super(SBMLParser, self).__init__(*args)

    def _parse_file(self, path, progress):
        return read_sbml3_model(path, progress)
