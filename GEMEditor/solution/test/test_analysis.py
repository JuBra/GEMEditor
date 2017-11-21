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
        model = Model("test")
        met1 = Metabolite(id="S7P", formula="C7H15O10P")
        met2 = Metabolite(id="T3P1", formula="C3H7O6P")
        met3 = Metabolite(id="E4P", formula="C4H9O7P")
        met4 = Metabolite(id="F6P", formula="C6H13O9P")
        model.add_metabolites((met1, met2, met3, met4))

        react1 = Reaction(id="r1", name="Transaldolase")
        react1.add_metabolites({met1: -1, met2: -1, met3: 1, met4: 1})

        react2 = Reaction(id="r2")
        react2.add_metabolites({met1: -1})

        react3 = Reaction(id="r3")
        react3.add_metabolites({met2: -1})

        react4 = Reaction(id="r4")
        react4.add_metabolites({met3: -1})

        react5 = Reaction(id="r5")
        react5.add_metabolites({met4: -1})

        model.add_reactions((react1, react2, react3, react4, react5))

        fluxes = {react1.id: 1,
                  react2.id: -1,
                  react3.id: -1,
                  react4.id: 1,
                  react5.id: 1}

        status, yields = get_yields(fluxes, model)
        assert status is True
        assert yields == {"C": {met3: 0.4, met4: 0.6},
                          "H": {met3: 9/22, met4: 13/22},
                          "O": {met3: 7/16, met4: 9/16},
                          "P": {met3: 0.5, met4: 0.5}}

    def test_get_yield_not_working_if_input_formula_missing(self):
        model = Model("test")
        met1 = Metabolite(id="S7P")
        met2 = Metabolite(id="T3P1", formula="C3H7O6P")
        met3 = Metabolite(id="E4P", formula="C4H9O7P")
        met4 = Metabolite(id="F6P", formula="C6H13O9P")
        model.add_metabolites((met1, met2, met3, met4))

        react1 = Reaction(id="r1", name="Transaldolase")
        react1.add_metabolites({met1: -1, met2: -1, met3: 1, met4: 1})

        react2 = Reaction(id="r2")
        react2.add_metabolites({met1: -1})

        react3 = Reaction(id="r3")
        react3.add_metabolites({met2: -1})

        react4 = Reaction(id="r4")
        react4.add_metabolites({met3: -1})

        react5 = Reaction(id="r5")
        react5.add_metabolites({met4: -1})

        model.add_reactions((react1, react2, react3, react4, react5))

        fluxes = {react1.id: 1,
                  react2.id: -1,
                  react3.id: -1,
                  react4.id: 1,
                  react5.id: 1}

        status, _ = get_yields(fluxes, model)
        assert status is False
