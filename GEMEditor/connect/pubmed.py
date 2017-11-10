from six.moves.urllib.error import URLError
from six.moves.urllib.request import urlopen
from six.moves.urllib.parse import quote
from lxml import etree as ET
from datetime import datetime as DateTime
from datetime import date as Date
from GEMEditor.data_classes import Reference
from PyQt5 import QtCore
from GEMEditor.connect.ncbi import search_ncbi, month_int_mapping
from GEMEditor.data_classes import Author
from GEMEditor.base.classes import Settings


class Journal:
    """ Journal class storing the journal information provided
    by the pubmed api

    name: str or None
    volume: str or None
    iso: str or None
    issue: str or None
    pubdate: date or None
    issn: str or None
    """


    def __init__(self):
        self.name = None
        self.volume = None
        self.ISO = None
        self.issue = None
        self.pubdate = None
        self.issn = None


class PubmedArticle:
    def __init__(self, pmid=None, pmc=None):
        self.journal = None
        self.date = None
        self.title = None
        self.pagination = None
        self.authors = None
        self.language = None
        self.pubtype = None
        self.pubmodel = None
        self.pubdate = None
        self.pubstatus = None
        self.ids = None
        self._pmid = pmid
        self._pmc = pmc

    @property
    def pmid(self):
        try:
            pubmed_id = self.ids["pubmed"]
        except (KeyError, TypeError):
            return self._pmid
        return pubmed_id

    @pmid.setter
    def pmid(self, pmid):
        self._pmid = pmid

    @property
    def pmc(self):
        try:
            pmc = self.ids["pmc"]
        except (KeyError, TypeError):
            return self._pmid
        return pmc

    @pmc.setter
    def pmc(self, pmc):
        self._pmc = pmc


class RetrievePubmedData(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)

    def __init__(self):
        QtCore.QObject.__init__(self)
        self.pmid = None
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
            self.information = get_pubmed_information(pmid=self.pmid,
                                                      email=email,
                                                      tool=tool)
        except URLError:
            self.error.emit("There appears to be a problem with your internet connection!")
        except (ValueError, TypeError) as e:
            self.error.emit(repr(e))
        self.finished.emit()

    def get_reference(self):
        if self.information is None:
            return None

        try:
            doi = self.information.ids["doi"]
        except KeyError:
            doi = None

        try:
            pmc = self.information.ids["pmc"]
        except KeyError:
            pmc = None

        if self.information.journal.pubdate is not None:
            year = str(self.information.journal.pubdate.year)
        else:
            year = None

        return Reference(authors=self.information.authors,
                         title=self.information.title,
                         journal=self.information.journal.name,
                         abstract="",
                         pmid=self.pmid,
                         doi=doi,
                         pmc=pmc,
                         year=year)

    def set_id(self, pmid):
        self.information = None
        self.pmid = pmid


# Functions for the download and parsing from pubmed
def fetch_pubmed_data(pmid, email, tool):
    """
    Download the information from ncbis eutils and return the raw string

    Parameters
    ----------
    pmid: List of ids or an individual pubmed id
    email: E-mail addresse
    tool: The name of the tool you are using

    Returns: A string containing the information of the ids provided
    -------

    """

    if isinstance(pmid, list):
        search_ids = pmid
    elif isinstance(pmid, str):
        search_ids = [pmid]
    else:
        raise TypeError("Pmid is expected to be an instance of (int, str or list) not {}".format(type(pmid).__name__))

    if search_ids:
        query_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={ids}&email={email}&tool={tool}&retmode=xml"
        url_data = urlopen(query_url.format(tool=tool,
                                            email=email,
                                            ids=",".join(search_ids)))
        return url_data.read()


def get_pubmed_information(pmid, email, tool):
    """
    Convenience function to get pubmed reference data in just one function call

    Parameters
    ----------
    pmid: <int> or <str>
    email: <str>
    tool: <tool>

    Returns
    -------
    """

    raw_data = fetch_pubmed_data(pmid, email, tool)
    if raw_data is None:
        return PubmedArticle(pmid=pmid)

    article_set = ET.fromstring(raw_data)
    if len(article_set) > 1:
        raise ValueError("There are more than 1 articles in the return set!")

    return parse_pubmed_article(article_set.find("PubmedArticle"), pmid=pmid)


