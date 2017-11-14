from collections import defaultdict


class CleaningDict(defaultdict):

    def __init__(self):
        super(CleaningDict, self).__init__(set)

    def remove_reaction(self, key, reaction):
        self[key].discard(reaction)
        if not self[key]:
            del self[key]


class ModelStats:

    def __init__(self):

        self.unique_reactions = defaultdict(list)
        self.list_boundary_reactions = []
        self.list_transport_reactions = []
        self.list_unbalanced_reactions = []
        self.list_unannotated_reactions = []
        self.list_reaction_wo_genes = []

        self.unique_metabolites = defaultdict(list)
        self.list_unannotated_metabolites = []

        self.list_unassigned_genes = []
        self.list_unannotated_genes = []

        # Setup reaction statistics
        self.reactions_total = 0

        # Setup metabolite statistics
        self.metabolites_total = 0

        # Setup gene statistics
        self.genes_total = 0

    @property
    def reactions_unique(self):
        return len(self.unique_reactions)

    @property
    def reactions_transport(self):
        return len(self.list_transport_reactions)

    @property
    def reactions_boundary(self):
        return len(self.list_boundary_reactions)

    @property
    def reactions_unbalanced(self):
        return len(self.list_unbalanced_reactions)

    @property
    def reactions_annotated(self):
        return self.reactions_total - len(self.list_unannotated_reactions)

    @property
    def reactions_wo_genes(self):
        return len(self.list_reaction_wo_genes)

    @property
    def metabolites_unique(self):
        return len(self.unique_metabolites)

    @property
    def metabolites_annotated(self):
        return self.metabolites_total - len(self.list_unannotated_metabolites)

    @property
    def genes_assigned(self):
        return self.genes_total - len(self.list_unassigned_genes)

    @property
    def genes_annotated(self):
        return self.genes_total - len(self.list_unannotated_genes)


