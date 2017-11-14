from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QSortFilterProxyModel


def reversibility(lower, upper):
    if lower == 0. and upper == 0.:
        return None
    elif lower >= 0 and upper >= 0 or lower <= 0 and upper <= 0:
        return False
    else:
        return True


def metabolite_is_dead_end(metabolite):
    # Return True if there are less than 2 reactions as a metabolite
    # can't be consumed and produced by a single reaction
    if len(metabolite.reactions) < 2:
        return True
    else:
        consuming, producing = set(), set()
        for r in metabolite.reactions:
            coeff = r.metabolites[metabolite]
            for x in (r.upper_bound * coeff, r.lower_bound * coeff):
                if x < 0:
                    consuming.add(r)
                elif x > 0:
                    producing.add(r)
            # No Dead-End if the metabolite can be produced by at least one and consumed
            # by at least one reaction
            # If the reactions in producing and consuming are the same reactions,
            # check that there are at least 2 reactions.
            if producing and consuming and (producing != consuming or len(producing) > 1):
                return False
        return True


class CustomSortFilterProxyModel(QSortFilterProxyModel):

    def __init__(self, *args, **kwargs):
        super(CustomSortFilterProxyModel, self).__init__(*args, **kwargs)
        self.custom_filter = 0

    def filterAcceptsRow(self, p_int, QModelIndex):
        item = self.sourceModel().item(p_int, 0).link
        if self.filterRegExp():
            return (self.passes_custom_filter(item) and
                    super(CustomSortFilterProxyModel, self).filterAcceptsRow(p_int, QModelIndex))
        else:
            return self.passes_custom_filter(item)

    def passes_custom_filter(self, item):
        raise NotImplementedError

    @QtCore.pyqtSlot(int)
    def set_custom_filter(self, n):
        self.custom_filter = n
        self.invalidateFilter()

    def setSourceModel(self, QAbstractItemModel):
        super(CustomSortFilterProxyModel, self).setSourceModel(QAbstractItemModel)
        QAbstractItemModel.dataChanged.connect(self.invalidate)


class ReactionProxyFilter(CustomSortFilterProxyModel):

    options = ("All", "Boundary reactions", "Transport reactions",
               "Without annotation", "Without genes", "Unbalanced", "KO", "Reversible",
               "Irreversible")

    def __init__(self, *args, **kwargs):
        super(ReactionProxyFilter, self).__init__(*args, **kwargs)

    def passes_custom_filter(self, reaction):
        if self.custom_filter == 0:
            return True
        elif self.custom_filter == 1:
            return reaction.boundary is True
        elif self.custom_filter == 2:
            return len(reaction.get_compartments()) > 1
        elif self.custom_filter == 3:
            return not bool(reaction.annotation) and reaction.boundary is False and len(reaction.get_compartments()) == 1
        elif self.custom_filter == 4:
            return not bool(reaction.genes) and reaction.boundary is False
        elif self.custom_filter == 5:
            return reaction.boundary is False and reaction.balanced is not True
        elif self.custom_filter == 6:
            return reversibility(reaction.lower_bound, reaction.upper_bound) is None
        elif self.custom_filter == 7:
            return reversibility(reaction.lower_bound, reaction.upper_bound) is True
        elif self.custom_filter == 8:
            return reversibility(reaction.lower_bound, reaction.upper_bound) is False
        else:
            raise NotImplementedError


class MetaboliteProxyFilter(CustomSortFilterProxyModel):

    options = ("All", "No formula", "No reaction", "No annotation", "Dead-End")

    def __init__(self, *args, **kwargs):
        super(MetaboliteProxyFilter, self).__init__(*args, **kwargs)

    def passes_custom_filter(self, metabolite):
        """

        Parameters
        ----------
        metabolite : GEMEditor.model.classes.cobra.Metabolite

        Returns
        -------
        bool : True if row passes the filter, False otherwise.
        """

        if self.custom_filter == 0:
            # All metabolites - Always true
            return True
        elif self.custom_filter == 1:
            # Return true if the metabolite formula is not set
            return not metabolite.formula
        elif self.custom_filter == 2:
            # Return true if the metabolite is not part of any reaction
            return not bool(metabolite.reactions)
        elif self.custom_filter == 3:
            # Return True if the metabolite does not contain any annotation
            return not bool(metabolite.annotation)
        elif self.custom_filter == 4:
            return metabolite_is_dead_end(metabolite)
        else:
            raise NotImplementedError


class GeneProxyFilter(CustomSortFilterProxyModel):

    options = ("All", "Unassigned")

    def __init__(self, *args, **kwargs):
        super(GeneProxyFilter, self).__init__(*args, **kwargs)

    def passes_custom_filter(self, gene):
        """ Check that the gene passes the selected filter

        Parameters
        ----------
        gene : GEMEditor.model.classes.cobra.Gene

        Returns
        -------
        bool : True if row passes the filter, False otherwise.
        """

        if self.custom_filter == 0:
            # All metabolites - Always true
            return True
        elif self.custom_filter == 1:
            # Return true if the reaction is not assigned
            return len(gene.reactions) == 0
        else:
            raise NotImplementedError


class FluxTableProxyFilter(QSortFilterProxyModel):

    options = ("All", "Nonzero flux", "Flux at bound", "All boundary", "Active boundary")

    def __init__(self, *args, **kwargs):
        super(FluxTableProxyFilter, self).__init__(*args, **kwargs)
        self.custom_filter = 0

    def filterAcceptsRow(self, p_int, QModelIndex):
        if self.filterRegExp():
            return (self.passes_custom_filter(p_int) and
                    super(FluxTableProxyFilter, self).filterAcceptsRow(p_int, QModelIndex))
        else:
            return self.passes_custom_filter(p_int)

    def passes_custom_filter(self, row):
        if self.custom_filter == 0:
            # All rows
            return True
        elif self.custom_filter == 1:
            # Flux nonequal to zero
            return self.sourceModel().item(row, 7).data(2) != 0.
        elif self.custom_filter == 2:
            # Flux at boundary
            flux = self.sourceModel().item(row, 7).data(2)
            lower_bound = self.sourceModel().item(row, 4).data(2)
            upper_bound = self.sourceModel().item(row, 5).data(2)
            return flux == lower_bound or flux == upper_bound
        elif self.custom_filter == 3:
            # Boundary reaction
            reaction = self.sourceModel().item(row, 0).link
            return reaction.boundary is True
        elif self.custom_filter == 4:
            reaction = self.sourceModel().item(row, 0).link
            flux = self.sourceModel().item(row, 7).data(2)
            return reaction.boundary and flux != 0.
        else:
            raise NotImplementedError

    @QtCore.pyqtSlot(int)
    def set_custom_filter(self, n):
        self.custom_filter = n
        self.invalidateFilter()


class RecursiveProxyFilter(QSortFilterProxyModel):

    def __init__(self, *args, **kwargs):
        super(RecursiveProxyFilter, self).__init__(*args, **kwargs)

    def filterAcceptsRow(self, p_int, QModelIndex):
        if super(RecursiveProxyFilter, self).filterAcceptsRow(p_int, QModelIndex) is True:
            return True

        elif self.filterRegExp():
            index = self.sourceModel().index(p_int, 0, QModelIndex)

            if index.isValid():
                # Search children
                for child_row in range(self.sourceModel().rowCount(index)):
                    if self.filterAcceptsRow(child_row, index):
                        return True
        return False
