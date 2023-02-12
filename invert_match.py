#!/usr/bin/env python3
# usage: python3 invert_match.py <match_location> <inverted_match_location>

import sys


def invert(path, new_path):
    with open(path) as match_file:
        string = match_file.read()
        lines = string.splitlines()
        parse(lines, new_path)
        match_file.close()


def parse(lines: list[str], new_path):
    match_infos = {
        "title": lines.pop(0),
        "a": [],
        "b": [],
        "cp": [],
        "cp_a": [],
        "cp_b": [],
        "lines": []
    }

    lines, match_infos = category(lines, "a", match_infos)
    lines, match_infos = category(lines, "b", match_infos)
    lines, match_infos = category(lines, "cp", match_infos)
    lines, match_infos = category(lines, "cp_a", match_infos)
    lines, match_infos = category(lines, "cp_b", match_infos)

    while len(lines) > 0:
        line = lines.pop(0)
        match_infos["lines"].append(line.split("\t"))

    match_infos = invert_object(match_infos)

    write(new_path, match_infos)


def write(new_path, obj):
    lines = [
                obj["title"],
                "\ta:"
            ] + obj["a"] + ["\tb:"] + obj["b"] + ["\tcp:"] + obj["cp"] + ["\tcp a:"] + obj["cp_a"] + ["\tcp b:"] + obj[
                "cp_b"] + obj["lines"]

    txt = ""

    for i in lines:
        txt += i + "\n"

    with open(new_path, 'w') as newFile:
        newFile.write(txt)
        newFile.close()


def category(lines: list[str], name: str, obj: dict):
    if lines[0].startswith("\t" + name.replace("_", " ")):
        lines.pop(0)

    line = lines.pop(0)
    while line.startswith("\t\t"):
        obj[name].append(line)
        line = lines.pop(0)

    lines.insert(0, line)

    return lines, obj


def invert_object(match_infos: dict):
    match_infos["c"] = match_infos["a"]
    match_infos["a"] = match_infos["b"]
    match_infos["b"] = match_infos["c"]

    match_infos["cp_c"] = match_infos["cp_a"]
    match_infos["cp_a"] = match_infos["cp_b"]
    match_infos["cp_b"] = match_infos["cp_c"]

    for i in range(0, len(match_infos["lines"])):
        line = match_infos["lines"][i]

        if line[0] == "c":
            line[0] = line[1]
            line[1] = line[2]
            line[2] = line[0]
            line[0] = "c"
        elif line[1] == "m" or line[1] == "f":
            line[0] = line[2]
            line[2] = line[3]
            line[3] = line[0]
            line[0] = ""
        elif line[2] == "ma":
            line[0] = line[3]
            line[3] = line[4]
            line[4] = line[0]
            line[0] = ""

        str_line = ""
        for g in line:
            str_line += g + "\t"

        str_line = str_line.removesuffix("\t")

        match_infos["lines"][i] = str_line

    return match_infos


if __name__ == '__main__':
    invert(sys.argv[1], sys.argv[2])
