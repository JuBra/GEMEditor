from lxml.etree import SubElement
from GEMEditor.rw import *
from GEMEditor.rw.annotation import annotate_xml_from_model
from cobra.io.sbml3 import SBML_DOT, clip
from GEMEditor.cobraClasses import Gene
from PyQt5.QtWidgets import QApplication


def add_genes(model_node, model):
    # add in genes
    if len(model.genes) > 0:
        genes_list_node = SubElement(model_node, fbc_listOfGeneProducts)
        for gene in model.genes:
            gene_id = gene.id.replace(".", SBML_DOT)
            gene_node = SubElement(genes_list_node, fbc_geneProduct,
                                   attrib={fbc_id: cobra_gene_prefix + gene_id,
                                           fbc_label: gene_id,
                                           fbc_name: gene.name or gene.id})
            if gene.genome:
                gene_node.set(ge_genome, gene.genome)

            annotate_xml_from_model(gene_node, gene)


def parse_genes(model_node, model=None, progress=None):

    gene_list_node = model_node.find(fbc_listOfGeneProducts)

    if gene_list_node is None:
        return
    elif progress is None:
        pass
    elif not progress.wasCanceled():
        progress.setLabelText("Reading genes...")
        progress.setRange(0, len(gene_list_node))
    else:
        return

    genes = []
    for i, gene_node in enumerate(gene_list_node.iterfind(fbc_geneProduct)):

        if progress is None:
            pass
        elif not progress.wasCanceled():
            progress.setValue(i)
            QApplication.processEvents()
        else:
            return

        new_gene = Gene(id=clip(gene_node.get(fbc_id), cobra_gene_prefix).replace(SBML_DOT, "."),
                        name=gene_node.get(fbc_name),
                        genome=gene_node.get(ge_genome))

        if model is not None:
            model.add_gene(new_gene)
        else:
            genes.append(new_gene)

    return genes
