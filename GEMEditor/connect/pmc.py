from PyQt5 import QtCore
from six.moves.urllib.error import URLError
from six.moves.urllib.request import urlopen
from six.moves.urllib.parse import quote
from GEMEditor.base.classes import Settings
from lxml import etree as ET


class IdConverter(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.identifier = None
        self.idtype = None
        self.information = None

    @QtCore.pyqtSlot()
    def retrieve_data(self):
        settings = Settings()
        email = settings.value("Email")
        tool = quote(settings.applicationName())
        if not email:
            self.error.emit("NCBI requests users of their webservice to identify themselves with an email adress! \n\nPlease set your email in the settings to download data from ncbi!")
            self.finished.emit()
            return

        try:
            self.information = get_mapping(identifier=self.identifier,
                                           idtype=self.idtype,
                                           email=email,
                                           tool=tool)
        except URLError:
            self.error.emit("There appears to be a problem with your internet connection!")
        except (ValueError, TypeError) as e:
            self.error.emit(repr(e))
        self.finished.emit()

    def get_information(self):
        return self.information

    def set_identifier(self, identifier, idtype="pmcid"):
        self.information = None
        self.identifier = identifier
        self.idtype = idtype


def get_mapping(identifier, idtype, email, tool):
    """
    Convenience function to get pubmed reference data in just one function call

    Parameters
    ----------
    identifier: str
    idtype: str
    email: str
    tool: tool

    Returns
    -------
    """

    raw_data = fetch_mapping_data(identifier, idtype, email, tool)
    if raw_data is None:
        return None

    tree = ET.fromstring(raw_data)

    return parse_mapping_xml(tree)


def fetch_mapping_data(identifier, idtype, email, tool):
    """
    Download a mapping between the different identifiers used in pubmed

    Parameters
    ----------
    identifier: Searched identifier
    idtype: idtype
    email: E-mail addresse
    tool: The name of the tool you are using

    Returns: A string containing the information of the xml content
    -------

    """

    query_url = " http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?idtype={idtype}&ids={ids}&email={email}&tool={tool}"
    url_data = urlopen(query_url.format(tool=tool,
                                        email=email,
                                        ids=quote(identifier),
                                        idtype=idtype))
    return url_data.read()


def parse_mapping_xml(node):
    """ Parse the mapping retrieved by tha ncbi id mapping api
    See: http://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/

    Parameters
    ----------
    node : XML node

    Returns
    -------
    result : dict or None
    """

    record_node = node.find("record")

    return {"pmc": record_node.get("pmcid") or None,
            "pmid": record_node.get("pmid") or None,
            "doi": record_node.get("doi") or None}


