
class BaseTreeElement:

    def __init__(self):
        self._children = []
        self._parents = []
        super(BaseTreeElement, self).__init__()

    def _add_child(self, child):
        self._children.append(child)

    def _remove_child(self, child, all=False):
        if all:
            self._children[:] = [x for x in self._children if x is not child]
        else:
            self._children.remove(child)

    def _add_parent(self, parent):
        self._parents.append(parent)

    def _remove_parent(self, parent, all=False):
        if all:
            self._parents[:] = [x for x in self._parents if x is not parent]
        else:
            self._parents.remove(parent)

    def add_child(self, child):
        self._add_child(child)
        child._add_parent(self)

    def remove_child(self, child, all=False):
        self._remove_child(child, all=all)
        child._remove_parent(self, all=all)

    def add_parent(self, parent):
        self._add_parent(parent)
        parent._add_child(self)

    def remove_parent(self, parent, all=False):
        self._remove_parent(parent, all=all)
        parent._remove_child(self, all=all)

    @property
    def genes(self):
        gene_set = set()
        for x in self._children:
            gene_set.update(x.genes)
        return gene_set

    @property
    def reactions(self):
        reaction_set = set()
        for x in self._parents:
            reaction_set.update(x.reactions)
        return reaction_set

    def delete_children(self, parent=None):
        for x in self._children:
            x.delete_children(self)
        self._children[:] = []
        if parent is not None:
            self._parents[:] = [x for x in self._parents if x is not parent]

    def prepare_deletion(self):
        """ Prepare the deletion of the object from the model.

        Unlink all parents and children"""

        # Delete all parents
        for parent in set(self._parents):
            self.remove_parent(parent, all=True)

        # Delete all child elements
        self.delete_children()

        try:
            super(BaseTreeElement, self).prepare_deletion()
        except AttributeError:
            pass


class EvidenceLink:

    def __init__(self, *args, **kwargs):
        super(EvidenceLink, self).__init__(*args, **kwargs)
        self._evidences = set()

    @property
    def evidences(self):
        return self._evidences.copy()

    def add_evidence(self, evidence):
        self._evidences.add(evidence)

    def remove_evidence(self, evidence):
        self._evidences.discard(evidence)

    def remove_all_evidences(self):
        for x in self.evidences:
            x.delete_links()

    def get_evidences_by_assertion(self, string):
        return [e for e in self._evidences if e.assertion == string]


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