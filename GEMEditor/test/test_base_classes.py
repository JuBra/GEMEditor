import pytest
from GEMEditor.base_classes import EvidenceLink
from GEMEditor.evidence_class import Evidence


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