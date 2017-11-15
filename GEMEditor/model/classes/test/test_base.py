import pytest
from GEMEditor.model.classes.base import EvidenceLink, BaseTreeElement
from GEMEditor.model.classes.evidence import Evidence


class TestBaseEvidenceElement:

    @pytest.fixture(autouse=True)
    def setup_class(self):
        self.instance = EvidenceLink()
        self.evidence = Evidence()

    def test_setup(self):
        assert isinstance(self.instance.evidences, set)
        assert len(self.instance.evidences) == 0

    def test_add_evidence(self):
        self.instance.add_evidence(self.evidence)
        assert self.evidence in self.instance.evidences
        assert len(self.instance.evidences) == 1

    def test_remove_evidence(self):
        self.instance.add_evidence(self.evidence)
        assert self.evidence in self.instance.evidences
        self.instance.remove_evidence(self.evidence)
        assert self.evidence not in self.instance.evidences
        assert len(self.instance.evidences) == 0


class TestBaseTreeElement:

    def test_add_child(self):
        parent = BaseTreeElement()
        child = BaseTreeElement()
        parent.add_child(child)

        # Check that the items are properly linked
        assert child in parent._children
        assert parent in child._parents

        # Check that genes returns empty as there is no child returning itself
        assert not parent.genes
        assert not child.reactions

    def test_add_parent(self):
        parent = BaseTreeElement()
        child = BaseTreeElement()
        child.add_parent(parent)

        # Check that the items are properly linked
        assert child in parent._children
        assert parent in child._parents

        # Check that genes returns empty as there is no child returning itself
        assert not parent.genes
        assert not child.reactions

    def test_removal_parent(self):
        parent = BaseTreeElement()
        child = BaseTreeElement()
        child.add_parent(parent)
        child.add_parent(parent)

        assert child._parents.count(parent) == 2
        assert parent._children.count(child) == 2

        # Remove only one entry
        child.remove_parent(parent)

        assert child._parents.count(parent) == 1
        assert parent._children.count(child) == 1

        # Readd parent
        child.add_parent(parent)

        assert child._parents.count(parent) == 2
        assert parent._children.count(child) == 2

        # Remove all entries for parent1
        child.remove_parent(parent, all=True)

        assert child._parents.count(parent) == 0
        assert parent._children.count(child) == 0

    def test_remove_parent2(self):
        parent = BaseTreeElement()
        child = BaseTreeElement()
        child.add_parent(parent)

        child.remove_parent(parent, all=True)
        assert not child._parents

    def test_removal_child(self):
        parent = BaseTreeElement()
        child = BaseTreeElement()
        parent.add_child(child)
        parent.add_child(child)

        assert child._parents.count(parent) == 2
        assert parent._children.count(child) == 2

        # Remove only one entry
        parent.remove_child(child)

        assert child._parents.count(parent) == 1
        assert parent._children.count(child) == 1

        # Readd child
        parent.add_child(child)

        assert child._parents.count(parent) == 2
        assert parent._children.count(child) == 2

        # Remove all entries for child1
        parent.remove_child(child, all=True)

        assert child._parents.count(parent) == 0
        assert parent._children.count(child) == 0
