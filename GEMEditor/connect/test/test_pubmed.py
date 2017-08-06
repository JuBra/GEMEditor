from datetime import date, datetime

import pytest
from lxml import etree as ET

from GEMEditor.connect.pubmed import parse_pubmed_search, fetch_pubmed_data, parse_pubmed_data, parse_medline_citation, parse_pubmed_article
from GEMEditor.connect.test.examples_pubmed import *
from GEMEditor.connect.pubmed import parse_pubtype_node, parse_pubmedpubdate_node, parse_journal_node, PubmedArticle, \
    parse_author_node


class Test_pubmed_parsing:

    def test_example_input(self):
        parsed = parse_pubmed_search(ex_pubmed_search)
        assert parsed["count"] == 255147
        assert parsed["retmax"] == 20
        assert parsed["retstart"] == 0
        assert parsed["query_key"] == "1"
        assert parsed["webenv"] == "0l93yIkBjmM60UBXuvBvPfBIq8-9nIsldXuMP0hhuMH-8GjCz7F_Dz1XL6z@397033B29A81FB01_0038SID"
        assert parsed["ids"] == ["229486465", "229486321", "229485738"]


    def test_empty_xml(self):
        parsed = parse_pubmed_search("<a></a>")
        assert parsed["count"] is None
        assert parsed["retmax"] is None
        assert parsed["retstart"] is None
        assert parsed["query_key"] is None
        assert parsed["webenv"] is None
        assert parsed["ids"] is None

    def test_empty_IdList(self):
        parsed = parse_pubmed_search("<a><IdList></IdList></a>")
        assert parsed["count"] is None
        assert parsed["retmax"] is None
        assert parsed["retstart"] is None
        assert parsed["query_key"] is None
        assert parsed["webenv"] is None
        assert parsed["ids"] == []


class Test_fetch_pubmed_data:

    def test_empty_list_input(self):
        assert fetch_pubmed_data([], "", "") is None


class Test_parse_medline_citation:

    def test_example_data(self):
        parsed = ET.fromstring(ex_medlineCitation)
        result = PubmedArticle(pmid=11748933)
        parse_medline_citation(parsed, result)

        assert result.date["created"] == date(2001, 12, 25)
        assert result.date["completed"] == date(2002, 3, 4)
        assert result.date["revised"] == date(2006, 11, 15)

        assert result.journal.name == "Cryobiology"
        assert result.journal.ISO == "Cryobiology"
        assert result.journal.volume == "42"
        assert result.journal.issue == "4"
        assert result.journal.pubdate == date(2001, 6, 1)
        assert result.journal.issn == "0011-2240"
        assert result.pubmodel == "Print"
        assert result.title == "Is cryopreservation a homogeneous process? Ultrastructure and motility of untreated, prefreezing, and postthawed spermatozoa of Diplodus puntazzo (Cetti)."
        assert result.pagination == "244-55"
        assert result.abstract == "This study subdivides the cryopreservation procedure for Diplodus puntazzo spermatozoa into three key phases, fresh, prefreezing (samples equilibrated in cryosolutions), and postthawed stages, and examines the ultrastructural anomalies and motility profiles of spermatozoa in each stage, with different cryodiluents. Two simple cryosolutions were evaluated: 0.17 M sodium chloride containing a final concentration of 15% dimethyl sulfoxide (Me(2)SO) (cryosolution A) and 0.1 M sodium citrate containing a final concentration of 10% Me(2)SO (cryosolution B). Ultrastructural anomalies of the plasmatic and nuclear membranes of the sperm head were common and the severity of the cryoinjury differed significantly between the pre- and the postfreezing phases and between the two cryosolutions. In spermatozoa diluted with cryosolution A, during the prefreezing phase, the plasmalemma of 61% of the cells was absent or damaged compared with 24% in the fresh sample (P < 0.001). In spermatozoa diluted with cryosolution B, there was a pronounced increase in the number of cells lacking the head plasmatic membrane from the prefreezing to the postthawed stages (from 32 to 52%, P < 0.01). In both cryosolutions, damages to nuclear membrane were significantly higher after freezing (cryosolution A: 8 to 23%, P < 0.01; cryosolution B: 5 to 38%, P < 0.001). With cryosolution A, the after-activation motility profile confirmed a consistent drop from fresh at the prefreezing stage, whereas freezing and thawing did not affect the motility much further and 50% of the cells were immotile by 60-90 s after activation. With cryosolution B, only the postthawing stage showed a sharp drop of motility profile. This study suggests that the different phases of the cryoprocess should be investigated to better understand the process of sperm damage."
        assert result.authors == [("Taddei", "A R", "AR"), ("Barbato", "F", "F"), ("Abelli", "L", "L"), ("Canese", "S", "S"), ("Moretti", "F", "F"), ("Rana", "K J", "KJ"), ("Fausto", "A M", "AM"), ("Mazzini", "M", "M")]
        assert result.language == "eng"
        assert result.pubtype == [("D016428", "Journal Article"), ("D013485", "Research Support, Non-U.S. Gov't")]

    def test_empty_data(self):
        parsed = ET.fromstring("<a></a>")
        result = PubmedArticle()
        parse_medline_citation(parsed, result)
        assert result.journal is None
        assert result.pmid is None
        assert result.date is None
        assert result.title is None
        assert result.pagination is None
        assert result.authors is None
        assert result.language is None
        assert result.pubtype is None
        assert result.pubmodel is None

    def test_empty_article(self):
        parsed = ET.fromstring("<a><Article PubModel='Test'></Article></a>")
        result = PubmedArticle()
        parse_medline_citation(parsed, result)
        assert result.journal is None
        assert result.pmid is None
        assert result.date is None
        assert result.title is None
        assert result.pagination is None
        assert result.authors is None
        assert result.language is None
        assert result.pubtype is None
        assert result.pubmodel == "Test"


