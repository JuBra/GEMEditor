from collections import defaultdict


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