from uuid import uuid4

from GEMEditor.model.classes.base import ReferenceLink
from GEMEditor.evidence.assertions import ASSERTIONS


class Evidence(ReferenceLink):
    _validity = dict((x.text, x.func_validity) for x in ASSERTIONS)
    _fixes = dict((x.text, x.func_fix) for x in ASSERTIONS)

    def __init__(self, internal_id=None, entity=None, eco=None, assertion=None, comment=None,
                 target=None):
        super(Evidence, self).__init__()
        self.internal_id = internal_id or str(uuid4())
        self.entity = None
        self.assertion = None
        self.eco = None
        self.comment = None
        self.target = None

        self.set_entity(entity)
        self.set_eco(eco)
        self.set_assertion(assertion)
        self.set_comment(comment)
        self.set_target(target)

    def set_entity(self, new_entity, reciprocal=True):
        """ Set the model entity that is the basis for the evidence

        Parameters
        ----------
        new_entity :
        reciprocal : bool

        Returns
        -------
        None
        """

        # Remove link from old entity to this evidence
        if self.entity:
            self.entity.remove_evidence(self)

        self.entity = new_entity
        # Set the link from the new entity to this evidence
        if reciprocal and new_entity:
            new_entity.add_evidence(self)

    def set_assertion(self, assertion):
        self.assertion = assertion or ""

    def set_target(self, new_target, reciprocal=True):
        """ Set the model entity that is the linked for the assertion

        Parameters
        ----------
        new_entity :
        reciprocal : bool

        Returns
        -------
        None
        """
        # Remove reference from old link to this evidence
        if self.target is not None:
            self.target.remove_evidence(self)

        self.target = new_target
        # Set the reference from the new link to this evidence
        if reciprocal and new_target:
            new_target.add_evidence(self)

    def set_eco(self, eco):
        self.eco = eco or ""

    def set_comment(self, comment):
        self.comment = comment or ""

    def delete_links(self):
        # Delete references
        self.remove_all_references()

        # Remove from items
        if self.entity:
            self.entity.remove_evidence(self)
            self.entity = None

        if self.target:
            self.target.remove_evidence(self)
            self.target = None

    def setup_links(self):
        """ Method that is used to establish the links from
        all linked items to this evidence instance

        Use this on copies created with the copy method in order
        to get proper cross referencing """

        # Set link for references
        for x in self.references:
            x.add_link(self, reciprocal=False)

        if self.entity:
            self.entity.add_evidence(self)

        if self.target:
            self.target.add_evidence(self)

    def copy(self):
        """ Return a copy of the evidence instance that links
        the same items as the original, but is not linked
        reciprocally by the items """

        new_evidence = self.__class__(internal_id=self.internal_id, assertion=self.assertion,
                                      eco=self.eco, comment=self.comment)
        # Don't set in constructor in order to allow non cross linked
        # copy
        new_evidence.set_entity(self.entity, reciprocal=False)
        new_evidence.set_target(self.target, reciprocal=False)
        for reference in self.references:
            new_evidence.add_reference(reference, reciprocal=False)

        return new_evidence

    def is_valid(self):
        """ Check that the evidence holds

        This function is called in order to
        assert if the the model complies with
        the experimental information stored
        in this item

        Returns
        -------
        bool or None,   Returns True if the assertion holds
                        Returns False if the assertion does not hold
                        Returns None if there is an error in the evidence
        """

        try:
            # Call validity function passing this instance
            return self._validity[self.assertion](self)
        except (AttributeError, KeyError, ValueError):
            return None

    def fix(self):
        """ Fix this evidence item

        In case the current evidence item is
        invalid, try to fix it. I.e. connect
        the gene to the reaction.

        Returns
        -------
        bool,   Returns True if the evidence could be fixed
                Returns True if the evidence could not be fixed
        """

        # Check if the evidence is still invalid
        validity = self.is_valid()
        if validity is not False:
            return bool(validity)

        try:
            self._fixes[self.assertion](self)
            return True
        except (KeyError, AttributeError, NotImplementedError):
            return False

    def __str__(self):
        return "ID: {id}\nEntity: {entity}\n" \
               "Assertion: {assertion}\n " \
               "Target: {target}\nECO: {eco}\n" \
               "Comment: {comment}\nRef: {ref}".format(id=self.internal_id,
                                                       entity=self.entity,
                                                       assertion=self.assertion,
                                                       target=self.target,
                                                       eco=self.eco,
                                                       comment=self.comment,
                                                       ref=";".join(x.reference_string for x in
                                                                    self.references))

    def __eq__(self, other):
        if (isinstance(other, Evidence) and
                self.internal_id == other.internal_id and
                self.entity is other.entity and
                self.target is other.target and
                self.eco == other.eco and
                self.assertion == other.assertion and
                self.comment == other.comment and
                self.references == other.references):
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return id(self)

    def substitute_item(self, old_item, new_item):
        """ Substitute an item linked in this evidence

        Parameters
        ----------
        old_item
        new_item

        Returns
        -------

        """

        if old_item is self.entity:
            self.set_entity(new_item)
        elif old_item is self.target:
            self.set_target(new_item)
        else:
            raise KeyError("{0!s} not a part of evidence {1!s}".format(old_item, self))
