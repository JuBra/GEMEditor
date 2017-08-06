

class BaseEvidenceElement:
    def __init__(self, *args, **kwargs):
        super(BaseEvidenceElement, self).__init__(*args, **kwargs)
        self.gem_evidences = set()

    def add_evidence(self, evidence):
        self.gem_evidences.add(evidence)

    def remove_evidence(self, evidence):
        self.gem_evidences.discard(evidence)

    def remove_all_evidences(self):
        for x in self.gem_evidences.copy():
            x.delete_links()

    def get_evidences_by_assertion(self, string):
        return [e for e in self.gem_evidences if e.assertion == string]

    def gem_prepare_deletion(self):
        """ Prepare deletion of all items """
        self.remove_all_evidences()

        try:
            super(BaseEvidenceElement, self).gem_prepare_deletion()
        except AttributeError:
            pass
