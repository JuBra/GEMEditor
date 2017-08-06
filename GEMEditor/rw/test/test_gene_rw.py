import pytest
from GEMEditor.rw import *
from GEMEditor.rw.gene import add_genes, parse_genes
from GEMEditor.cobraClasses import Gene, Model
from cobra.io.sbml3 import SBML_DOT
from lxml.etree import Element


class TestGeneIO:

    @pytest.fixture(autouse=True)
    def setup_items(self):
        self.test_id = "test.id"
        self.test_name = "test_name"
        self.test_genome = "test_genome"
        self.gene = Gene(id=self.test_id,
                         name=self.test_name,
                         genome=self.test_genome)
        self.model = Model("Test_model")
        self.model.genes.append(self.gene)

    def test_setup(self):
        assert self.gene.id == self.test_id
        assert self.gene.name == self.test_name
        assert self.gene.genome == self.test_genome
        assert len(self.model.genes) == 1

    def test_gene_addition(self):
        root = Element("Test")
        add_genes(root, self.model)

        assert len(root) == 1
        gene_list_node = root.find(fbc_listOfGeneProducts)
        assert gene_list_node is not None
        assert len(gene_list_node) == 1

        gene_node = gene_list_node.find(fbc_geneProduct)
        assert gene_node is not None
        assert gene_node.get(fbc_id) == "G_" + self.test_id.replace(".", SBML_DOT)
        assert gene_node.get(fbc_name) == self.test_name
        assert gene_node.get(ge_genome) == self.test_genome

    def test_empty_genome_addition(self):
        root = Element("Test")
        model = Model()
        gene_id = "test_id"
        gene_name = "test_name"
        empty_genome_gene = Gene(id=gene_id,
                                 name=gene_name)
        model.genes.append(empty_genome_gene)

        assert len(model.genes) == 1

        add_genes(root, model)
        gene_list_node = root.find(fbc_listOfGeneProducts)
        assert gene_list_node is not None
        assert len(gene_list_node) == 1

        gene_node = gene_list_node.find(fbc_geneProduct)
        assert gene_node is not None
        assert gene_node.get(fbc_id) == "G_" + gene_id.replace(".", SBML_DOT)
        assert gene_node.get(fbc_name) == gene_name
        assert gene_node.get(ge_genome) is None

    def test_write_parse_consistency(self):
        root = Element("Test")
        add_genes(root, self.model)

        genes = parse_genes(root)
        assert len(genes) == 1

        gene = genes[0]
        assert gene.id == self.test_id
        assert gene.name == self.test_name
        assert gene.genome == self.test_genome
