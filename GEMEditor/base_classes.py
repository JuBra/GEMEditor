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
    
    def prepare_deletion(self):
        self.remove_all_evidences()

        try:
            super(BaseEvidenceElement, self).prepare_deletion()
        except AttributeError:
            return


class BaseReferenceElement:

    def __init__(self, *args, **kwargs):
        super(BaseReferenceElement, self).__init__(*args, **kwargs)
        self.references = set()

    def add_reference(self, reference):
        self.references.add(reference)

    def remove_reference(self, reference):
        self.references.discard(reference)

    def prepare_deletion(self):
        # Do nothing as references are currently not reciprocally linked

        try:
            super(BaseReferenceElement, self).prepare_deletion()
        except AttributeError:
            return