class Test_parse_pubmed_data:

    def test_example_data(self):
        parsed = ET.fromstring(ex_pubmedData)
        result = PubmedArticle()
        parse_pubmed_data(parsed, result)
        assert result.pubdate["pubmed"].isoformat() == "2001-12-26T10:00:00"
        assert result.pubdate["medline"].isoformat() == "2002-03-05T10:01:00"
        assert result.pubdate["entrez"].isoformat() == "2001-12-26T10:00:00"
        assert result.pubstatus == "ppublish"
        assert result.ids["pubmed"] == "11748933"
        assert result.ids["doi"] == "10.1006/cryo.2001.2328"
        assert result.ids["pii"] == "S0011-2240(01)92328-4"

    def test_empty_xml(self):
        xml_data = ET.fromstring("<a></a>")
        result = PubmedArticle()
        parse_pubmed_data(xml_data, result)
        assert result.ids == None
        assert result.pubdate == None
        assert result.pubstatus == None

    def test_empty_elements(self):
        xml_data = ET.fromstring("<a><History></History><PublicationStatus></PublicationStatus><ArticleIdList></ArticleIdList></a>")
        result = PubmedArticle()
        parse_pubmed_data(xml_data, result)
        assert result.ids == None
        assert result.pubdate == None
        assert result.pubstatus == None


class Test_pubmed_article:

    def test_parse_pubmed_article(self):
        parsed = ET.fromstring(ex_pubmed_article)
        result = parse_pubmed_article(parsed)

        # Test Medline Citation part
        assert result.date["created"] == date(2001, 12, 25)
        assert result.date["completed"] == date(2002, 3, 4)
        assert result.date["revised"] == date(2006, 11, 15)

        assert result.pmid == "11748933"
        assert result.journal.name == "Cryobiology"
        assert result.journal.ISO == "Cryobiology"
        assert result.journal.volume == "42"
        assert result.journal.issue == "4"
        assert result.journal.pubdate == date(2001, 6, 1)
        assert result.journal.issn == "0011-2240"
        assert result.pubmodel == "Print"
        assert result.title == "Is cryopreservation a homogeneous process? Ultrastructure and motility of untreated, prefreezing, and postthawed spermatozoa of Diplodus puntazzo (Cetti)."
        assert result.pagination == "244-55"
        assert result.abstract == "This study subdivides the cryopreservation procedure for Diplodus puntazzo spermatozoa into three key phases, fresh, prefreezing (samples equilibrated in cryosolutions), and postthawed stages, and examines the ultrastructural anomalies and motility profiles of spermatozoa in each stage, with different cryodiluents. Two simple cryosolutions were evaluated: 0.17 M sodium chloride containing a final concentration of 15% dimethyl sulfoxide (Me(2)SO) (cryosolution A) and 0.1 M sodium citrate containing a final concentration of 10% Me(2)SO (cryosolution B). Ultrastructural anomalies of the plasmatic and nuclear membranes of the sperm head were common and the severity of the cryoinjury differed significantly between the pre- and the postfreezing phases and between the two cryosolutions. In spermatozoa diluted with cryosolution A, during the prefreezing phase, the plasmalemma of 61% of the cells was absent or damaged compared with 24% in the fresh sample (P < 0.001). In spermatozoa diluted with cryosolution B, there was a pronounced increase in the number of cells lacking the head plasmatic membrane from the prefreezing to the postthawed stages (from 32 to 52%, P < 0.01). In both cryosolutions, damages to nuclear membrane were significantly higher after freezing (cryosolution A: 8 to 23%, P < 0.01; cryosolution B: 5 to 38%, P < 0.001). With cryosolution A, the after-activation motility profile confirmed a consistent drop from fresh at the prefreezing stage, whereas freezing and thawing did not affect the motility much further and 50% of the cells were immotile by 60-90 s after activation. With cryosolution B, only the postthawing stage showed a sharp drop of motility profile. This study suggests that the different phases of the cryoprocess should be investigated to better understand the process of sperm damage."
        assert result.authors == [("Taddei", "A R", "AR"), ("Barbato", "F", "F"), ("Abelli", "L", "L"), ("Canese", "S", "S"), ("Moretti", "F", "F"), ("Rana", "K J", "KJ"), ("Fausto", "A M", "AM"), ("Mazzini", "M", "M")]
        assert result.language == "eng"
        assert result.pubtype == [("D016428", "Journal Article"), ("D013485", "Research Support, Non-U.S. Gov't")]

        # Test Pubmed Data part
        assert result.pubdate["pubmed"].isoformat() == "2001-12-26T10:00:00"
        assert result.pubdate["medline"].isoformat() == "2002-03-05T10:01:00"
        assert result.pubdate["entrez"].isoformat() == "2001-12-26T10:00:00"
        assert result.pubstatus == "ppublish"
        assert result.ids["pubmed"] == "11748933"
        assert result.ids["doi"] == "10.1006/cryo.2001.2328"
        assert result.ids["pii"] == "S0011-2240(01)92328-4"


