from GEMEditor.analysis.formula import *
from GEMEditor.model.classes.cobra import Reaction, Metabolite, Model
from PyQt5.QtWidgets import QApplication

# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


class Test_update_formula_from_neighborhood:

    def test_successful_update(self):
        """ Check that metabolite formula is successfully updated
        from a reaction where all other metabolite formulae are set """

        react = Reaction("rea")
        met1 = Metabolite("met1", formula="C7H8O2")
        met2 = Metabolite("met2", formula="C8H8O4")
        met3 = Metabolite("met3")
        react.add_metabolites({met1: 1,
                               met3: 1,
                               met2: -1})

        result = update_formula_from_neighborhood(met3)

        assert result is True
        assert met3.formula == "CO2"

    def test_no_update_if_boundary(self):
        """ Check that formula is not updated when metabolite is
        part of a boundary reaction """

        react = Reaction("rea")
        met1 = Metabolite("met1")
        react.add_metabolites({met1: -1})

        result = update_formula_from_neighborhood(met1)

        assert result is False
        assert not met1.formula

    def test_no_update_if_mutliple_metabolites_wo_formula(self):
        """ Check that formula is not updated if multiple metabolites
        have no formula set """

        react = Reaction("rea")
        met1 = Metabolite("met1", formula="C7H8O2")
        met2 = Metabolite("met2")
        met3 = Metabolite("met3")
        react.add_metabolites({met1: 1,
                               met3: 1,
                               met2: -1})

        result = update_formula_from_neighborhood(met3)

        assert result is False
        assert not met3.formula

    def test_no_update_for_contradicting_formulae(self):
        """ Check that the formula is not updated if there are
        multiple reactions and the derived formula of those
        are contradicting """

        react = Reaction("rea")  # CO2 expected
        met1 = Metabolite("met1", formula="C7H8O2")
        met2 = Metabolite("met2", formula="C8H8O4")
        met3 = Metabolite("met3")
        react.add_metabolites({met1: 1,
                               met3: 1,
                               met2: -1})

        react1 = Reaction("rea2")  # H2O expected
        met4 = Metabolite("met4", formula="H2O")
        react1.add_metabolites({met3: -1,
                                met4: 1})

        result = update_formula_from_neighborhood(met3)

        assert result is False
        assert not met3.formula


class Test_update_formulae_iteratively:

    def test_update_iteratively(self):
        """ Check that metabolite are successfully
        updated one after another """

        react = Reaction("rea")
        met1 = Metabolite("met1", formula="C7H8O2")
        met2 = Metabolite("met2")
        met3 = Metabolite("met3")  # Update to CO2 in second iteration
        react.add_metabolites({met1: 1,
                               met3: 1,
                               met2: -1})

        react1 = Reaction("rea2")  # Transfer C8H8O4
        met4 = Metabolite("met4", formula="C8H8O4")
        react1.add_metabolites({met2: -1,
                                met4: 1})

        # Setup model
        model = Model("id")
        model.add_metabolites([met1, met2, met3, met4])
        model.add_reactions([react, react1])

        return_value = update_formulae_iteratively(model)

        assert met2.formula == met4.formula
        assert met3.formula == "CO2"
        assert set(return_value) == set([met2, met3])
