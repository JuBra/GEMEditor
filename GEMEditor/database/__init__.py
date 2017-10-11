from os.path import join, abspath, dirname
from collections import namedtuple, defaultdict

database_path = abspath(join(dirname(abspath(__file__)), "modelling.db"))

# MetaNetX files
metanetx_url = "ftp://ftp.vital-it.ch/databases/metanetx/MNXref/latest/"
metanetx_files = {"Metabolites": "chem_prop.tsv",
                  "MetaboliteLinks": "chem_xref.tsv",
                  "Reactions": "reac_prop.tsv",
                  "ReactionLinks": "reac_xref.tsv",
                  "Compartments": "comp_prop.tsv"}


# Databases that have been mapped by MetaNetX
Database = namedtuple('Database', ["mnx_prefix", "name", "type", "miriam_collection", "validator"])
miriam_databases = [Database("mnx", 'MetaNetX Chemical', "metabolite", 'metanetx.chemical', r"^MNXM\d+$"),
                    Database('chebi', 'ChEBI', "metabolite", 'chebi', r"^CHEBI:\d+$"),
                    Database('kegg', 'KEGG Compound', "metabolite", 'kegg.compound', r"^C\d+$"),
                    Database('kegg', 'KEGG Drug', "metabolite", 'kegg.drug', r"^D\d+$"),
                    Database('kegg', 'KEGG Glycan', "metabolite", 'kegg.glycan', r"^G\d+$"),
                    Database('kegg', 'KEGG Environ', "metabolite", 'kegg.environ', r"^(ev\:)?E\d+$"),
                    Database('metacyc', 'MetaCyc Metabolite', "metabolite", None, r".*"),
                    Database('upa', 'UniPathway Compound', "metabolite", "unipathway.compound", r"^UPC\d{5}$"),
                    Database('seed', 'SEED Compound', "metabolite", 'seed.compound', r"^cpd\d+$"),
                    Database('bigg', 'BiGG Metabolite', "metabolite", 'bigg.metabolite', r"^[a-z_A-Z0-9]+$"),
                    Database('biopath', "BioPath Metabolite", "metabolite", None, r".*"),
                    Database('lipidmaps', 'Lipid Maps', "metabolite", 'lipidmaps', r"^LM(FA|GL|GP|SP|ST|PR|SL|PK)[0-9]{4}([0-9a-zA-Z]{4,6})?$"),
                    Database('hmdb', 'Human Metabolome Database', "metabolite", 'hmdb', r"^HMDB\d{5}$"),
                    Database('reactome', 'Reactome', "metabolite", 'reactome', r"(^(REACTOME:)?R-[A-Z]{3}-[0-9]+(-[0-9]+)?$)|(^REACT_\d+$)"),
                    Database('umbbd', 'UM-BBD Compound', "metabolite", 'umbbd.compound', r"^c\d+$"),
                    Database(None, 'InChI', "metabolite", 'inchi', r"^InChI\=1S\/[A-Za-z0-9]+(\/[cnpqbtmsih][A-Za-z0-9\-\+\(\)\,]+)+$"),

                    # Reactions
                    Database('mnx', 'MetaNetX Reaction', "reaction", 'metanetx.reaction', r"^MNXR\d+$"),
                    Database('rhea', 'Rhea', "reaction", 'rhea', r"^\d{5}$"),
                    Database('kegg', 'KEGG Reaction', "reaction", 'kegg.reaction', r"^R\d+$"),
                    Database('metacyc', 'MetaCyc Reaction', "reaction", None, r".*"),
                    Database('upa', 'UniPathway Reaction', "reaction", "unipathway.reaction", r"^UCR\d{5}$"),
                    Database('seed', 'SEED Reaction', "reaction", None, r".*"),
                    Database('bigg', 'BiGG Reaction', "reaction", 'bigg.reaction', r"^[a-z_A-Z0-9]+$"),
                    Database('biopath', "BioPath Reaction", "reaction", None, r".*"),
                    Database('reactome', 'Reactome', "reaction", 'reactome', r"(^(REACTOME:)?R-[A-Z]{3}-[0-9]+(-[0-9]+)?$)|(^REACT_\d+$)"),
                    Database(None, 'EC code', "reaction", "ec-code", r"^\d+\.-\.-\.-|\d+\.\d+\.-\.-|\d+\.\d+\.\d+\.-|\d+\.\d+\.\d+\.(n)?\d+$")]


# The chebi and reactome identifier are missing their respective identifiers
missing_prefix = defaultdict(str)
missing_prefix["chebi"] = "CHEBI:"
missing_prefix["reactome"] = "REACT_"


# Some collections have been merged by MetaNetX
metabolite_ambiguitiy_map = {"kegg": ["kegg.compound",
                                      "kegg.drug",
                                      "kegg.glycan",
                                      "kegg.environ"],
                             "bigg": 'bigg.metabolite',
                             "seed": 'seed.compound',
                             "umbbd": 'umbbd.compound'}

reaction_ambiguitiy_map = {"kegg": 'kegg.reaction',
                           "bigg": 'bigg.reaction'}
