from six.moves.urllib.request import urlopen
from six.moves.urllib.error import URLError
from collections import defaultdict


def get_kegg_compound_data(kegg_id):
    """ Get information on the metabolite from the KEGG database

    Parameters
    ----------
    kegg_id : str

    Returns
    -------

    """
    urldata = urlopen("http://rest.kegg.jp/get/{}".format(kegg_id.strip()))
    if urldata.getcode() != 200:
        raise URLError("Code {}: An error occured while getting information about {}".format(urldata.getcode(), kegg_id))

    return urldata.read().decode("utf-8")


def parse_kegg_compound_info(data):
    """ Parse the information from the KEGG api

    Parameters
    ----------
    data : str

    Returns
    -------

    """
    formula = None
    names = []
    db_links = defaultdict(list)

    current_step = None
    current_db = None

    for line in data.split("\n"):
        split_line = line.split(" ")
        if split_line[0] != "":
            current_step = split_line[0]

        if current_step == "FORMULA":
            formula = split_line[-1]
        elif current_step == "NAME":
            names.append(" ".join(split_line[1:]).strip('" ;'))
        elif current_step == "DBLINKS":
            links = [x for x in split_line[1:] if x != ""]
            if links[0].endswith(":"):
                current_db = links[0].strip(":").lower()
                db_links[current_db].extend(links[1:])
            else:
                db_links[current_db].extend(links)

    return formula, names, db_links


def retrieve_kegg_info(kegg_id):
    """ Retrieve the data for kegg_id from KEGG

    Parameters
    ----------
    kegg_id : str

    Returns
    -------

    """

    data = get_kegg_compound_data(kegg_id)
    return parse_kegg_compound_info(data)