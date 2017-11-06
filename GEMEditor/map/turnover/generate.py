import networkx as nx
import numpy as np
from cobra.io import read_sbml_model
from cobra import Metabolite
import json
from escher.validate import validate_map


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


def circular_positions(radius, num_of_points, center=(0, 0)):
    """ Get the coordinates of evenly distributed points on a circle with a fiven radius

    If the center is given, the coordinates are absolute positions, otherwise the coordinates are relative.

    Parameters
    ----------
    radius: float
    num_of_points: int
    center: tuple

    Returns
    -------
    iterator
    """

    if radius <= 0.:
        raise ValueError("The radius needs to be positive!")
    if num_of_points <= 0 or not isinstance(num_of_points, int):
        raise ValueError("The number of points needs to be a positive integer!")

    step_size = 2 * np.pi / num_of_points
    x_offset, y_offset = center

    for i in range(num_of_points):
        yield (np.cos(i*step_size)*radius+x_offset, np.sin(i*step_size)*radius+y_offset)


def get_parting_node(start, end, distance=0.5):
    """ Get the coordinates of a point located in a distance from start between two given coordinates

    Parameters
    ----------
    start: tuple
    end: tuple
    distance: float

    Returns
    -------

    """
    start = np.array(start)
    end = np.array(end)

    return tuple(start + distance * (end-start))


def filter_dictionary(dictionary, filter_condition=lambda *args: True):
    """ Filter dictionary for items that meet a certain condition

    Parameters
    ----------
    dictionary: dict
    filter_condition: function

    Returns
    -------

    """
    return dict((k, v) for k, v in dictionary.items() if filter_condition(k, v))


def secondary_position_factor(num_points):
    """ Return a alternating negative and positive values

    Parameters
    ----------
    num_points

    Returns
    -------

    """

    n = 1
    while n <= num_points:
        return_value = np.ceil(n/2)
        if n % 2 == 0:
            yield -1 * return_value
        else:
            yield return_value
        n += 1


def secondary_positions(start, end, num_positions, distance=0.4, max_distance_from_edge=0.5):
    """ Get positions on a line perpendicular to a vector from start to end

    Calculates a perpendicular vector to the input one.

    Parameters
    ----------
    start: tuple
    end: tuple
    num_positions: int
    distance: float
    max_distance_from_edge: float

    Returns
    -------
    list
    """
    if num_positions <= 0:
        return []

    vector = np.array(end) - np.array(start)
    # Note that the perpendicular vector has the same length as the input vector
    perpendicular_vector = np.array([-vector[1], vector[0]])

    intermediate_node = np.array(get_parting_node(start, end, distance))
    step_length = max_distance_from_edge/(num_positions * 5)

    return [factor * step_length * perpendicular_vector + intermediate_node for factor in secondary_position_factor(num_positions)]


def split_metabolites(reaction):
    """ Split the metabolites of a reaction into substrates and products, based on the stoichiometric coefficient

    Parameters
    ----------
    reaction: GEMEditor.cobraClasses.Reaction

    Returns
    -------
    dict, dict
    """
    substrates = filter_dictionary(reaction.metabolites, lambda k, v: v < 0)
    products = filter_dictionary(reaction.metabolites, lambda k, v: v > 0)
    return substrates, products


def add_standard_nodes_to_graph(graph, reaction):
    substrate, middle, product = get_subnodes(reaction)

    graph.add_nodes_from([substrate, middle, product])
    graph.add_edges_from([(substrate, middle), (middle, product)])

    return substrate, middle, product


