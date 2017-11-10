import logging


class EvidenceLink:

    def __init__(self, *args, **kwargs):
        super(EvidenceLink, self).__init__(*args, **kwargs)
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


