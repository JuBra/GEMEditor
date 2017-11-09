import pytest
from pandas import Series
from ..base import status_objective_from_solution, fluxes_from_solution, shadow_prices_from_solution
from cobra.core import LegacySolution, Solution

@pytest.fixture()
def legacy_solution():
    return LegacySolution(status="optimal", f=0.9, x_dict={"r1": 0.9}, y_dict={"m1": 1})

@pytest.fixture()
def new_solution():
    return Solution(status="optimal", objective_value=0.8, fluxes=Series(data=[0.8], index=["r1"]),
                    shadow_prices=Series(data=[0.7], index=["m1"]))


class TestGetAttributesFromSolution:

    def test_status_objective_from_solution(self, new_solution, legacy_solution):
        status, objective = status_objective_from_solution(new_solution)
        assert status == "optimal"
        assert objective == 0.8

        status, objective = status_objective_from_solution(legacy_solution)
        assert status == "optimal"
        assert objective == 0.9

        with pytest.raises(TypeError):
            status_objective_from_solution(None)

    def test_fluxes_from_solution(self, new_solution, legacy_solution):
        fluxes = fluxes_from_solution(new_solution)
        assert fluxes["r1"] == 0.8

        fluxes = fluxes_from_solution(legacy_solution)
        assert fluxes["r1"] == 0.9

        with pytest.raises(TypeError):
            fluxes_from_solution(None)

    def test_shadowprices_from_solution(self, new_solution, legacy_solution):
        prices = shadow_prices_from_solution(new_solution)
        assert prices["m1"] == 0.7

        prices = shadow_prices_from_solution(legacy_solution)
        assert prices["m1"] == 1

        with pytest.raises(TypeError):
            shadow_prices_from_solution(None)
