import numpy as np
from GEMEditor.map.base import get_escher_json, MapGraph, add_subnodes
from GEMEditor.base import split_dict_by_value


PARAMS_TURNOVER = {
    "reaction_width": 200,
    "reaction_height": 400,
    "y_margin": 100,
    "x_margin": 100,
    "reaction_x_padding": 100,
    "center_y_padding": 600,
    "met_y_offset": 100}


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


def setup_turnover_map(metabolite, rates, params=PARAMS_TURNOVER):
    graph, pos = layout_turnover(metabolite, rates, params)

    positive, negative, _ = split_dict_by_value(rates)

    return get_escher_json(graph, pos, params)
