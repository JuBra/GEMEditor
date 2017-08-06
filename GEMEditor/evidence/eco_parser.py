from os.path import abspath, dirname, join


class EvidenceCode:

    def __init__(self, id=None):
        self.id = id
        self.name = None
        self.definition = None
        self.synonyms = set()
        self.parents = set()
        self.children = set()

    def __str__(self):
        return "Eco: {id}\n" \
               "Name: {name}\n" \
               "Definition: {definition}\n".format(id=self.id, name=self.name, definition=self.definition)


def parse_eco(path):
    """ Parse the evidence codes provided by https://github.com/evidenceontology/evidenceontology"""

    all_ecos = dict()
    relationshipts = []
    with open(path, "r") as open_file:
        new_eco = None
        is_obsolete = False
        for line in open_file:
            line = line.strip()
            if "[Term]" in line:
                if new_eco is not None and not is_obsolete:
                    all_ecos[new_eco.id] = new_eco
                new_eco = EvidenceCode()
                is_obsolete = False
                continue
            elif "[Typedef]" in line:
                if new_eco is not None and not is_obsolete:
                    all_ecos[new_eco.id] = new_eco
                new_eco = None
                is_obsolete = False
                continue
            elif new_eco is None:
                continue

            split_line = line.split(" ")
            if split_line[0] == "id:":
                new_eco.id = split_line[1]
            elif split_line[0] == "name:":
                new_eco.name = " ".join(split_line[1:])
            elif split_line[0] == "def:":
                new_eco.definition = " ".join(split_line[1:])
            elif split_line[0] == "is_a:":
                relationshipts.append((split_line[1], new_eco.id))
            elif split_line[0] == "synonym:":
                new_eco.synonyms.add(" ".join(split_line[1:]))
            elif split_line[0] == "is_obsolete:":
                is_obsolete = True
        if new_eco:
            all_ecos[new_eco.id] = new_eco

    # Link parents to children
    for link in relationshipts:
        parent = all_ecos[link[0]]
        child = all_ecos[link[1]]
        parent.children.add(child)
        child.parents.add(parent)
    return all_ecos

all_ecos = parse_eco(abspath(join(dirname(abspath(__file__)), "eco.obo")))