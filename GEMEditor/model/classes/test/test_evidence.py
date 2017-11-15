import pytest
from GEMEditor.model.classes.cobra import Reaction, Gene
from GEMEditor.model.classes.reference import Reference
from GEMEditor.model.classes.evidence import Evidence


class TestEvidence:

    def test_evidence_init(self):
        entity = Reaction()
        link = Gene()
        target = Gene("id2")
        eco = "ECO:000000"
        assertion = "Presence"
        comment = "test comment"
        reference = Reference()
        evidence = Evidence(entity=entity, link=link, eco=eco, assertion=assertion, comment=comment, target=target)
        evidence.add_reference(reference)

        # Check proper linking
        assert evidence.entity is entity
        assert evidence in entity.evidences
        assert evidence.link is link
        assert evidence in link.evidences
        assert evidence.target is target
        assert evidence in target.evidences

        # Check attributes
        assert evidence.assertion == assertion
        assert evidence.eco == eco
        assert evidence.comment == comment

        # Check id is set
        assert type(evidence.internal_id) is str
        assert evidence.internal_id != ""

        # Check the references
        assert reference in evidence.references
        assert evidence in reference.linked_items

    def test_override_entity(self):
        entity = Reaction()
        link = Gene()
        eco = "ECO:000000"
        assertion = "Presence"
        comment = "test comment"
        reference = Reference()
        evidence = Evidence(entity=entity, link=link, eco=eco, assertion=assertion, comment=comment)
        evidence.add_reference(reference)

        new_reaction = Reaction()
        evidence.set_entity(new_reaction)

        # Check disconnection of old reaction
        assert evidence.entity is new_reaction
        assert evidence not in entity.evidences

    def test_override_link(self):
        entity = Reaction()
        link = Gene()
        eco = "ECO:000000"
        assertion = "Presence"
        comment = "test comment"
        reference = Reference()
        evidence = Evidence(entity=entity, link=link, eco=eco, assertion=assertion, comment=comment)
        evidence.add_reference(reference)

        new_gene = Gene()
        evidence.set_linked_item(new_gene)

        # Check disconnection of old reaction
        assert evidence.link is new_gene
        assert evidence not in link.evidences

    def test_override_target(self):
        entity = Reaction()
        target = Gene()
        eco = "ECO:000000"
        assertion = "Presence"
        comment = "test comment"
        reference = Reference()
        evidence = Evidence(entity=entity, eco=eco, assertion=assertion, comment=comment, target=target)
        evidence.add_reference(reference)

        new_gene = Gene()
        evidence.set_target(new_gene)

        # Check disconnection of old reaction
        assert evidence.target is new_gene
        assert evidence not in target.evidences

    def test_delete_links(self):
        entity = Reaction()
        link = Gene()
        target=Gene()
        eco = "ECO:000000"
        assertion = "Presence"
        comment = "test comment"
        reference = Reference()
        evidence = Evidence(entity=entity, link=link, eco=eco, assertion=assertion, comment=comment, target=target)
        evidence.add_reference(reference)

        evidence.delete_links()

        assert evidence.entity is None
        assert evidence.link is None
        assert len(evidence.references) == 0
        assert evidence not in entity.evidences
        assert evidence not in link.evidences
        assert evidence not in target.evidences

    def test_setup_links(self):
        entity = Reaction()
        link = Gene()
        target = Gene()
        eco = "ECO:000000"
        assertion = "Presence"
        comment = "test comment"
        reference = Reference()
        evidence = Evidence()
        evidence.entity = entity
        evidence.link = link
        evidence.target = target
        evidence.eco = eco
        evidence.assertion = assertion
        evidence.comment = comment
        evidence.add_reference(reference, reciprocal=False)

        assert evidence not in entity.evidences
        assert evidence not in link.evidences
        assert evidence not in reference.linked_items
        assert evidence not in target.evidences

        evidence.setup_links()

        assert evidence in entity.evidences
        assert evidence in link.evidences
        assert evidence in reference.linked_items
        assert evidence in target.evidences

    def test_copy_evidence(self):
        entity = Reaction()
        link = Gene()
        target = Gene()
        eco = "ECO:000000"
        assertion = "Presence"
        comment = "test comment"
        reference = Reference()
        evidence = Evidence(entity=entity, link=link, eco=eco, assertion=assertion, comment=comment, target=target)
        evidence.add_reference(reference)

        # Create copy
        copy = evidence.copy()

        # Check the correctness of the copy
        assert evidence.entity is copy.entity
        assert evidence.link is copy.link
        assert evidence.target is copy.target
        assert evidence.eco == copy.eco
        assert evidence.assertion == copy.assertion
        assert evidence.comment == copy.comment
        assert evidence.references == copy.references
        assert evidence.references is not copy.references

        # Check that the copy is not linked
        assert copy not in entity.evidences
        assert copy not in link.evidences
        assert copy not in reference.linked_items
        assert copy not in target.evidences

    def test_equality(self):
        entity = Reaction()
        link = Gene()
        target = Gene()
        eco = "ECO:000000"
        assertion = "Presence"
        comment = "test comment"
        reference = Reference()
        evidence = Evidence(entity=entity, link=link, eco=eco, assertion=assertion, comment=comment, target=target)
        evidence.add_reference(reference)
        assert evidence.copy() == evidence

    @pytest.mark.parametrize("attribute,new_value", [("entity", Reaction()),
                                                      ("link", Gene()),
                                                      ("target", Gene()),
                                                      ("eco", "new eco"),
                                                      ("assertion", "new assertion"),
                                                      ("comment", "new comment")])
    def test_inequality(self, attribute, new_value):
        entity = Reaction()
        link = Gene()
        target = Gene()
        eco = "ECO:000000"
        assertion = "Presence"
        comment = "test comment"
        reference = Reference()
        evidence = Evidence(entity=entity, link=link, eco=eco, assertion=assertion, comment=comment, target=target)
        evidence.add_reference(reference)

        new_copy = evidence.copy()
        setattr(new_copy, attribute, new_value)
        assert new_copy != evidence
        assert not new_copy == evidence

    def test_inequality_reference(self):
        entity = Reaction()
        link = Gene()
        target = Gene()
        eco = "ECO:000000"
        assertion = "Presence"
        comment = "test comment"
        reference = Reference()
        evidence = Evidence(entity=entity, link=link, eco=eco, assertion=assertion, comment=comment, target=target)
        evidence.add_reference(reference)

        new_copy = evidence.copy()
        new_copy.remove_all_references()

        assert new_copy != evidence
        assert not new_copy == evidence



