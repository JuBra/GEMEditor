import networkx as nx
import numpy as np
from cobra import Metabolite
import json
from GEMEditor.base import split_dict_by_value


PARAMS_TURNOVER = {
    "reaction_width": 200,
    "reaction_height": 400,
    "y_margin": 100,
    "x_margin": 100,
    "reaction_x_padding": 100,
    "center_y_padding": 600,
    "met_y_offset": 100}


class MapGraph(nx.Graph):

    def __init__(self, *args, **kwargs):
        super(MapGraph, self).__init__(*args, **kwargs)

    @property
    def reactions(self):
        return set(t[0] for t in self.nodes() if isinstance(t, tuple))


def get_subnodes(reaction):
    """ Get all the subnodes for a reaction

    Parameters
    ----------
    reaction :

    Returns
    -------

    """
    return (reaction, "educts"), (reaction, "middle"), (reaction, "products")


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


def prev_reaction_shift(n, params):
    """ Calculate position of the reaction

    Parameters
    ----------
    n: int,
        Index of the reaction
    params: dict,
        Plotting parameters


    Returns
    -------
    np.array:
        Shift of the current reaction
    """

    if n == 0:
        return np.array((0, 0))
    else:
        total_width = params["reaction_width"] + params["reaction_x_padding"]
        return np.array((n * total_width, 0.))


def middle_node_positions(origin, params):
    """ Calculate positions of the middle nodes

    Parameters
    ----------
    origin: np.array,
        Origin of the reaction
    params: dict,
        Plotting parameters

    Returns
    -------

    """

    met_y_offset = params["met_y_offset"]
    width = params["reaction_width"]
    height = params["reaction_height"]

    top = origin + np.array((width/2, met_y_offset))
    bottom = origin + np.array((width/2, height - met_y_offset))
    middle = top + (bottom - top) / 2

    return top, middle, bottom


def metabolite_positions(origin, n, params):

    positions = []

    if n == 0:
        pass
    elif n == 1:
        positions.append(origin + np.array((params["reaction_width"] / 2, 0)))
    else:
        step = params["reaction_width"] / (n - 1)
        for i in range(n):
            positions.append(origin + i * np.array((step, 0)))

    return positions


def total_width_reactions(n, params):

    if n == 0:
        return 0
    else:
        width = params["reaction_width"]
        return (n * width) + ((n-1) * params["reaction_x_padding"])


def centering_shift(num_producing, num_consuming, params):

    width_producing = total_width_reactions(num_producing, params)
    width_consuming = total_width_reactions(num_consuming, params)

    shift = abs(width_producing-width_consuming)/2

    if width_producing > width_consuming:
        # Shift consuming
        return np.array((0, 0)), np.array((shift, 0))
    else:
        # Shift producing
        return np.array((shift, 0)), np.array((0, 0))


def add_metabolites(graph, positions, origin, reaction, metabolites, subnode, params):

    met_positions = metabolite_positions(origin, len(metabolites), params)

    for i, m in enumerate(metabolites):
        node = (reaction, m)
        graph.add_node(node)
        graph.add_edge(subnode, node)
        positions[node] = met_positions[i]


def add_reaction(graph, positions, origin, reaction, metabolite, met_connection_node, params):

    top_node, middle_node, bottom_node = add_subnodes(graph, reaction)
    top, middle, bottom = middle_node_positions(origin, params)

    positions[top_node] = top
    positions[middle_node] = middle
    positions[bottom_node] = bottom

    products, educts, _ = split_dict_by_value(reaction.metabolites)

    if metabolite in products:
        products.pop(metabolite)
        same, other = products, educts
    else:
        educts.pop(metabolite)
        same, other = educts, products

    # Add nodes to graph
    for m in reaction.metabolites.keys():
        if m is metabolite:
            continue
        graph.add_node((reaction, m))

    reaction_shift = np.array((0, params["reaction_height"]))

    if met_connection_node == "top":
        graph.add_edge(top_node, metabolite)
        add_metabolites(graph, positions, origin, reaction, same.keys(), top_node, params)
        add_metabolites(graph, positions, origin+reaction_shift, reaction, other.keys(), bottom_node, params)
    else:
        graph.add_edge(bottom_node, metabolite)
        add_metabolites(graph, positions, origin+reaction_shift, reaction, same.keys(), bottom_node, params)
        add_metabolites(graph, positions, origin, reaction, other.keys(), top_node, params)


def get_margin_shift(params):
    return np.array((params["x_margin"], params["y_margin"]))


def position_center(n, params):
    x_shift = np.array((total_width_reactions(n, params), 0)) / 2
    y_shift = np.array((0, params["reaction_height"] + params["center_y_padding"]))

    return get_margin_shift(params) + x_shift + y_shift


def layout_turnover(metabolite, rates, params):

    graph = MapGraph()
    positions = {}

    producing, consuming, _ = split_dict_by_value(rates)

    margin_shift = get_margin_shift(params)
    prod_x_shift, cons_x_shift = centering_shift(len(producing), len(consuming), params)
    cons_y_shift = np.array((0, 2 * params["center_y_padding"] + params["reaction_height"]))

    positions[metabolite] = position_center(max(len(producing), len(consuming)), params)

    for i, item in enumerate(sorted(producing.items(), key=lambda x: x[1], reverse=True)):
        origin = margin_shift + prod_x_shift + prev_reaction_shift(i, params)
        add_reaction(graph, positions, origin, item[0], metabolite, "bottom", params)

    for i, item in enumerate(sorted(consuming.items(), key=lambda x: abs(x[1]), reverse=True)):
        origin = margin_shift + cons_x_shift + prev_reaction_shift(i, params) + cons_y_shift
        add_reaction(graph, positions, origin, item[0], metabolite, "top", params)

    return graph, {k: tuple(v) for k, v in positions.items()}


def canvas_size(pos, params):
    width = max(p[0] for p in pos.values()) + 2 * params["x_margin"]
    height = max(p[1] for p in pos.values()) + 2 * params["y_margin"]
    return width, height


def setup_turnover_map(metabolite, rates, params=PARAMS_TURNOVER):
    graph, pos = layout_turnover(metabolite, rates, params)

    positive, negative, _ = split_dict_by_value(rates)

    return get_escher_json(graph, pos, params)
