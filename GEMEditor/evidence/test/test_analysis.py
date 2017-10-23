from GEMEditor.evidence.analysis import *
from GEMEditor.evidence_class import Evidence
from GEMEditor.cobraClasses import Reaction, Gene


class Test_sort_evidences:

    def test_sorting_erroneous(self):
        evidence = Evidence()

        assert evidence.is_valid() is None

        conflicts, failing, errors = sort_evidences([evidence])
        assert not conflicts
        assert not failing
        assert evidence in errors

    def test_sorting_failing(self):
        reaction = Reaction()
        gene = Gene()
        evidence = Evidence(entity=gene, target=reaction, assertion="Catalyzing reaction")

        assert evidence.is_valid() is False

        conflicts, failing, errors = sort_evidences([evidence])
        assert not conflicts
        assert [evidence] in failing
        assert not errors

    def test_sorting_valid(self):
        reaction = Reaction()
        gene = Gene()
        evidence = Evidence(entity=gene, target=reaction, assertion="Catalyzing reaction")
        reaction.add_child(gene)

        assert evidence.is_valid() is True

        conflicts, failing, errors = sort_evidences([evidence])
        assert not conflicts
        assert not failing
        assert not errors

    def test_sorting_conflicting(self):
        reaction = Reaction()
        gene = Gene()
        reaction.add_child(gene)
        evidence1 = Evidence(entity=gene, target=reaction, assertion="Catalyzing reaction")
        evidence2 = Evidence(entity=gene, target=reaction, assertion="Not catalyzing reaction")

        assert evidence1.is_valid() is True
        assert evidence2.is_valid() is False

        conflicts, failing, errors = sort_evidences([evidence1, evidence2])
        assert len(conflicts) == 1
        assert set(conflicts[0]) == set([evidence1, evidence2])
        assert not failing
        assert not errors
