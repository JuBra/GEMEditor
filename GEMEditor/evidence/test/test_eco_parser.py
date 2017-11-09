import pytest
from GEMEditor.evidence.eco_parser import parse_eco

# Todo: Implement parsing tests
# class TestSampleParsing:
#
#     @pytest.fixture()
#     def ecos(self):
#         return parse_eco(path)
#
#     def test_first_eco(self, ecos):
#         first = ecos["ECO:0000000"]
#         assert first.name == "evidence"
#         assert first.definition == '"A type of information that is used to support an assertion." [ECO:MCC]'
#         assert first.id == "ECO:0000000"
#         assert first.children == set([ecos["ECO:0000001"]])
#
#     def test_second_eco(self, ecos):
#         second = ecos["ECO:0000001"]
#         assert second.id == "ECO:0000001"
#         assert second.name == "inference from background scientific knowledge"
#         assert second.definition == '"A curator inference that links the current annotation to a different evidence-based annotation via background knowledge of the curator." [ECO:go, ECO:MCC]'
#         assert second.children == set([ecos["ECO:0000002"]])
#
#     def test_third_eco(self, ecos):
#         third = ecos["ECO:0000002"]
#         assert third.name == "direct assay evidence"
#         assert third.definition == '"Experimental evidence that is based on direct measurement of some aspect of a biological feature." [ECO:MCC, GO:IDA]'
#         assert third.children == set([ecos["ECO:0000003"]])
