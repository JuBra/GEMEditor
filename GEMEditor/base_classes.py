import logging


class BaseEvidenceElement:

    def __init__(self, *args, **kwargs):
        super(BaseEvidenceElement, self).__init__(*args, **kwargs)
        self.evidences = set()

    def add_evidence(self, evidence):
        self.evidences.add(evidence)

    def remove_evidence(self, evidence):
        self.evidences.discard(evidence)

    def remove_all_evidences(self):
        for x in self.evidences.copy():
            x.delete_links()

    def get_evidences_by_assertion(self, string):
        return [e for e in self.evidences if e.assertion == string]


class ReferenceLink:
    """ Base class for items

    Implements all methods for items that
    can contain a link to a reference item.

    See Evidence and ModelTest classes """

    def __init__(self, *args, **kwargs):
        super(ReferenceLink, self).__init__(*args, **kwargs)
        self._references = set()

    @property
    def references(self):
        return self._references.copy()

    def add_reference(self, item, reciprocal=True):
        """ Remove reference link from item

        All items that inherit from this class
        should be able to link to each other.

        Parameters
        ----------
        reference: ReferenceLink
        reciprocal: bool
        """
        self._references.add(item)
        if reciprocal:
            item.add_reference(self, reciprocal=False)

    def remove_reference(self, item, reciprocal=True):
        """ Remove reference link from item

        Parameters
        ----------
        item: ReferenceLink
        reciprocal: bool
        """
        self._references.discard(item)
        if reciprocal:
            item.remove_reference(self, reciprocal=False)

    def remove_all_references(self):
        """ Remove all reference links """

        for item in self.references:
            self.remove_reference(item, reciprocal=True)

