import networkx as nx
import numpy as np
from cobra import Metabolite
import json
from GEMEditor.solution.analysis import get_rates
from GEMEditor.base import split_dict_by_value


params = {
    "reaction_width": 10,
    "reaction_height": 30,
    "y_margin": 10,
    "x_margin": 10,
    "reaction_x_padding": 10,
    "center_y_padding": 20,
    "met_y_offset": 10}


class Counter:

    def __init__(self):
        self.count = -1

    def __call__(self, *args, **kwargs):
        self.count += 1
        return str(self.count)

counter = Counter()


def get_subnodes(reaction):
    """ Get all the subnodes for a reaction

    Parameters
    ----------
    reaction :

    Returns
    -------

    """
    return (reaction, "educts"), (reaction, "middle"), (reaction, "products")


def entry_from_metabolite(metabolite, position, scaling=1, x_margin=0, y_margin=0, is_primary=False):
    x = position[0] * scaling + x_margin
    y = position[1] * scaling + y_margin
    label_offset = 25 if is_primary else 10
    return {"node_type": "metabolite",
            "x": x,
            "y": y,
            "bigg_id": metabolite.id,
            "name": metabolite.name,
            "label_x": x+label_offset,
            "label_y": y+label_offset,
            "node_is_primary": is_primary}


def entry_from_reaction(graph, reaction, node_index, positions, scaling, x_margin, y_margin):

    segments = {}
    json_metabolites = []
    educt_node, middle_node, product_node = get_subnodes(reaction)

    # Get the middle node of the reaction
    middle_node_id = node_index[middle_node]
    mid_pos = positions[middle_node]
    x = mid_pos[0] * scaling + x_margin
    y = mid_pos[1] * scaling + y_margin

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


def get_escher_graph(reactions, graph, final_positions, scaling=1, x_margin=0, y_margin=0, canvas_width=2000, canvas_height=2000):

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

        pos = final_positions[node]
        x = pos[0] * scaling + x_margin
        y = pos[1] * scaling + y_margin
        if isinstance(node, Metabolite):
            entry = entry_from_metabolite(node, final_positions[node], scaling, x_margin, y_margin, is_primary=True)
        elif isinstance(node[1], Metabolite):
            entry = entry_from_metabolite(node[1], final_positions[node], scaling, x_margin, y_margin, is_primary=False)
        elif node[1] == "middle":
            entry = {"node_type": "midmarker",
                     "x": x,
                     "y": y}
        else:
            entry = {"node_type": "multimarker",
                     "x": x,
                     "y": y}
        nodes[index] = entry

    reactions_dict = {}
    for reaction in reactions:
        reactions_dict[counter()] = entry_from_reaction(graph, reaction, node_index, final_positions, scaling, x_margin, y_margin)

    result.append({"reactions": reactions_dict,
                   "nodes": nodes,
                   "text_labels": {},
                   "canvas": {"x": 0., "y": 0., "width": canvas_width, "height": canvas_height}})
    return result


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
        return n * width + (n-1) * params["reaction_x_padding"]


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

    graph = nx.Graph()
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


def canvas_size(max_num_reactions, params):
    width = total_width_reactions(max_num_reactions, params) + 2 * params["x_margin"]
    height = 2 * (params["y_margin"] + params["reaction_height"] + params["center_y_padding"])

    return width, height


def setup_turnover_map(metabolite, fluxes):

    rates = get_rates(fluxes, metabolite)
    reactions = [r for r, v in rates.items() if v != 0.]
    graph, pos = layout_turnover(metabolite, rates, params)

    consuming = sum(1 for v in rates.values() if v > -1)

    width, height = canvas_size(max(consuming, len(reactions) - consuming), params)

    escher_json = get_escher_graph(reactions, graph, pos, 10, 0, 0, width * 2.2, height * 10)
    return json.dumps(escher_json)
