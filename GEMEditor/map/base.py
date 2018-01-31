import json
import escher
import os
import logging
import sys
import networkx
from cobra.core import Metabolite


LOGGER = logging.getLogger(__name__)


ESCHER_OPTIONS_WEB = {"js_source": "web",
                      "menu": "none",
                      "scroll_behavior": "zoom",
                      "html_wrapper": True,
                      "protocol": "https"}

ESCHER_OPTIONS_LOCAL = ESCHER_OPTIONS_WEB.copy()
ESCHER_OPTIONS_LOCAL["js_source"] = "local"


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
        return builder._get_html(**ESCHER_OPTIONS_WEB)

    @property
    def display_path(self):
        if isinstance(self._file_path, str):
            return os.path.basename(self._file_path)
        else:
            return str(self._file_path)

    def __contains__(self, item):
        if hasattr(item, "id"):
            return item.id in self._reaction_ids
        elif isinstance(item, str):
            return item in self._reaction_ids
        else:
            return False


class MapGraph(networkx.Graph):

    def __init__(self, *args, **kwargs):
        super(MapGraph, self).__init__(*args, **kwargs)

    @property
    def reactions(self):
        return set(t[0] for t in self.nodes() if isinstance(t, tuple))


def replace_css_paths(html):
    escher_path = os.path.dirname(escher.__file__)
    full_path = "file://"+escher_path + "/static"
    replaced = html.replace('escher/static', full_path.replace("\\", "/"))
    return replaced


def canvas_size(positions, params):
    """ Calculate the canvas size from node positions

    Parameters
    ----------
    positions: dict,
        Dictionary containg all positions of the nodes
    params: dict,
        Dictionary containing the mapping parameters

    Returns
    -------
    width: float or int,
        Canvas width
    height: float or int,
        Canvas height
    """

    width = max(p[0] for p in positions.values()) + 2 * params["x_margin"]
    height = max(p[1] for p in positions.values()) + 2 * params["y_margin"]
    return width, height


def get_subnodes(reaction):
    """ Get all the subnodes for a reaction

    Parameters
    ----------
    reaction :

    Returns
    -------

    """
    return (reaction, "educts"), (reaction, "middle"), (reaction, "products")


def add_subnodes(graph, reaction):
    """ NetworkX graph

    Parameters
    ----------
    graph: networkx.Graph,
        Graph containing the map nodes
    reaction:
        Reaction to be plotted

    Returns
    -------

    """

    educt_node, middle_node, product_node = get_subnodes(reaction)
    graph.add_nodes_from([educt_node, middle_node, product_node])
    graph.add_edge(educt_node, middle_node)
    graph.add_edge(middle_node, product_node)

    return educt_node, middle_node, product_node


def entry_from_metabolite_node(node, x, y):
    """ Generate a metabolite entry for use in Escher map

    Nodes are expected to be of the form:
    <Metabolite>
    (<Reaction>, <Metabolite>)
    (<Reaction>, "middle")
    (<Reaction>, "educts")
    (<Reaction>, "products")


    Parameters
    ----------
    node: Metabolite or tuple,
        The node for which to generate an entry
    x: float or int,
        x position of the metabolite on the map
    y: float or int,
        y position of the metabolite on the map

    Returns
    -------
    dict,
        Metabolite entry
    """

    entry = {"x": x, "y": y}

    def add_metabolite_info(metabolite, is_primary):
        label_offset = 25 if is_primary else 10
        entry.update({"bigg_id": metabolite.id, "name": metabolite.name,
                      "label_x": x + label_offset, "label_y": y + label_offset,
                      "node_is_primary": is_primary, "node_type": "metabolite"})

    # Add appropriate information
    if isinstance(node, Metabolite):
        add_metabolite_info(node, is_primary=True)
    elif isinstance(node[1], Metabolite):
        add_metabolite_info(node[1], is_primary=False)
    elif node[1] == "middle":
        entry["node_type"] = "midmarker"
    else:
        entry["node_type"] = "multimarker"

    return entry


def entry_from_reaction(graph, reaction, node_index, positions, counter):

    segments = {}
    json_metabolites = []
    educt_node, middle_node, product_node = get_subnodes(reaction)

    # Get the middle node of the reaction
    middle_node_id = node_index[middle_node]
    x, y = positions[middle_node]

    for metabolite, stoichiometry in reaction.metabolites.items():
        json_metabolites.append({"coefficient": stoichiometry, "bigg_id": metabolite.id})

        for node in (metabolite, (reaction, metabolite)):
            for edge in graph.edges([node]):
                node1, node2 = edge
                segments[counter()] = {"from_node_id": node_index[node1], "to_node_id": node_index[node2], "b1": None, "b2": None}

    # Connect intermediate nodes to middle node
    for intermediate_node in (educt_node, product_node):
        if intermediate_node in node_index:
            segments[counter()] = {"from_node_id": node_index[intermediate_node],
                                   "to_node_id": middle_node_id, "b1": None, "b2": None}

    return {"name": reaction.name or reaction.id,
            "bigg_id": reaction.id,
            "reversibility": reaction.lower_bound < 0. < reaction.upper_bound,
            "label_x": x+10,
            "label_y": y+10,
            "gene_reaction_rule": reaction.gene_reaction_rule,
            "genes": [dict([("bigg_id", x.id), ("name", x.name)]) for x in reaction.genes],
            "metabolites": json_metabolites,
            "segments": segments}


def get_escher_json(graph, positions, params):


    # Generate unique numeric ids
    class Counter:

        def __init__(self):
            self.count = -1

        def __call__(self, *args, **kwargs):
            self.count += 1
            return str(self.count)

    counter = Counter()

    result = [{"map_name": "test_name",
               "map_id": "1234565",
               "map_description": "test",
               "homepage": "https://escher.github.io",
               "schema": "https://escher.github.io/escher/jsonschema/1-0-0#"}]

    nodes = {}
    node_index = {}

    for node in graph.nodes():
        index = counter()
        node_index[node] = index

        x, y = positions[node]
        nodes[index] = entry_from_metabolite_node(node, x, y)

    reactions_dict = {}
    for reaction in graph.reactions:
        reactions_dict[counter()] = entry_from_reaction(graph, reaction, node_index, positions, counter)

    width, height = canvas_size(positions, params)
    result.append({"reactions": reactions_dict, "nodes": nodes, "text_labels": {},
                   "canvas": {"x": 0., "y": 0., "width": width, "height": height}})

    return json.dumps(result)
