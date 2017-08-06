from collections import Counter
from facts import AA_names

def add_AA_sequence_to_reactions(AA_sequence, AA_Metabolite_Map):
    AA_Stoichiometry = Counter(AA_sequence)
    metabolite_stoichiometry = shortcut_mappings(AA_Stoichiometry, AA_Metabolite_Map)
    return metabolite_stoichiometry


def shortcut_mappings(value_source, key_source):
    """
    Combine dictionaries into new mapping by matching keys
    """
    common_keys = set(value_source.keys()).intersection(set(key_source.keys()))
    return dict((key_source[x], value_source[x]) for x in common_keys)

def parse_fasta_string(input_stream):
    proteins = []
    current_item = []
    for i, line in enumerate(input_stream):
        if line.strip() == "":
            continue
        elif line.startswith(">"):
            if current_item:
                proteins.append("".join(current_item))
                current_item = []
        else:
            current_item.append(line.strip("\n").upper())
    return proteins

if __name__ == "__main__":
    inversed_mapping = dict((value, key) for key, value in AA_names.items())
    with open(r"C:\Coding\GEM Editor\testdev\Aspni7_GeneCatalog_proteins_20131226.aa_2.fasta", "r") as open_file:
        prot_file = parse_fasta_string(open_file)
        for element in prot_file[:5]:
            print(add_AA_sequence_to_reactions(element, inversed_mapping))