def layout_circular(metabolite, reactions, x_dim=20, y_dim=20, cutoff_simplify=10):
    """ Get a circular layout of all reactions that have the metabolite as a participant

    Parameters
    ----------
    metabolite: Metabolite, Metabolite for which to draw the map
    reactions: list or set or dict, Reactions to include in the map
    x_dim: int, Map dimension in x direction
    y_dim: int, Map dimension in y direction
    cutoff_simplify: int,   Reduce map to two nodes per reaction if number of reactions
                            exceeds that number

    Returns
    -------

    """
    # Calculate layout parameters
    center = (x_dim/2, y_dim/2)
    radius = min(x_dim, y_dim) * 0.4
    center_node = metabolite
    positions = {center_node: center}

    # Layout reactions using the graph
    graph = nx.Graph()
    graph.add_node(center_node)
    for reaction, end_position in zip(reactions, circular_positions(radius, len(reactions), center)):

        # Divide metabolites in products and metabolites
        substrates, products = split_metabolites(reaction)
        if metabolite in products:
            substrates, products = products, substrates
        substrates.pop(metabolite)

        # Choose end node for reaction
        if products:
            # Use least connected metabolite as end node
            # This prevents cofactors of being drawn as
            # end nodes.
            end_item = sorted(products.keys(), key=lambda x: len(x.reactions))[0]
            end_node = (reaction, end_item)
            products.pop(end_item)
        else:
            end_node = (reaction, "end")

        # Add end node to graph
        graph.add_node(end_node)
        positions[end_node] = end_position

        # Remove metabolites to draw if the map should be simplified
        if len(reactions) > cutoff_simplify:
            substrates.clear()
            products.clear()

        # Get standard nodes
        substrates_node, middle_node, products_node = get_subnodes(reaction)
        graph.add_node(middle_node)
        positions[middle_node] = get_parting_node(center, end_position)

        # Add substrates if any
        if substrates:
            # Add node
            graph.add_node(substrates_node)
            graph.add_edges_from([(center_node, substrates_node), (substrates_node, middle_node)])
            positions[substrates_node] = get_parting_node(center, end_position, 0.4)

            # Add substrates to graph
            for substrate, metabolite_position in zip(substrates.keys(),
                                                      secondary_positions(center, end_position, len(substrates), 0.3)):
                metabolite_node = (reaction, substrate)
                graph.add_node(metabolite_node)
                positions[metabolite_node] = metabolite_position
                graph.add_edge(metabolite_node, substrates_node)

        else:
            # Do not add any intermediate nodes
            graph.add_edge(center_node, middle_node)

        # Add products if any
        if products:
            graph.add_node(products_node)
            graph.add_edges_from([(middle_node, products_node), (products_node, end_node)])
            positions[products_node] = get_parting_node(center, end_position, 0.6)

            # Add products to graph
            for product, metabolite_position in zip(products.keys(),
                                                    secondary_positions(center, end_position, len(products), 0.7)):
                metabolite_node = (reaction, product)
                graph.add_node(metabolite_node)
                positions[metabolite_node] = metabolite_position
                graph.add_edge(metabolite_node, products_node)

        else:
            # Do not add any intermediate nodes
            graph.add_edge(middle_node, end_node)

    return graph, positions


def layout_reactions(reactions, secondary_metabolites, k=0.1, iterations=50.):
    """ Layout the reactions using the networkx package

    Parameters
    ----------
    reactions : list
    secondary_metabolites : set

    Returns
    -------

    """
    graph = nx.Graph()

    for reaction in reactions:

        # Add one node for products and educts
        educt_node, _, product_node = get_subnodes(reaction)
        graph.add_node(product_node)
        graph.add_node(educt_node)

        graph.add_edge(product_node, educt_node, weight=2)

        for metabolite, stoichiometry in reaction.metabolites.items():
            if metabolite not in secondary_metabolites:
                if stoichiometry > 0.:
                    graph.add_node(metabolite)
                    graph.add_edge(product_node, metabolite, weight=1)
                elif stoichiometry < 0.:
                    graph.add_node(metabolite)
                    graph.add_edge(educt_node, metabolite, weight=1)

    # Get positions
    positions = nx.spring_layout(graph, k=k, iterations=iterations*2)

    # Calculate the middle node
    for reaction in reactions:

        # Calculate the middle position
        educt_node, middle_node, product_node = get_subnodes(reaction)
        positions[middle_node] = (positions[educt_node] + positions[product_node]) / 2
        graph.add_node(middle_node)

        # Remove edge between educt_node and product_node
        graph.remove_edge(educt_node, product_node)

        # Add edges between educt_node, product_node and middle_node
        graph.add_edge(educt_node, middle_node, weight=3)
        graph.add_edge(middle_node, product_node, weight=3)

        # Add secondary metabolites

        for metabolite, stoichiometry in reaction.metabolites.items():
            if metabolite in secondary_metabolites:
                if stoichiometry == 0.:
                    continue
                metabolite_node = (reaction, metabolite)
                if stoichiometry > 0.:
                    graph.add_node(metabolite_node)
                    graph.add_edge(product_node, metabolite_node, weight=2)
                elif stoichiometry < 0.:
                    graph.add_node(metabolite_node)
                    graph.add_edge(educt_node, metabolite_node, weight=2)

    # Calculate final position
    final_positions = nx.spring_layout(graph, pos=positions, fixed=positions.keys(), k=k/3, iterations=iterations)

    return graph, final_positions


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


def get_escher_graph(reactions, graph, final_positions, scaling, x_margin, y_margin):

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
                   "canvas": {"x": 0., "y": 0., "width": 2000, "height": 2000}})
    return result


def setup_map(reactions, cofactors, k=0.1, iterations=30, scaling=3000, x_margin=300, y_margin=300):
    graph, pos = layout_reactions(reactions, cofactors, k, iterations)

    escher_json = get_escher_graph(reactions, graph, pos, scaling, x_margin, y_margin)
    return json.dumps(escher_json)


def setup_turnover_map(metabolite, reactions=()):
    reactions = reactions or metabolite.reactions
    graph, pos = layout_circular(metabolite, reactions, 200, 200)
    escher_json = get_escher_graph(reactions, graph, pos, 10, 0, 0)
    return json.dumps(escher_json)
