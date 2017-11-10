import pytest
from GEMEditor.rw import *
from GEMEditor.rw.evidences import add_evidences_to_xml, parse_evidences_from_xml, get_item_from_model
from lxml.etree import Element
import lxml.etree as ET
from GEMEditor.data_classes import Reference
from GEMEditor.evidence_class import Evidence
from GEMEditor.cobraClasses import Model, Reaction, Gene, Metabolite, GeneGroup
from GEMEditor.rw.test.ex_evidences import minimal_evidence, full_evidence
from PyQt5.QtWidgets import QApplication


# Make sure to only start an application
# if there is no active one. Opening multiple
# applications will lead to a crash.
app = QApplication.instance()
if app is None:
    app = QApplication([])


class TestEvidence:

    @pytest.fixture(autouse=True)
    def setup_evidence(self):
        self.reaction = Reaction("r_id")
        self.gene = Gene("g_id")
        self.target = Gene("g_id2")
        self.model = Model("test id")
        self.reference = Reference()
        self.model.add_gene(self.gene)
        self.model.add_gene(self.target)
        self.model.add_reactions([self.reaction])
        self.model.add_reference(self.reference)

        # Set type
        self.assertion = "Catalyzed by"
        self.eco = "ECO:0000000"
        self.comment = "test"
        self.term = "term"
        self.evidence = Evidence(entity=self.reaction, link=self.gene,
                                 term=self.term, eco=self.eco,
                                 assertion=self.assertion, comment=self.comment, target=self.target)

        self.evidence.add_reference(self.reference)

        self.model.all_evidences[self.evidence.internal_id] = self.evidence

        self.root = Element("root", nsmap={None: ge_ns})

    def test_setup(self):
        assert self.evidence.entity is self.reaction
        assert self.evidence.link is self.gene
        assert self.evidence.target is self.target

        assert len(self.evidence.references) == 1
        assert list(self.evidence.references)[0] is self.reference

        assert self.evidence.assertion == self.assertion
        assert self.evidence.eco == self.eco
        assert self.evidence.comment == self.comment
        assert self.evidence.term == self.term

    def test_add_evidence(self):
        add_evidences_to_xml(self.root, self.model)

        list_of_evidences = self.root.find(ge_listOfEvidences)
        assert list_of_evidences is not None
        assert len(list_of_evidences) == 1

        evidence_node = list_of_evidences.find(ge_evidence)
        assert evidence_node is not None
        assert evidence_node.get("entity_id") == self.reaction.id
        assert evidence_node.get("entity_type") == "Reaction"
        assert evidence_node.get("id") == self.evidence.internal_id
        assert evidence_node.get("comment") == self.comment
        assert evidence_node.get("link_id") == self.gene.id
        assert evidence_node.get("link_type") == "Gene"
        assert evidence_node.get("target_id") == self.target.id
        assert evidence_node.get("target_type") == "Gene"
        assert evidence_node.get("assertion") == self.assertion
        assert evidence_node.get("eco") == self.eco
        assert evidence_node.get("term") == self.term

        evidence_references_node = evidence_node.find(ge_listOfReferenceLinks)
        assert evidence_references_node is not None
        assert len(evidence_references_node) == 1

        reference_link_node = evidence_references_node.find(ge_referenceLink)
        assert reference_link_node is not None
        assert reference_link_node.get("id") == self.reference.id

    def test_no_references_added_if_empty(self):
        self.evidence.remove_all_references()
        add_evidences_to_xml(self.root, self.model)

        list_of_evidences = self.root.find(ge_listOfEvidences)
        assert list_of_evidences is not None

        evidence_node = list_of_evidences.find(ge_evidence)
        assert evidence_node is not None

        # Check that reference not is not found
        assert evidence_node.find(ge_listOfReferenceLinks) is None

    def test_write_parse_consistency(self):
        add_evidences_to_xml(self.root, self.model)

        model = Model("New model")
        model.add_gene(self.gene)
        model.add_gene(self.target)
        model.add_reactions([self.reaction])
        model.add_reference(self.reference)

        assert len(model.all_evidences) == 0
        parse_evidences_from_xml(self.root, model)
        assert len(model.all_evidences) == 1

        evidence = model.all_evidences[self.evidence.internal_id]
        assert evidence == self.evidence

    def test_get_item_from_model(self):
        model = Model("test id")
        reaction = Reaction("r_id")
        metabolite = Metabolite("m_id")
        gene = Gene("g_id")
        # ToDo: Add gene group

        model.add_reactions([reaction])
        model.add_metabolites([metabolite]),
        model.add_gene(gene)
        # ToDo: Add gene group

        assert get_item_from_model("Model", model.id, model) is model
        assert get_item_from_model("Reaction", reaction.id, model) is reaction
        assert get_item_from_model("Metabolite", metabolite.id, model) is metabolite
        assert get_item_from_model("Gene", gene.id, model) is gene

        # Test expected errors

        # GeneGroup not implemented
        with pytest.raises(NotImplementedError):
            get_item_from_model("GeneGroup", "test_id", model)

        # ID not in model
        with pytest.raises(KeyError):
            get_item_from_model("Reaction", "Not in model", model)
        with pytest.raises(KeyError):
            get_item_from_model("Metabolite", "Not in model", model)
        with pytest.raises(KeyError):
            get_item_from_model("Gene", "Not in model", model)

    def test_minimal_example(self):
        """ Test that a minimal evidence example is parsed correctly """

        xml_tree = ET.fromstring(minimal_evidence)
        model = Model()
        reaction = Reaction("Test")
        model.add_reaction(reaction)

        assert len(model.all_evidences) == 0
        assert len(reaction.evidences) == 0

        parse_evidences_from_xml(xml_tree, model)

        assert len(model.all_evidences) == 1
        assert len(reaction.evidences) == 1

        evidence = list(reaction.evidences)[0]
        assert evidence.entity is reaction
        assert evidence.assertion == "Presence"

    def test_full_example(self):
        """ Test that a minimal evidence example is parsed correctly """

        xml_tree = ET.fromstring(full_evidence)
        model = Model()
        reaction = Reaction("Test")
        link_item = Gene("link_id")
        target_item = Gene("target_id")
        reference = Reference("ref_id")
        model.add_reaction(reaction)
        model.add_gene(link_item)
        model.add_gene(target_item)
        model.add_reference(reference)

        assert len(model.all_evidences) == 0
        assert len(reaction.evidences) == 0

        parse_evidences_from_xml(xml_tree, model)

        assert len(model.all_evidences) == 1
        assert len(reaction.evidences) == 1

        evidence = list(reaction.evidences)[0]
        assert evidence.entity is reaction
        assert evidence.link is link_item
        assert evidence.target is target_item
        assert evidence.assertion == "Catalyzed by"
        assert evidence.eco == "ECO:0000000"
        assert len(evidence.references) == 1
        assert list(evidence.references)[0] is reference
        assert evidence.comment == "test comment"