def parse_pubmed_search(input_string):
    """
    Parses the xml response of ncbi's eutils API to an esearch request

    Parameters
    ----------

    Returns: A dictionary with the information returned by esearch

    {"ids": list or None,
    "count": int or None,
    "retstart": int or None,
    "retmax": int or None,
    "query_key": str or None,
    "webenv": str or None}

    -------
    """

    # Parse url object to xml tree
    xml_tree = ET.fromstring(input_string)

    # Get the hit count
    xml_count = xml_tree.find("Count")
    try:
        count = int(xml_count.text)
    except AttributeError:
        count = None

    # Get retmax
    xml_retmax = xml_tree.find("RetMax")
    try:
        retmax = int(xml_retmax.text)
    except AttributeError:
        retmax = None

    # Get retstart
    xml_retstart = xml_tree.find("RetStart")
    try:
        retstart = int(xml_retstart.text)
    except AttributeError:
        retstart = None

    xml_querykey = xml_tree.find("QueryKey")
    try:
        query_key = xml_querykey.text
    except AttributeError:
        query_key = None

    xml_webenv = xml_tree.find("WebEnv")
    try:
        webenv = xml_webenv.text
    except AttributeError:
        webenv = None

    xml_idlist = xml_tree.find("IdList")
    if xml_idlist is not None:
        pubmed_ids = [entry.text for entry in xml_idlist.getchildren()]
    else:
        pubmed_ids = None

    return {"ids": pubmed_ids,
            "count": count,
            "retstart": retstart,
            "retmax": retmax,
            "query_key": query_key,
            "webenv": webenv}


def parse_pubmed_article(article, **kwargs):
    """
    Parse the xml information returned by NCBIs eutils api

    Parameters
    ----------
    article: xml node of the article informatino

    Returns
    -------
    PubmedArticle instance combining all information
    """
    if article is None:
        return
    result = PubmedArticle(kwargs)
    parse_medline_citation(article.find("MedlineCitation"), result)
    parse_pubmed_data(article.find("PubmedData"), result)

    return result


def parse_medline_citation(node, result):
    """
    Parse the medline citation part that is part of NCBIs response to eutils API queries.

    Parameters
    ----------
    xml_node: An xml node containing the medline citation

    Returns: Publication intance
                Attributes:
                    .journal - <Journal> or None
                    .pmid - <int> or None
                    .date - <dict> or None
                    .title - <str> or None
                    .pagination - <str> or None
                    .authors - <list> or None
                    .language - <str> or None
                    .pubtype - <list> or None
                    .pubmodel - <str> or None
                    .ids - None
                    .pubstatus - None
                    .pubdate - None
    -------

    """

    if node is None:
        return

    parse_article_node(node.find("Article"), result)


    # Get the dates from medline citation
    dates = {}
    date_created = parse_date_node(node.find("DateCreated"))
    dates["created"] = date_created

    completed_date = parse_date_node(node.find("DateCompleted"))
    dates["completed"] = completed_date

    revised_date = parse_date_node(node.find("DateRevised"))
    dates["revised"] = revised_date

    if any([x is not None for x in dates.values()]):
        result.date = dates
    else:
        result.date = None
    return


def parse_pubmed_data(node, result):
    """
    Parse the PubmedData section of a xml file containing NCBIs pubmed API response

    Parameters
    ----------
    pubmed_data

    Returns: PubmedData object
    -------

    PubmedData attributes:
        .ids:   dict - {type: identifier} e.g. "pubmed": 1123312 or
                None - if no ArticleIdList found

        .pubstatus: str - e.g. "ppublish"
                    None - if no PublicationStatus found

        .pubdate:   dict - {database: DateTime object} e.g. ("medline": DateTime}
                    None - if no History element found
    """
    if node is None:
        return

    result.pubdate = parse_history_node(node.find("History"))
    result.pubstatus = parse_pubstatus_node(node.find("PublicationStatus"))
    result.ids = parse_idlist_node(node.find("ArticleIdList"))
    return


def parse_date_node(node):
    """ Parse the Medline ciation date node

    Parameters
    ----------
    node : Node or None

    Returns
    -------
    date: str or None
    """

    if node is None:
        return None
    temp_dict = {}
    for element in ("Year", "Month", "Day"):
        subnode = node.find(element)
        if subnode is not None:
            if element == "Month":
                temp_dict[element.lower()] = month_int_mapping[subnode.text]
            else:
                temp_dict[element.lower()] = int(subnode.text)
    return Date(**temp_dict)


def parse_author_node(node):
    """ Parse author node of pubmed xml response

    Parameters
    ----------
    node : XML node or None

    Returns
    -------
    result: list or None
    """

    if node is None:
        return

    result = []
    for element in node.getchildren():
        lastname, forename, initials = "", "", ""

        lastname_node = element.find("LastName")
        if lastname_node is not None:
            lastname = lastname_node.text

        forename_node = element.find("ForeName")
        if forename_node is not None:
            forename = forename_node.text

        initials_node = element.find("Initials")
        if initials_node is not None:
            initials = initials_node.text

        result.append(Author(lastname, forename, initials))
    return result


