from six.moves.urllib.request import urlopen
from six.moves.urllib.parse import quote_plus

# Mapping between month abbreviations and the numerical month
month_int_mapping = {'': 0,
                     'Jan': 1,
                     'Feb': 2,
                     'Sep': 9,
                     'Oct': 10,
                     'Aug': 8,
                     'Apr': 4,
                     'Jun': 6,
                     'Mar': 3,
                     'Dec': 12,
                     'May': 5,
                     'Jul': 7,
                     'Nov': 11,
                     '01': 1,
                     '02': 2,
                     '03': 3,
                     '04': 4,
                     '05': 5,
                     '06': 6,
                     '07': 7,
                     '08': 8,
                     '09': 9,
                     '10': 10,
                     '11': 11,
                     '12': 12,
                     '1': 1,
                     '2': 2,
                     '3': 3,
                     '4': 4,
                     '5': 5,
                     '6': 6,
                     '7': 7,
                     '8': 8,
                     '9': 9,
                     "10": 10,
                     "11": 11,
                     "12": 12}

# List of all ncbi databases - 2016-02-24
NCBI_DATABASES = {"bioproject": "BioProject",
                  "biosample": "BioSample",
                  "biosystems": "Biosystems",
                  "books": "Books",
                  "cdd": "Conserved Domains",
                  "gap": "dbGaP",
                  "dbvar": "dbVar",
                  "epigenomics": "Epigenomics",
                  "nucest": "EST",
                  "gene": "Gene",
                  "genome": "Genome",
                  "gds": "GEO Datasets",
                  "geoprofiles": "GEO Profiles",
                  "nucgss": "GSS",
                  "homologene": "HomoloGene",
                  "mesh": "MeSH",
                  "toolkit": "NCBI C++ Toolkit",
                  "ncbisearch": "NCBI Web Site",
                  "nlmcatalog": "NLM Catalog",
                  "nuccore": "Nucleotide",
                  "omia": "OMIA",
                  "popset": "PopSet",
                  "probe": "Probe",
                  "protein": "Protein",
                  "proteinclusters": "Protein Clusters",
                  "pcassay": "PubChem BioAssay",
                  "pccompound": "PubChem Compound",
                  "pcsubstance": "PubChem Substance",
                  "pubmed": "PubMed",
                  "pmc": "PubMed Central",
                  "snp": "SNP",
                  "sra": "SRA",
                  "structure": "Structure",
                  "taxonomy": "Taxonomy",
                  "unigene": "UniGene",
                  "unists": "UniSTS"}


def search_ncbi(search_term, email, tool, database="pubmed", retstart=0, retmax=100000):
    """
    Search pubmed using NCBI's eutils API

    Parameters
    ----------
    search_term: Input string - spaces will be replaced by "+"
    email: E-mail addresse
    tool: The name of the tool you are using
    database : A identifier of a NCBI database
    retstart: The start index from which on results will be returned
    retmax: The maximum number of results to be returned

    Returns: A string containing the xml information returned by eutils
    -------
    """
    if database not in NCBI_DATABASES:
        raise ValueError('Unknown NCBI database "{0}"'.format(database))

    search_term = quote_plus(search_term)
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db={database}&term={term}&retstart={retstart}&retmax={retmax}&email={email}&tool={tool}"
    url_data = urlopen(search_url.format(database=database,
                                         tool=tool,
                                         term=search_term,
                                         email=email,
                                         retmax=str(retmax),
                                         retstart=str(retstart)))
    return url_data.read()
