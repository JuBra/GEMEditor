from collections import defaultdict
from six import iteritems


def invert_mapping(mapping):
    """ Invert a mapping dictionary

    Parameters
    ----------
    mapping: dict

    Returns
    -------

    """
    inverted_mapping = defaultdict(list)
    for key, value in mapping.items():
        if isinstance(value, (list, set)):
            for element in value:
                inverted_mapping[element].append(key)
        else:
            inverted_mapping[value].append(key)

    return inverted_mapping


def generate_copy_id(base_id, collection, suffix="_copy"):
    """ Generate a new id that is not present in collection

    Parameters
    ----------
    base_id: str, Original id while copying or New for new entries
    collection: dict or list
    suffix: str, Suffix that is added to the base id

    Returns
    -------

    """

    composite_id = str(base_id) + suffix
    new_id = composite_id
    n = 0
    # Make sure there is no metabolite with the same id
    while new_id in collection:
        # Add number to end of id
        n += 1
        new_id = composite_id + str(n)
    return new_id


def get_annotation_to_item_map(list_of_items):
    """ Find model items with overlapping annotations

    Parameters
    ----------
    item
    list_of_items

    Returns
    -------

    """
    annotation_to_item = defaultdict(list)
    for item in list_of_items:
        for annotation in item.annotation:
            annotation_to_item[annotation].append(item)
    return annotation_to_item


def convert_to_bool(input_str):
    """ Convert string of boolean value to actual bolean

    PyQt5 stores boolean values as strings 'true' and 'false
    in the settings. In order to use those stored values
    they need to be converted back to the boolean values.

    Parameters
    ----------
    input_str: str

    Returns
    -------
    bool
    """
    mapping = {"true": True,
               "false": False,
               "none": None}

    if isinstance(input_str, bool):
        return input_str
    elif not isinstance(input_str, str):
        raise TypeError("Input should be a string or boolean")
    else:
        return mapping[input_str.lower()]


def check_charge_balance(metabolites):
    """ Check charge balance of the reaction """
    # Check that charge is set for all metabolites
    if not all(x.charge is not None for x in metabolites.keys()):
        return None
    else:
        return sum([metabolite.charge * coefficient for metabolite, coefficient in iteritems(metabolites)])


def check_element_balance(metabolites):
    """ Check that the reaction is elementally balanced """

    metabolite_elements = defaultdict(int)
    for metabolite, coefficient in iteritems(metabolites):
        for element, count in iteritems(metabolite.elements):
            metabolite_elements[element] += coefficient * count
    return {k: v for k, v in iteritems(metabolite_elements) if v != 0}


def reaction_string(stoichiometry, use_metabolite_names=True):
    """Generate the reaction string """

    attrib = "id"
    if use_metabolite_names:
        attrib = "name"

    educts = [(str(abs(value)), getattr(key, attrib)) for key, value in iteritems(stoichiometry) if value < 0.]
    products = [(str(abs(value)), getattr(key, attrib)) for key, value in iteritems(stoichiometry) if value > 0.]

    return " + ".join([" ".join(x) for x in educts])+" --> "+" + ".join([" ".join(x) for x in products])


def unbalanced_metabolites_to_string(in_dict):
    substrings = ['{0}: {1:.1f}'.format(*x) for x in in_dict.items()]
    return "<br>".join(substrings)


def reaction_balance(metabolites):
    """ Check the balancing status of the stoichiometry

    Parameters
    ----------
    metabolites : dict - Dictionary of metabolites with stoichiometric coefficnets

    Returns
    -------
    charge_str : str or bool
    element_str : str or bool
    balanced : str or bool
    """
    element_result = check_element_balance(metabolites)
    charge_result = check_charge_balance(metabolites)

    if charge_result is None:
        charge_str = "Unknown"
    elif charge_result == 0:
        charge_str = "OK"
    else:
        charge_str = str(charge_result)

    if not all(x.formula for x in metabolites.keys()):
        element_str = "Unknown"
    elif element_result == {}:
        element_str = "OK"
    else:
        element_str = unbalanced_metabolites_to_string(element_result)

    if len(metabolites) < 2:
        balanced = None
    elif element_str == "OK" and charge_str == "OK":
        balanced = True
    elif element_str not in ("OK", "Unknown") or charge_str not in ("OK", "Unknown"):
        balanced = False
    else:
        balanced = "Unknown"

    return charge_str, element_str, balanced


def merge_groups_by_overlap(data):
    """ Merge sets

    Parameters
    ----------
    data: list

    Returns
    -------

    """

    new_index = list(range(len(data)))
    mapping = dict()
    data = [set(m) for m in data]

    # Iterate over groups in data and merge groups
    # to the one with the lowest index
    for i, group in enumerate(data):
        for element in group:
            if element not in mapping:
                # Element has not been seen before
                # point element to current index
                mapping[element] = i
                continue
            else:
                # Get the new location location of the group
                # to which the element mapping points
                destination = new_location(new_index, mapping[element])
                if destination == i:
                    # Group has already been merged
                    continue
                elif destination > i:
                    # Merge to lowest index always
                    destination, i = i, destination

                # Merge current group with the one
                # the item has been found in before
                data[destination].update(data[i])
                data[i] = None
                # Store new index of group
                new_index[i] = destination
                i = destination

    # Filter out the empty groups
    return [g for g in data if g]


def new_location(new_index, n):
    """ Find new location

    Iteratively follow pointers to new location.

    Parameters
    ----------
    new_index: list, Should be initialized from range
    n: int

    Returns
    -------
    int
    """

    while new_index[n] != n:
        n = new_index[n]
    return n


def unpack(iterable, cls):
    """ Unpack the value

    Parameters
    ----------
    iterable
    cls

    Returns
    -------

    """

    if len(iterable) == 1:
        return iterable.pop()
    else:
        return cls(iterable)


def text_is_different(input, state):
    """ Check if the input is different from output

    Test if the input is different to the output
    while ignoring the difference between None
    and empty string.

    Parameters
    ----------
    input: str or None
    state: str

    Returns
    -------
    bool
    """
    if not input and not state:
        return False
    else:
        return input != state


def restore_state(object, state):
    """ Restore the state of an object

    Parameters
    ----------
    object: Object which should be restored
    state: State from settings

    Returns
    -------

    """

    if state:
        object.restoreState(state)


def restore_geometry(object, state):
    """ Restore the geometry of an object

        Parameters
        ----------
        object: Object which should be restored
        state: State from settings

        Returns
        -------

    """

    if state:
        object.restoreGeometry(state)


def split_dict_by_value(dictionary):
    """ Split dictionary by values

    This functions splits dictionary entries based
    on the value into positive, negative and zero
    dictionaries.

    Parameters
    ----------
    dictionary: dict,
        Input dictionary

    Returns
    -------
    positive: dict,
        Dictionary containg all items with positive value
    negative: dict,
        Dictionary cotaining all items with negative value
    zero: dict,
        Dictionary containing all items with zero value
    """

    positive, negative, zero = {}, {}, {}

    for k, v in dictionary.items():
        if v > 0.:
            positive[k] = v
        elif v < 0.:
            negative[k] = v
        else:
            zero[k] = v

    return positive, negative, zero
