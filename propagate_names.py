import json
import os
import sys


def propagate_names(diff_path: str, mappings_path: str):
    with open(diff_path, 'r') as diff_file:
        diff_dict = json.loads(diff_file.read())

    for i in os.listdir(mappings_path):
        if i == "counter.txt":
            continue

        with open(mappings_path + "/" + i, 'r') as f:
            lines = [transform_line(line, diff_dict) + "\n" for line in f.readlines()]
        with open(mappings_path + "/" + i, 'w') as f:
            f.writelines(lines)


def transform_line(line: str, dic: dict):
    line_parts = line.strip("\n").split("\t")

    match line_parts[0]:
        case "CLASS":
            class_path = line_parts[-1].split("/")
            names = class_path[-1].split("$")
            names = [transform(key, dic) for key in names]
            class_path[-1] = '$'.join(names)
            line_parts[-1] = '/'.join(class_path)
        case "FIELD" | "METHOD":
            line_parts[-1] = transform(line_parts[-1], dic)

    return '\t'.join(line_parts)


def transform(key: str, dic: dict):
    if (var := dic.get(key)) is not None:
        return var
    else:
        return key


if __name__ == "__main__":
    propagate_names(sys.argv[1], sys.argv[2])
