

class BaseModelItem:

    def __init__(self):
        super(BaseModelItem, self).__init__()
        self.gem_evidences = set()
        self.gem_annotations = set()

    def add_evidence(self, evidence):
        self.gem_evidences.add(evidence)

    def remove_evidence(self, evidence):
        self.gem_evidences.discard(evidence)

    def get_evidences_by_assertion(self, string):
        return [e for e in self.gem_evidences if e.assertion == string]

    def remove_all_evidences(self):
        for x in self.gem_evidences.copy():
            x.delete_links()

    def gem_prepare_deletion(self):
        self.remove_all_evidences()

    def add_annotation(self, annotation):
        self.gem_annotations.add(annotation)

    def remove_annotation(self, annotation):
        self.gem_annotations.discard(annotation)

    def get_annotation_by_collection(self, *args):
        return set([x.identifier for x in self.gem_annotations if x.collection in args])



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


class BaseReferenceElement:
    def __init__(self, *args, **kwargs):
        super(BaseReferenceElement, self).__init__(*args, **kwargs)
        self.gem_references = set()

    def add_reference(self, reference):
        self.gem_references.add(reference)

    def remove_reference(self, reference):
        self.gem_references.discard(reference)

    def gem_prepare_deletion(self):
        """ Prepare deletion of item """
        self.gem_references.clear()

        try:
            super(BaseReferenceElement, self).gem_prepare_deletion()
        except AttributeError:
            pass