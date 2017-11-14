import operator
from collections import namedtuple, OrderedDict, defaultdict
from uuid import uuid4


class LinkReference:
    """ Base class for items

    Implements all methods for items that
    can contain a link to a reference item.

    See Evidence and ModelTest classes """

    def __init__(self, *args, **kwargs):
        super(LinkReference, self).__init__(*args, **kwargs)
        self._references = set()

    @property
    def references(self):
        return self._references.copy()

    def add_reference(self, reference, reciprocal=True):
        """ Remove reference link from item

        All items that inherit from this class
        should be able to link to each other.

        Parameters
        ----------
        reference: Reference
        reciprocal: bool
        """
        self._references.add(reference)
        if reciprocal:
            reference.add_link(self, reciprocal=False)

    def remove_reference(self, reference, reciprocal=True):
        """ Remove reference link from item

        Parameters
        ----------
        item: Reference
        reciprocal: bool
        """
        self._references.discard(reference)
        if reciprocal:
            reference.remove_link(self, reciprocal=False)

    def remove_all_references(self):
        """ Remove all reference links """
        for reference in self.references:
            self.remove_reference(reference, reciprocal=True)


class Reference:
    """ ReferenceItem contains the information a pubmed or similar literature reference
    Authors are saved as author instances """

    def __init__(self, id=None, pmid="", pmc="", doi="", url="",
                 authors=None, year="", title="", journal="", abstract=""):
        super(Reference, self).__init__()
        self._linked_items = set()
        self.id = id or str(uuid4())
        self.pmid = pmid
        self.pmc = pmc
        self.doi = doi
        self.url = url
        if authors is None:
            self.authors = []
        else:
            self.authors = authors
        self.year = year
        self.title = title
        self.journal = journal
        self.abstract = abstract

    @property
    def linked_items(self):
        return self._linked_items.copy()

    @property
    def annotation(self):
        result = set()
        if self.pmid:
            result.add(Annotation("pubmed", self.pmid))
        if self.pmc:
            result.add(Annotation("pmc", self.pmc))
        if self.doi:
            result.add(Annotation("doi", self.doi))
        return result

    def add_link(self, item, reciprocal=True):
        """ Remove reference link from item

        All items that inherit from this class
        should be able to link to each other.

        Parameters
        ----------
        reference: LinkReference
        reciprocal: bool
        """
        self._linked_items.add(item)
        if reciprocal:
            item.add_reference(self, reciprocal=False)

    def remove_link(self, item, reciprocal=True):
        """ Remove reference link from item

        Parameters
        ----------
        item: LinkReference
        reciprocal: bool
        """
        self._linked_items.discard(item)
        if reciprocal:
            item.remove_reference(self, reciprocal=False)

    def remove_all_links(self):
        """ Remove all reference links """

        for item in self.linked_items:
            self.remove_link(item, reciprocal=True)

    def reference_string(self):
        """ Get the authors part of the usual citation of scientific literature i.e.:

            Lastname F et al., YYYY if there are more than 2 authors
            Lastname1 F1 and Lastname2 F2, YYYY if there are 2 authors
            Lastname F, YYYY if there is only one author

            Input tuple with (lastname, firstname, initials)
        """
        # If there are more than 2 authors return a string
        if len(self.authors) > 2:
            return "{0} et al., {1}".format(self.authors[0].display_str, self.year)
        elif len(self.authors) == 2:
            return "{0} and {1}, {2}".format(self.authors[0].display_str,
                                             self.authors[1].display_str,
                                             self.year)
        elif self.authors:
            return "{0}, {1}".format(self.authors[0].display_str, self.year)
        else:
            return ""

    def __str__(self):
        id_strings = []
        for attrib in ("pmid", "pmc", "doi"):
            if getattr(self, attrib):
                id_strings.append("{0}: {1}".format(attrib.upper(), getattr(self, attrib)))

        return "ID: {id}\n" \
               "Authors: {authors}\n" \
               "Title: {title}\n" \
               "{id_strings}".format(id=self.id,
                                     authors=self.reference_string(),
                                     title=self.title,
                                     id_strings="; ".join(id_strings))


class Annotation:
    def __init__(self, collection=None, identifier=None, type="is"):
        self._collection = collection
        self._identifier = identifier
        self._type = type

    @property
    def collection(self):
        return self._collection

    @property
    def identifier(self):
        return self._identifier

    @property
    def type(self):
        return self._type

    def __eq__(self, other):
        if isinstance(other, Annotation) and (self.collection == other.collection and
                                                self.identifier == other.identifier and
                                                      self.type == other.type):
            return True
        else:
            return False

    def __hash__(self):
        return hash((self._collection, self._identifier, self._type))

    def __str__(self):
        return "Annotation({0!s}, {1!s})".format(self._collection, self._identifier)


