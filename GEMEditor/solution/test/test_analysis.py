import pandas as pd
from PyQt5.QtWidgets import QApplication
from cobra.core import LegacySolution, Solution, Metabolite, Reaction
from GEMEditor.solution.analysis import get_turnover, get_yields
from GEMEditor.model.classes import Model, Reaction, Metabolite

# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


def test_get_turnover():
    met = Metabolite("m1")
    r1 = Reaction("r1")
    r1.add_metabolites({met: -2})
    r2 = Reaction("r2")
    r2.add_metabolites({met: 1})

    solution = LegacySolution(f=1, x_dict={r1.id: 500, r2.id: 1000})
    assert get_turnover(solution, met) == 1000

    solution = Solution(objective_value=1, status="optimal",
                        fluxes=pd.Series(data=[500, 1000], index=[r1.id, r2.id]))
    assert get_turnover(solution, met) == 1000


class TestGetYields:

    def test_get_yield(self):
        model = Model("model")
        met1 = Metabolite("m1", formula="H2O")
        met2 = Metabolite("m2", formula="O2")
        met3 = Metabolite("m3", formula="H2O2")

        model.add_metabolites((met1, met2, met3))

        react1 = Reaction("r1")
        react1.add_metabolites({met1: -1})

        react2 = Reaction("r2")
        react2.add_metabolites({met2: -1})

        react3 = Reaction("r3")
        react3.add_metabolites({met1: -2,
                                met2: -1,
                                met3: 2})

        react4 = Reaction("r4")
        react4.add_metabolites({met3: -1})

        model.add_reactions((react1, react2, react3, react4))

        fluxes = {react1.id: -10,
                  react2.id: -5,
                  react3.id: 5,
                  react4.id: 10}

        status, yields = get_yields(fluxes, model)

        assert status is True
        assert yields == {"H": {met3: 1.}, "O": {met3: 1.}}
