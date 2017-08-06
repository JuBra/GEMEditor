from collections import Counter

line_counter = Counter()
with open("chem_prop.tsv") as open_file:
    for line in open_file:
        if line.startswith("#"):
            continue

        split_line = line.split("\t")
        num_columns = len(split_line)
        line_counter[num_columns] += 1

print(line_counter)