import pytest
from GEMEditor.cobraClasses import Reaction, Metabolite
from GEMEditor.map.turnover.generate import circular_positions, get_parting_node, filter_dictionary, secondary_position_factor, \
    split_metabolites


@pytest.mark.parametrize("n", (1, 5, 10, 100))
def test_num_of_points(n):
    assert len(list(circular_positions(1, n))) == n


def test_y_equals_zero_for_single_value():
    x_value, y_value = list(circular_positions(1, 1))[0]

    assert x_value == 1
    assert y_value == 0


def test_single_point_with_center():
    center = (30., 30.)
    x_value, y_value = list(circular_positions(1, 1, center))[0]

    assert x_value == 30+1
    assert y_value == 30


@pytest.mark.parametrize("start, end, offset, expected_substrate_node", [((0, 0), (0, 0), 10, (0, 0)),
                                                                         ((0, 0), (10, 10), 0.4, (4, 4)),
                                                                         ((10, 10), (0, 0), 0.4, (6, 6)),
                                                                         ((0, 0), (-10, -10), 0.4, (-4, -4)),
                                                                         ((-10, -10), (0, 0), 0.4, (-6, -6)),
                                                                         ((10, 10), (-10, -10), 0.4, (2, 2)),
                                                                         ((-10, -10), (10, 10), 0.4, (-2, -2))
                                                                         ])
def test_get_parting_node(start, end, offset, expected_substrate_node):
    start_node = get_parting_node(start, end, offset)
    assert start_node == expected_substrate_node


def test_filter_dictionary():

    test = {"a": 1,
            "b": 2,
            "c": 3}

    assert filter_dictionary(test, lambda k, v: v > 1) == {"b": 2, "c": 3}
    assert filter_dictionary(test, lambda k, v: k.startswith("a")) == {"a": 1}
    assert filter_dictionary(test, lambda k, v: False) == {}


def test_secondary_position_factor():

    result = list(secondary_position_factor(4))
    assert len(result) == 4
    assert set(result) == set([-1, 1, -2, 2])


def test_split_metabolites():
    reaction = Reaction("r1")
    metabolite1 = Metabolite("m1")
    metabolite2 = Metabolite("m2")

    reaction.add_metabolites({metabolite1: -1,
                              metabolite2: 1})

    substrates, products = split_metabolites(reaction)
    assert metabolite1 in substrates
    assert substrates[metabolite1] == -1
    assert metabolite2 in products
    assert products[metabolite2] == 1


def test_split_metabolites2():
    reaction = Reaction("r1")
    substrates, products = split_metabolites(reaction)
    assert substrates == {}
    assert products == {}