from collections import OrderedDict
from PyQt5 import QtCore, QtGui
from GEMEditor.model.display.tables import ReactionBaseTable, GeneTable


class CustomProxy(QtCore.QSortFilterProxyModel):

    def __init__(self, *args, **kwargs):
        super(CustomProxy, self).__init__(*args, **kwargs)

        # Set filter options
        self._options = OrderedDict([("All", lambda *args: True)])
        # Keep track of currently selected filter
        self._filter = self._options["All"]

    def filterAcceptsRow(self, row, index):
        if not self.filterRegExp():
            return self._filter(row, index)
        elif super(CustomProxy, self).filterAcceptsRow(row, index):
            return self._filter(row, index)
        else:
            return False

    @property
    def options(self):
        return self._options.keys()

    @QtCore.pyqtSlot(str)
    def set_filter(self, filter):
        self._filter = self._options[filter]
        self.invalidateFilter()


class CustomSolutionTable(QtGui.QStandardItemModel):

    def __init__(self):
        super(CustomSolutionTable, self).__init__()
        self._model = None
        self._solution = None

    def set_solution(self, model, solution):
        self._model = model
        self._solution = solution
        self._populate_table()

    def _populate_table(self, collection="reactions"):
        self.blockSignals(True)
        self.setRowCount(0)
        for item in getattr(self._model, collection):
            self.appendRow(self.row_factory(item, self._solution))
        self.blockSignals(False)
        self.dataChanged.emit(self.index(0, 0),
                              self.index(self.rowCount()-1,
                                         self.columnCount()-1))
        self.sort(0)

    @staticmethod
    def row_factory(reaction, solution):
        raise NotImplementedError


class FBATable(CustomSolutionTable):
    """ QStandardItemModel used for an FBA solution

    This class is used by the SolutionDialog displaying
    the flux values of the individual reactions

    """

    header = ReactionBaseTable.header + ("Flux",)

    def __init__(self):
        super(FBATable, self).__init__()
        self._col_flux = self.header.index("Flux")
        self._col_lb = self.header.index("Lower Bound")
        self._col_ub = self.header.index("Upper Bound")
        self._col_id = self.header.index("ID")

    @staticmethod
    def row_factory(reaction, solution):
        try:
            value = solution.fluxes[reaction.id]
        except KeyError:
            value = 0
        finally:
            solution_item = QtGui.QStandardItem()
            solution_item.setData(float(value), 2)

        return ReactionBaseTable.row_from_item(reaction)+[solution_item]

    def get_flux(self, row):
        return self.item(row, self._col_flux).data(2)

    def get_reaction(self, row):
        return self.item(row, self._col_id).link

    def get_bounds(self, row):
        return (self.item(row, self._col_lb).data(2),
                self.item(row, self._col_ub).data(2))


class FBAProxy(CustomProxy):
    """ QSortFilterProxyModel to be used in FBA solution dialogs

    This proxy model allows the user to filter for categories
    relevant to FBA solutions.

    """

    def __init__(self, *args, **kwargs):
        super(FBAProxy, self).__init__(*args, **kwargs)

        # Setup filters
        self._options["Nonzero flux"] = self._filter_flux_nonzero
        self._options["Flux at bound"] = self._filter_flux_at_bound
        self._options["All boundaries"] = self._filter_all_boundary
        self._options["Active boundaries"] = self._filter_active_boundary

    def _filter_flux_nonzero(self, row, _):
        return self.sourceModel().get_flux(row) != 0.

    def _filter_flux_at_bound(self, row, _):
        flux = self.sourceModel().get_flux(row)
        return flux in self.sourceModel().get_bounds(row)

    def _filter_all_boundary(self, row, _):
        return self.sourceModel().get_reaction(row).boundary is True

    def _filter_active_boundary(self, *args):
        return self._filter_all_boundary(*args) and \
               self._filter_flux_nonzero(*args)


