import pandas as pd
from cobra.core import LegacySolution, Solution, Metabolite, Reaction
from GEMEditor.solution.analysis import get_turnover


def test_get_turnover():
    met = Metabolite("m1")
    r1 = Reaction("r1")
    r1.add_metabolites({met: -2})
    r2 = Reaction("r2")
    r2.add_metabolites({met: 1})

    solution = LegacySolution(f=1, x_dict={r1.id: 500, r2.id: 1000})
    assert get_turnover(solution, met) == 1000

    solution = Solution(objective_value=1, status="optimal", reactions=[],
                        fluxes=pd.Series(data=[500, 1000], index=[r1.id, r2.id]))
    assert get_turnover(solution, met) == 1000
