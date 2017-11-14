from collections import namedtuple
from uuid import uuid4


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
        reference: GEMEditor.model.classes.base.LinkReference
        reciprocal: bool
        """
        self._linked_items.add(item)
        if reciprocal:
            item.add_reference(self, reciprocal=False)

    def remove_link(self, item, reciprocal=True):
        """ Remove reference link from item

        Parameters
        ----------
        item: GEMEditor.model.classes.base.LinkReference
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