def parse_pubtype_node(node):
    """ Parse the pubtype node

    Parameters
    ----------
    node : XML node or none

    Returns
    -------
    list or None
    """

    if node is None:
        return
    result = []
    for element in node.getchildren():
        ui = element.get("UI")
        text = element.text
        result.append((ui, text))
    return result or None


def parse_pubmedpubdate_node(node):
    """ Parse the pubmedpubdate node of the xml response from pubmed api

    Parameters
    ----------
    node : XML node or None

    Returns
    -------
    status : str or None
    date: date or None
    """

    if node is None:
        return None, None

    status = node.get("PubStatus")

    # Define default values for the date time object
    result = {"year": None,
              "month": 1,
              "day": 1,
              "hour": 0,
              "minute": 0}

    # Replace default values if possible
    for x in ("Year", "Month", "Day", "Hour", "Minute"):
        try:
            result[x.lower()] = int(node.find(x).text)
        except (TypeError, AttributeError, ValueError):
            continue

    if result["year"] is None:
        return status, None
    else:
        return status, DateTime(**result)


def parse_journal_node(node):
    """ Parse the journal node of the xml response of ncbi

    Parameters
    ----------
    node : lxml.Element or None

    Returns
    -------
    result: Journal or None
    """

    if node is None:
        return

    journal = Journal()

    # Process ISSN node
    issn_node = node.find("ISSN")
    if issn_node is not None:
        journal.issn = issn_node.text

    # Process name node
    name_node = node.find("Title")
    if name_node is not None:
        journal.name = name_node.text

    # Process iso abbreviation
    iso_node = node.find("ISOAbbreviation")
    if iso_node is not None:
        journal.ISO = iso_node.text

    # Process issue node
    journal_issue_node = node.find("JournalIssue")
    if journal_issue_node is not None:

        volume_node = journal_issue_node.find("Volume")
        if volume_node is not None:
            journal.volume = volume_node.text

        issue_node = journal_issue_node.find("Issue")
        if issue_node is not None:
            journal.issue = issue_node.text

        pubdate_node = journal_issue_node.find("PubDate")
        if pubdate_node is not None:

            year_node = pubdate_node.find("Year")
            if year_node is None:
                return journal
            year = int(year_node.text)

            month_node = pubdate_node.find("Month")
            if month_node is not None:
                month = month_int_mapping[month_node.text]
            else:
                month = 1

            day_node = pubdate_node.find("Day")
            if day_node is not None:
                day = int(day_node.text)
            else:
                day = 1

            journal.pubdate = Date(year, month, day)

        else:
            journal.pubdate = None

    return journal


def parse_history_node(node):
    """ Parse the history node of a pubmed xml response

    Parameters
    ----------
    node : XML node or None

    Returns
    -------
    pubdate: dict or none
    """
    if node is None:
        return

    pubdate = {}
    for element in node.getchildren():
        status, date = parse_pubmedpubdate_node(element)
        if status is not None and date is not None:
            pubdate[status] = date
    return pubdate or None


def parse_pubstatus_node(node):
    """ Parse pubstatus node

    Parameters
    ----------
    node : XML node or None

    Returns
    -------
    str or None
    """
    if node is not None:
        return node.text


def parse_idlist_node(node):
    """

    Parameters
    ----------
    node : XML node or None

    Returns
    -------
    dict or None
    """
    if node is None:
        return

    id_dict = {}
    for element in node.getchildren():
        id_type = element.get("IdType")
        if id_type is None:
            raise ValueError("IdType not found")
        id_string = element.text
        id_dict[id_type] = id_string
    return id_dict or None


def parse_article_node(node, result):
    """ Parse the article node section

    Parameters
    ----------
    node : XML node or None

    Returns
    -------
    MedlineCitation
    """

    if node is None:
        return result

    result.pubmodel = node.get("PubModel")
    result.journal = parse_journal_node(node.find("Journal"))

    title_node = node.find("ArticleTitle")
    if title_node is not None:
        result.title = title_node.text

    pagination_node = node.find("Pagination")
    if pagination_node is not None:
        medline_pag_node = pagination_node.find("MedlinePgn")
        if medline_pag_node is not None:
            result.pagination = medline_pag_node.text

    abstract_node = node.find("Abstract")
    if abstract_node is not None:
        result.abstract = abstract_node.find("AbstractText").text

    result.authors = parse_author_node(node.find("AuthorList"))

    language_node = node.find("Language")
    if language_node is not None:
        result.language = language_node.text

    pubtype_list = node.find("PublicationTypeList")
    if pubtype_list is not None:
        result.pubtype = parse_pubtype_node(pubtype_list)

    return result
