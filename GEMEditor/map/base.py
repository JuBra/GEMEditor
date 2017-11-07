import json
import escher
import os
import logging
import sys


LOGGER = logging.getLogger(__name__)


ESCHER_GET_HTML_OPTIONS = {"js_source": "web",
                           "menu": "none",
                           "scroll_behavior": "zoom",
                           "html_wrapper": True,
                           "protocol": "https"}


class WrongEscherFormat(BaseException):

    def __init__(self, *args):
        super(WrongEscherFormat, self).__init__(*args)


class MapWrapper:
    """ Wrapper for loaded map """

    def __init__(self, map_json=None, path=None):
        self._map_json = None
        self._file_path = None
        self._reaction_ids = set()

        self.set_map_json(map_json, path)

    def set_map_json(self, map_json, path):
        """ Set the map json

        Parameters
        ----------
        json: str,  String containing an escher map
        path: str,  Path to the map file

        Returns
        -------
        None
        """

        self._map_json = map_json
        self._file_path = path
        self._parse_json()

    def _parse_json(self):
        """ Parse map json and populate reaction ids

        Returns
        -------

        Raises
        ------
        JSONDecodeError
            If the map json is not a valid JSON file
        WrongEscherFormat
            If there is a problem while parsing JSON
        """

        parsed = json.loads(self._map_json)

        try:
            node = parsed[1]
            reactions_dict = node["reactions"]
            reaction_ids = set(v["bigg_id"] for v in reactions_dict.values())
        except:
            tb = sys.exc_info()[2]
            raise WrongEscherFormat("Error parsing reaction ids").with_traceback(tb)
        else:
            self._reaction_ids = reaction_ids

    def get_html(self, reaction_data=None, gene_data=None, metabolite_data=None):
        """ Generate the html from map

        Parameters
        ----------
        reaction_data: dict
        metabolite_data: dict
        gene_data: dict

        Returns
        -------
        map_html: str
        """
        builder = escher.Builder(map_json=self._map_json,
                                 reaction_data=reaction_data,
                                 gene_data=gene_data,
                                 metabolite_data=metabolite_data)
        return builder._get_html(**ESCHER_GET_HTML_OPTIONS)

    @property
    def display_path(self):
        if isinstance(self._file_path, str):
            return os.path.basename(self._file_path)
        else:
            return str(self._file_path)

    def __contains__(self, item):
        logging.warning(str(self._reaction_ids))
        if hasattr(item, "id"):
            return item.id in self._reaction_ids
        elif isinstance(item, str):
            return item in self._reaction_ids
        else:
            return False