def test_valid_example():
    node = ET.fromstring(ex_pubtype)

    result = parse_pubtype_node(node)
    assert result[0] == ("D016428", "Journal Article")
    assert result[1] == ("D013485", "Research Support, Non-U.S. Gov't")


def test_parse_pubmedpubdate_node1():
    """ Test the parsing of pubmedpubdate nodes """
    node = ET.fromstring(ex_pubmedpubdate)
    status, date = parse_pubmedpubdate_node(node)
    assert status == "pubmed"
    assert date == datetime(2001, 12, 26, 10, 0)


def test_parse_pubmedpubdate_node2():
    """ Test the parsing of pubmedpubdate node without day and hour"""
    node = ET.fromstring(ex_pubmedpubdate2)
    status, date = parse_pubmedpubdate_node(node)
    assert status == "pubmed"
    assert date == datetime(1975, 4, 1, 0, 0)


def test_parse_pubmedpubdate_node3():
    """ Test the parsing of pubmedpubdate node without day and hour"""
    node = ET.fromstring(ex_pubmedpubdate3)
    status, date = parse_pubmedpubdate_node(node)
    assert status == "ecollection"
    assert date == datetime(2016, 1, 1, 0, 0)


def test_parse_journal_node1():
    """ Test valid example 1"""
    node = ET.fromstring(ex_journal_node1)
    journal = parse_journal_node(node)
    assert journal.issn == "0003-9950"
    assert journal.issue == "3"
    assert journal.volume == "93"
    assert journal.pubdate == date(1975, 3, 1)
    assert journal.name == "Archives of ophthalmology (Chicago, Ill. : 1960)"
    assert journal.ISO == "Arch. Ophthalmol."


def test_parse_journal_node2():
    """ Test valid example 2"""
    node = ET.fromstring(ex_journal_node2)
    journal = parse_journal_node(node)
    assert journal.issn == "0011-2240"
    assert journal.issue == "4"
    assert journal.volume == "42"
    assert journal.pubdate == date(2001, 6, 1)
    assert journal.name == "Cryobiology"
    assert journal.ISO == "Cryobiology"


def test_parse_journal_node3():
    """ Test valid example 2"""
    node = ET.fromstring(ex_journal_node3)
    journal = parse_journal_node(node)
    assert journal.issn == "0514-7484"
    assert journal.issue == "2"
    assert journal.volume == "16"
    assert journal.pubdate == date(1976, 1, 1)
    assert journal.name == "Zhurnal eksperimental'noĭ i klinicheskoĭ meditsiny"
    assert journal.ISO == "Zh Eksp Klin Med"


def test_parse_journal_node4():
    """ Test valid example 2"""
    node = ET.fromstring(ex_journal_node4)
    journal = parse_journal_node(node)
    assert journal.issn == "0132-8867"
    assert journal.issue == "5"
    assert journal.volume == None
    assert journal.pubdate == None
    assert journal.name == "Zdravookhranenie Kirgizii"
    assert journal.ISO == "Zdravookhr Kirg"


def test_parse_author_node():
    """ Test author node where part of the
    name, forename, initials is missing """
    node = ET.fromstring(ex_author_missing_information)
    authors = parse_author_node(node)

    assert len(authors) == 6
    author1 = authors[0]
    assert author1.lastname == "Ahmad"
    assert author1.firstname == "Malik Shoaib"
    assert author1.initials == "MS"

    author2 = authors[1]
    assert author2.lastname == "Zafar"
    assert author2.firstname == "Salman"
    assert author2.initials == "S"

    author3 = authors[2]
    assert author3.lastname == "Yousuf"
    assert author3.firstname == "Sammar"
    assert author3.initials == "S"

    author4 = authors[3]
    assert author4.lastname == "Atia-Tul-Wahab"
    assert author4.firstname == ""
    assert author4.initials == ""

    author5 = authors[4]
    assert author5.lastname == "Atta-Ur-Rahman"
    assert author5.firstname == ""
    assert author5.initials == ""

    author6 = authors[5]
    assert author6.lastname == "Choudhary"
    assert author6.firstname == "M Iqbal"
    assert author6.initials == "MI"
