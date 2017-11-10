import logging


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