class FVATable(CustomSolutionTable):
    """ QStandardItemModel used for an FBA solution

    This class is used by the SolutionDialog displaying
    the flux values of the individual reactions

    """

    header = ReactionBaseTable.header + ("Min", "Max", "Range")

    def __init__(self):
        super(FVATable, self).__init__()

        # Column containing the flux value
        self._col_min = self.header.index("Min")
        self._col_max = self.header.index("Max")

    @staticmethod
    def row_factory(reaction, solution):
        """ Get a table row from an entry

        Parameters
        ----------
        entry: tuple,
            Tuple of (reaction, solution)

        Returns
        -------
        list:
            List containing the items to add to the table
        """

        try:
            fva_results = solution.fluxes[reaction.id]
        except KeyError:
            items = [QtGui.QStandardItem("NA")]*3
        else:
            items = [QtGui.QStandardItem()]*3
            items[0].setData(float(fva_results["minimum"]), 2)
            items[1].setData(float(fva_results["maximum"]), 2)
            items[2].setData(float(fva_results["range"]), 2)

        return ReactionBaseTable.row_from_item(reaction) + items

    def get_min_max(self, row):
        return (self.item(row, self._col_min).data(2),
                self.item(row, self._col_max).data(2))


class FVAProxy(CustomProxy):
    """ QSortFilterProxyModel to be used in FVA solution dialogs

    This proxy model allows the user to filter for categories
    relevant to FVA solutions.

    """

    def __init__(self, *args, **kwargs):
        super(FVAProxy, self).__init__(*args, **kwargs)

        # Setup filters
        self._options["Fixed active"] = self._filter_fixed_active
        self._options["Fixed inactive"] = self._filter_fixed_inactive
        self._options["Fixed unidirectional"] = self._filter_fixed_unidirectional

    def _filter_fixed_active(self, row, _):
        min, max = self.sourceModel().get_min_max(row)
        return min == max != 0.

    def _filter_fixed_inactive(self, row, _):
        min, max = self.sourceModel().get_min_max(row)
        return min == max == 0.

    def _filter_fixed_unidirectional(self, row, _):
        min, max = self.sourceModel().get_min_max(row)
        return (min > 0. and max > 0.) or \
               (min < 0. and max < 0.)


class ReactionDeletionTable(CustomSolutionTable):
    """ QStandardItemModel used for displaying gene deletions

    This class is used by the SolutionDialog displaying
    the values of gene deletions

    """

    header = ReactionBaseTable.header + ("ID", "Objective", "Status")

    def __init__(self):
        super(ReactionDeletionTable, self).__init__()
        self._col_objective = self.header.index("Objective")
        self.max_flux = None

    def set_solution(self, model, solution):
        self.max_flux = max(solution["flux"])
        super(ReactionDeletionTable, self).set_solution(model, solution)

    @staticmethod
    def row_factory(reaction, solution):
        return ReactionBaseTable.row_from_item(reaction) + \
               deletion_items(reaction, solution)

    def objective(self, row):
        return self.item(row, self._col_objective).data(2)


class GeneDeletionTable(CustomSolutionTable):

    header = GeneTable.header + ("ID", "Objective", "Status")

    def __init__(self):
        super(GeneDeletionTable, self).__init__()
        self._col_objective = self.header.index("Objective")
        self.max_flux = None

    def set_solution(self, model, solution):
        self.max_flux = max(solution["flux"])
        self._model = model
        self._solution = solution
        self._populate_table("genes")

    @staticmethod
    def row_factory(gene, solution):
        return GeneTable.row_from_item(gene) + \
               deletion_items(gene, solution)

    def objective(self, row):
        return self.item(row, self._col_objective).data(2)


class DeletionProxy(CustomProxy):
    """ QSortFilterProxyModel to be used in deletion solution dialogs

    This proxy model allows the user to filter for categories
    relevant to deletion solutions.

    """

    def __init__(self, *args, **kwargs):
        super(DeletionProxy, self).__init__(*args, **kwargs)

        # Setup options
        self._options["KO phenotype"] = self.filter_ko_phenotype
        self._options["Partial phenotype"] = self.filter_partial_phenotype
        self._options["No phenotype"] = self.filter_no_phenotype

    def filter_ko_phenotype(self, row, _):
        return self.sourceModel().objective(row) == 0.

    def filter_partial_phenotype(self, row, _):
        table = self.sourceModel()
        return 0. < table.objective(row) < table.max_flux

    def filter_no_phenotype(self, row, _):
        table = self.sourceModel()
        return table.objective(row) == table.max_flux


def deletion_items(item, solution):
    try:
        ko_result = solution[item.id]
    except KeyError:
        flux, status = QtGui.QStandardItem("NA"), QtGui.QStandardItem("NA")
    else:
        flux = QtGui.QStandardItem()
        flux.setData(float(ko_result["flux"]), 2)
        status = QtGui.QStandardItem(ko_result["status"])
    return [flux, status]