class Author(namedtuple("Author", ["lastname", "firstname", "initials"])):

    __slots__ = ()

    def __new__(cls, lastname="", firstname="", initials=""):
        self = super(Author, cls).__new__(cls,
                                          lastname=lastname,
                                          firstname=firstname,
                                          initials=initials)
        return self

    @property
    def display_str(self):
        if self.initials:
            return "{0} {1}".format(self.lastname, self.initials)
        else:
            return self.lastname


class ModelTest(LinkReference):

    def __init__(self, id=None, description="", comment=""):
        super(ModelTest, self).__init__()
        self.id = id or str(uuid4())
        self.description = description or ""
        self.comment = comment or ""
        self.gene_settings = []
        self.reaction_settings = []
        self.outcomes = []

    def add_setting(self, setting):
        if isinstance(setting, ReactionSetting):
            self.reaction_settings.append(setting)
        elif isinstance(setting, GeneSetting):
            self.gene_settings.append(setting)

    def add_outcome(self, outcome):
        self.outcomes.append(outcome)

    def get_gene_settings(self):
        return self.gene_settings

    def get_reaction_settings(self):
        return self.reaction_settings

    def all_settings(self):
        return self.reaction_settings + self.gene_settings

    def clear_all(self):
        self.gene_settings[:] = []
        self.reaction_settings[:] = []
        self.outcomes[:] = []
        for x in list(self.references):
            self.remove_reference(x)


class ReactionSetting:

    def __init__(self, reaction=None, upper_bound=None,
                 lower_bound=None, objective_coefficient=None):
        self.reaction = reaction
        self._old_upper = None
        self._old_lower = None
        self._old_objective = None
        self.upper_bound = upper_bound
        self.lower_bound = lower_bound
        self.objective_coefficient = objective_coefficient
        self.state_saved = False

    def do(self):
        self._old_upper = self.reaction.upper_bound
        self._old_lower = self.reaction.lower_bound
        self._old_objective = self.reaction.objective_coefficient
        self.state_saved = True
        self.reaction.upper_bound = self.upper_bound
        self.reaction.lower_bound = self.lower_bound
        self.reaction.objective_coefficient = self.objective_coefficient

    def undo(self):
        if self.state_saved:
            self.reaction.upper_bound = self._old_upper
            self.reaction.lower_bound = self._old_lower
            self.reaction.objective_coefficient = self._old_objective
            self._old_upper = None
            self._old_lower = None
            self._old_objective = None
            self.state_saved = False

    def __eq__(self, other):
        if (isinstance(other, self.__class__) and
            self.reaction is other.reaction and
            self.upper_bound == other.upper_bound and
            self.lower_bound == other.lower_bound and
            self.objective_coefficient == other.objective_coefficient):
            return True
        else:
            return False

    def is_valid(self):
        if (self.reaction and self.upper_bound is not None and
                    self.lower_bound is not None and self.objective_coefficient is not None):
            return True
        else:
            return False


class GeneSetting:

    def __init__(self, gene=None, activity=None):
        self.gene = gene
        self.activity = activity
        self._old_activity = None
        self._changed_reactions = []

    def do(self):
        self._old_activity = self.gene.functional
        self.gene.functional = self.activity
        for reaction in self.gene.reactions:
            if not reaction.functional:
                self._changed_reactions.append((reaction, reaction.lower_bound, reaction.upper_bound))
                reaction.lower_bound, reaction.upper_bound = 0, 0

    def undo(self):
        for x in reversed(self._changed_reactions):
            x[0].lower_bound = x[1]
            x[0].upper_bound = x[2]
        self._changed_reactions = []
        if self._old_activity is not None:
            self.gene.functional = self._old_activity
            self._old_activity = None

    def __eq__(self, other):
        if (isinstance(other, self.__class__) and
            self.gene is other.gene and self.activity is other.activity):
            return True
        else:
            return False

    def is_valid(self):
        return self.activity is not None and self.gene is not None


class Outcome:

    options = OrderedDict([("greater than", operator.gt),
                           ("less than", operator.lt)])

    def __init__(self, reaction=None, value=None, operator=None):
        self.reaction = reaction
        self.value = value
        self.operator = operator

    def check_solution(self, solution, precision=0.01):
        """ Check if the flux value in the solution matches the expectation in the testcase """
        if not self.operator:
            return False
        selected_operator = self.options[self.operator]
        if selected_operator is operator.gt:
            return selected_operator(solution.x_dict[self.reaction.id]-precision, self.value)
        else:
            return selected_operator(solution.x_dict[self.reaction.id]+precision, self.value)

    def is_valid(self):
        return (self.operator in self.options and
                isinstance(self.value, float) and
                self.reaction is not None)

    def __eq__(self, other):
        if (isinstance(other, self.__class__) and
                    self.reaction is other.reaction and
                    self.value == other.value and
                    self.operator == other.operator):
            return True
        else:
            return False


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


