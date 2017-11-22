from GEMEditor.base.proxy import CustomSortFilterProxyModel


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


class ReferenceProxyFilter(CustomSortFilterProxyModel):

    options = ("All", "Unassigned")

    def __init__(self, *args, **kwargs):
        super(ReferenceProxyFilter, self).__init__(*args, **kwargs)

    def passes_custom_filter(self, reference):
        """ Check that the gene passes the selected filter

        Parameters
        ----------
        gene : GEMEditor.model.classes.cobra.Gene

        Returns
        -------
        bool : True if row passes the filter, False otherwise.
        """

        if self.custom_filter == 0:
            # All references - Always true
            return True
        elif self.custom_filter == 1:
            # Return true if the reaction is not assigned
            return len(reference.linked_items) == 0
        else:
            raise NotImplementedError
