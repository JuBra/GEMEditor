import pytest
from GEMEditor.model.classes.cobra import Reaction, Metabolite, Gene
from GEMEditor.model.classes.annotation import Annotation
from GEMEditor.widgets.proxymodels import ReactionProxyFilter, reversibility
from GEMEditor.widgets.tables import ReactionTable
from PyQt5.QtWidgets import QApplication

# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestReactionProxyFilter:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.dataTable = ReactionTable()
        self.proxyModel = ReactionProxyFilter()
        self.proxyModel.setSourceModel(self.dataTable)

    @pytest.fixture()
    def boundary_reaction(self):
        reaction = Reaction("r1")
        metabolite = Metabolite("m1")
        reaction.add_metabolites({metabolite: -1})
        return reaction

    @pytest.fixture()
    def normal_reaction(self):
        reaction = Reaction("r1")
        metabolite = Metabolite("m1")
        metabolite2 = Metabolite("m2")
        reaction.add_metabolites({metabolite: -1,
                                  metabolite2: 1})
        return reaction

    @pytest.fixture()
    def transport_reaction(self):
        reaction = Reaction("r1")
        metabolite = Metabolite("m1", compartment="c")
        metabolite2 = Metabolite("m2", compartment="e")
        reaction.add_metabolites({metabolite: -1,
                                  metabolite2: 1})
        return reaction

    def test_set_custom_filter(self):
        assert self.proxyModel.custom_filter == 0

        # Set custom filter number
        self.proxyModel.set_custom_filter(1)

        assert self.proxyModel.custom_filter == 1

    @pytest.mark.parametrize("n, expectation", [(0, True), (1, True), (2, False), (3, False), (4, False)])
    def test_row_accepted_boundary(self, n, expectation, boundary_reaction):

        self.proxyModel.custom_filter = n
        self.dataTable.update_row_from_item(boundary_reaction)

        # Get model index
        index = self.dataTable.item(0, 0).index()
        parent = self.dataTable.parent(index)

        assert self.proxyModel.filterAcceptsRow(0, parent) is expectation
        assert self.proxyModel.passes_custom_filter(boundary_reaction) is expectation

        self.proxyModel.setFilterFixedString("r1")
        assert self.proxyModel.filterAcceptsRow(0, parent) is expectation
        assert self.proxyModel.passes_custom_filter(boundary_reaction) is expectation

        self.proxyModel.setFilterFixedString("xyz")
        assert self.proxyModel.passes_custom_filter(boundary_reaction) is expectation
        assert self.proxyModel.filterAcceptsRow(0, parent) is False

    @pytest.mark.parametrize("n, expectation", [(0, True), (1, False), (2, False), (3, True), (4, True)])
    def test_row_accepted_normal(self, n, expectation, normal_reaction):

        self.proxyModel.custom_filter = n
        self.dataTable.update_row_from_item(normal_reaction)

        # Get model index
        index = self.dataTable.item(0, 0).index()
        parent = self.dataTable.parent(index)

        assert self.proxyModel.filterAcceptsRow(0, parent) is expectation
        assert self.proxyModel.passes_custom_filter(normal_reaction) is expectation

        self.proxyModel.setFilterFixedString("r1")
        assert self.proxyModel.filterAcceptsRow(0, parent) is expectation
        assert self.proxyModel.passes_custom_filter(normal_reaction) is expectation

        self.proxyModel.setFilterFixedString("xyz")
        assert self.proxyModel.filterAcceptsRow(0, parent) is False
        assert self.proxyModel.passes_custom_filter(normal_reaction) is expectation

    @pytest.mark.parametrize("n, expectation", [(0, True), (1, False), (2, True), (3, False), (4, True)])
    def test_row_accepted_transport(self, n, expectation, transport_reaction):

        self.proxyModel.custom_filter = n
        self.dataTable.update_row_from_item(transport_reaction)

        # Get model index
        index = self.dataTable.item(0, 0).index()
        parent = self.dataTable.parent(index)

        assert self.proxyModel.filterAcceptsRow(0, parent) is expectation
        assert self.proxyModel.passes_custom_filter(transport_reaction) is expectation

        self.proxyModel.setFilterFixedString("r1")
        assert self.proxyModel.filterAcceptsRow(0, parent) is expectation
        assert self.proxyModel.passes_custom_filter(transport_reaction) is expectation

        self.proxyModel.setFilterFixedString("xyz")
        assert self.proxyModel.passes_custom_filter(transport_reaction) is expectation
        assert self.proxyModel.filterAcceptsRow(0, parent) is False

    @pytest.mark.parametrize("n, expectation", [(0, True), (1, False), (2, False), (3, False), (4, True)])
    def test_row_accepted_annotated(self, n, expectation, normal_reaction):
        normal_reaction.add_annotation(Annotation("chebi", "CHEBI:5123"))
        self.proxyModel.custom_filter = n
        self.dataTable.update_row_from_item(normal_reaction)

        # Get model index
        index = self.dataTable.item(0, 0).index()
        parent = self.dataTable.parent(index)

        assert self.proxyModel.filterAcceptsRow(0, parent) is expectation
        assert self.proxyModel.passes_custom_filter(normal_reaction) is expectation

        self.proxyModel.setFilterFixedString("r1")
        assert self.proxyModel.filterAcceptsRow(0, parent) is expectation
        assert self.proxyModel.passes_custom_filter(normal_reaction) is expectation

        self.proxyModel.setFilterFixedString("xyz")
        assert self.proxyModel.filterAcceptsRow(0, parent) is False
        assert self.proxyModel.passes_custom_filter(normal_reaction) is expectation

    @pytest.mark.parametrize("n, expectation", [(0, True), (1, False), (2, False), (3, True), (4, False)])
    def test_row_accepted_genes(self, n, expectation, normal_reaction):
        normal_reaction.add_child(Gene())
        self.proxyModel.custom_filter = n
        self.dataTable.update_row_from_item(normal_reaction)

        # Get model index
        index = self.dataTable.item(0, 0).index()
        parent = self.dataTable.parent(index)

        assert self.proxyModel.filterAcceptsRow(0, parent) is expectation
        assert self.proxyModel.passes_custom_filter(normal_reaction) is expectation

        self.proxyModel.setFilterFixedString("r1")
        assert self.proxyModel.filterAcceptsRow(0, parent) is expectation
        assert self.proxyModel.passes_custom_filter(normal_reaction) is expectation

        self.proxyModel.setFilterFixedString("xyz")
        assert self.proxyModel.filterAcceptsRow(0, parent) is False
        assert self.proxyModel.passes_custom_filter(normal_reaction) is expectation

    def test_passes_custom_filter(self):
        """ Should raise not implemented error a number outside of options
        is chosen"""
        self.proxyModel.custom_filter = len(self.proxyModel.options)

        with pytest.raises(NotImplementedError):
            self.proxyModel.passes_custom_filter(Reaction())

class TestMetaboliteProxyFilter:

    def test_filtering(self):
        # Todo: Implement test
        assert True


@pytest.mark.parametrize("lower,upper,expected", [
    (0., 0., None),
    (-5, 5, True),
    (0, 5, False),
    (-5., 0, False),
    (-5, -2, False),
    (2, 5, False)])
def test_reversibility(lower, upper, expected):
    assert reversibility(lower, upper) is expected