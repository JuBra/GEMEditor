from collections import defaultdict, namedtuple


def get_resource_dict(resources):
    result = dict()
    for x in resources:
        result[x.collection] = x
        result[x.display_name] = x
    return result


AA_names = {"Alanine": "A",
            "Arginine": "R",
            "Asparagine": "N",
            "Aspartic acid": "D",
            "Cysteine": "C",
            "Glutamic acid": "E",
            "Glutamine": "Q",
            "Glycine": "G",
            "Histidine": "H",
            "Isoleucine": "I",
            "Leucine": "L",
            "Lysine": "K",
            "Methionine": "M",
            "Phenylalanine": "F",
            "Proline": "P",
            "Serine": "S",
            "Threonine": "T",
            "Tryptophan": "W",
            "Tyrosine": "Y",
            "Valine": "V",
            "Selenocysteine": "U",
            "Pyrrolysine": "O"}

AA_ignore_characters = ["*"]

# MIRIAM collections

def return_tuple():
    return ("Unknown", ".*")

Resource = namedtuple("Resource", ['collection', 'display_name', "validator"])

Metabolite_annotations = [Resource("kegg.compound", "KEGG Compound", r"^C\d+$"),
                          Resource("chebi", "CHEBI", r"^CHEBI:\d+$"),
                          Resource("inchi", "InChI", r"^InChI\=1[^ ]*"),
                          Resource("chembank", "ChemBank", r"^\d+$"),
                          Resource("hmdb", "HMDB", r"^HMDB\d{5}$"),
                          Resource("pubchem.compound", "PubChem", r"^\d+$"),
                          Resource("swisslipid", "SwissLipids", r"^SLM:\d+$"),
                          Resource("bigg.metabolite","BiGG Metabolite", r"^[a-z_A-Z0-9]+$"),
                          Resource("metanetx.chemical", "MetaNetX", "^MNXM\d+$")]

Metabolite_annotations = get_resource_dict(Metabolite_annotations)

Reaction_annotations = [Resource("kegg.reaction", "KEGG Reaction", r"^R\d+$"),
                        Resource("rhea", "Rhea", r"^\d{5}$"),
                        Resource("biocyc", "BioCyc", r"^[A-Z-0-9]+(?<!CHEBI)(\:)?[A-Za-z0-9+_.%-]+$"),
                        Resource("sabiork.reaction", "SABIO-RK", r"^\d+$"),
                        Resource("ec-code", "EC code", r"^\d+\.-\.-\.-|\d+\.\d+\.-\.-|\d+\.\d+\.\d+\.-|\d+\.\d+\.\d+\.(n)?\d+$"),
                        Resource("tcdb", "Transport Classification", r"^\d+\.[A-Z]\.\d+\.\d+\.\d+$"),
                        Resource("reactome", "Reactome", r"(^(REACTOME:)?R-[A-Z]{3}-[0-9]+(-[0-9]+)?$)|(^REACT_\d+$)"),
                        Resource("bigg.reaction", "BiGG Reaction", r"^[a-z_A-Z]+$"),
                        Resource("metanetx.reaction", "MetaNetX", r"^MNXR\d+$")]

Reaction_annotations = get_resource_dict(Reaction_annotations)

Gene_annotations = [Resource("interpro", "InterPro", r"^IPR\d{6}$"),
                    Resource("uniprot", "UniProtKB", r"^([A-N,R-Z][0-9]([A-Z][A-Z, 0-9][A-Z, 0-9][0-9]){1,2})|([O,P,Q][0-9][A-Z, 0-9][A-Z, 0-9][A-Z, 0-9][0-9])(\.\d+)?$")]

Gene_annotations = get_resource_dict(Gene_annotations)


Taxonomy_annotations = {"taxonomy": ("NCBI taxonomy", r"^\d+$")}

Compartment_annotations = {"bigg.compartment": ("BiGG Compartment", r"^[a-z_A-Z]+$"),
                           "metanetx.compartment": ("MetaNetX ", r"^MNXC\d+$")}
