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


def metabolite_positions(origin, metabolites, params):
    """ Calculate the positions of the metabolites

    Parameters
    ----------
    origin: np.array,
        Origin of the reaction
    metabolites: iterable,
        Metabolites to position
    params: dict,
        Layout parameters

    Returns
    -------
    positions: list,
        Positions of the metabolites
    """

    n = len(metabolites)

    if not metabolites:
        return []
    elif n == 1:
        return [origin + np.array((params["reaction_width"] / 2, 0))]
    else:
        step = params["reaction_width"] / (n - 1)
        return [origin + i * np.array((step, 0)) for i in range(n)]


def reaction_box_width(n, params):
    """ Calculate the width of the boxes containing reactions

    Parameters
    ----------
    n: int,
        Number of reactions in the box
    params: dict,
        Layout parameters

    Returns
    -------
    float or int,
        Width of the reaction box
    """

    if n == 0:
        return 0
    else:
        width = params["reaction_width"]
        return (n * width) + ((n-1) * params["reaction_x_padding"])


def centering(num_producing, num_consuming, params):
    """ Calculate the centering shift

    Parameters
    ----------
    num_producing: int,
        Number of producing reactions
    num_consuming: int,
        Number of consuming reactions
    params: dict,
        Layout parameters

    Returns
    -------
    np.array,
        Shift of the producing reactions
    np.array,
        Shift of the consuming reactions
    """

    # Calculate the width of the boxes containing reactions
    producing = reaction_box_width(num_producing, params)
    consuming = reaction_box_width(num_consuming, params)

    shift = abs(producing-consuming)/2

    if producing > consuming:
        # Shift consuming
        return np.array((0, 0)), np.array((shift, 0))
    else:
        # Shift producing
        return np.array((shift, 0)), np.array((0, 0))


def add_metabolites(graph, positions, origin, reaction, metabolites, subnode, params):
    """ Add metabolites to graph

    Parameters
    ----------
    graph: MapGraph
        Graph containing map nodes
    positions: dict
        Positions of map nodes
    origin: np.array
        Origin of plotting
    reaction: GEMEditor.main.classes.Reaction
        Reaction of which the metabolites are part of
    metabolites: iterable
        Metabolites to be added
    subnode: tuple
        Reaction subnode to which to connect the metabolite node
    params: dict
        Layout parameters

    """

    met_positions = metabolite_positions(origin, metabolites, params)

    for i, metabolite in enumerate(metabolites):
        node = (reaction, metabolite)
        graph.add_node(node)
        graph.add_edge(subnode, node)
        positions[node] = met_positions[i]


def add_reaction(graph, positions, origin, reaction, metabolite, connect_to_central, params):
    """ Add reaction to graph

    Parameters
    ----------
    graph: MapGraph
        Graph containing map nodes
    positions: dict
        Positions of map nodes
    origin: np.array
        Origin of plotting
    reaction: GEMEditor.main.classes.Reaction
        Reaction to add
    metabolite: GEMEditor.main.classes.Metabolite
        Center metabolite for which the turnover is displayed
    connect_to_central: {'top', 'bottom'}
        Reaction subnode which should be connected to the central metabolite
    params: dict
        Layout parameters

    """

    # Set up reaction nodes
    top_node, middle_node, bottom_node = add_subnodes(graph, reaction)
    top, middle, bottom = middle_node_positions(origin, params)

    positions[top_node] = top
    positions[middle_node] = middle
    positions[bottom_node] = bottom

    # Get metabolites on the same and other side of the equation
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

    # Calculate shift for bottom nodes
    reaction_shift = np.array((0, params["reaction_height"]))

    if connect_to_central == "top":
        # Place metabolites on the same side of the equation on the top side of the reaction
        graph.add_edge(top_node, metabolite)
        add_metabolites(graph, positions, origin, reaction, same.keys(), top_node, params)
        add_metabolites(graph, positions, origin+reaction_shift, reaction, other.keys(), bottom_node, params)
    else:
        # Place metabolites on the same side of the equation on the bottom side of the reaction
        graph.add_edge(bottom_node, metabolite)
        add_metabolites(graph, positions, origin+reaction_shift, reaction, same.keys(), bottom_node, params)
        add_metabolites(graph, positions, origin, reaction, other.keys(), top_node, params)


def margin_shift(params):
    """ Get the shift in positions by margin

    Parameters
    ----------
    params: dict,
        Layout parameters

    Returns
    -------
    np.array,
        Margin shift
    """

    return np.array((params["x_margin"], params["y_margin"]))


def center(n, params):
    """ Get center position

    Parameters
    ----------
    n: int,
        Number of consuming reactions or producing reactions
    params: dict,
        Layout parameters

    Returns
    -------
    np.array,
        Center position

    """

    x_shift = np.array((reaction_box_width(n, params), 0)) / 2
    y_shift = np.array((0, params["reaction_height"] + params["center_y_padding"]))

    return margin_shift(params) + x_shift + y_shift


def layout_turnover(metabolite, rates, params):
    """ Calculate coordinates of the individual nodes

    Parameters
    ----------
    metabolite: GEMEditor.main.classes.Metabolite,
        Metabolite for which to generate the map
    rates: dict,
        Dictionary containing the partial rates of the reactions
    params: dict,
        Layout parameters

    Returns
    -------
    graph: MapGraph,
        Graph containing nodes and edges
    positions: dict,
        Dictionary containing positions of the nodes

    """

    graph = MapGraph()
    positions = {}
    producing, consuming, _ = split_dict_by_value(rates)

    # Calculate the shift from position (0,0)
    margin = margin_shift(params)
    # Calculate centering of reactions
    prod_centering, cons_centering = centering(len(producing), len(consuming), params)
    # Calculate consuming y_offset
    cons_y_offset = np.array((0, 2 * params["center_y_padding"] + params["reaction_height"]))

    positions[metabolite] = center(max(len(producing), len(consuming)), params)

    for i, item in enumerate(sorted(producing.items(), key=lambda x: x[1], reverse=True)):
        origin = margin + prod_centering + prev_reaction_shift(i, params)
        add_reaction(graph, positions, origin, item[0], metabolite, "bottom", params)

    for i, item in enumerate(sorted(consuming.items(), key=lambda x: abs(x[1]), reverse=True)):
        origin = margin + cons_centering + prev_reaction_shift(i, params) + cons_y_offset
        add_reaction(graph, positions, origin, item[0], metabolite, "top", params)

    return graph, {k: tuple(v) for k, v in positions.items()}


def setup_turnover_map(metabolite, rates, params=PARAMS_TURNOVER):
    """ Generate metabolite turnover map

    Parameters
    ----------
    metabolite: GEMEditor.main.classes.Metabolite,
        Metabolite for which to generate the map
    rates: dict,
        Dictionary containing the partial rates of the reactions
    params: dict,
        Layout parameters

    Returns
    -------
    str,
        Escher json string
    """

    graph, pos = layout_turnover(metabolite, rates, params)
    return get_escher_json(graph, pos, params)
