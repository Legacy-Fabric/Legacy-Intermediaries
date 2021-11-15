#!/usr/bin/env python3
# usage: python3 invert_match.py <match_location> <inverted_match_location>

import sys

def invert(path, newPath):
    with open(path) as match:
        string = match.read()
        lines = string.splitlines()
        parse(lines, newPath)
        match.close()
        
def parse(lines: list[str], newPath):
    obj = {
        "title": lines.pop(0),
        "a": [],
        "b": [],
        "cp": [],
        "cp_a": [],
        "cp_b": [],
        "lines": []
    }

    lines, obj = category(lines, "a", obj)
    lines, obj = category(lines, "b", obj)
    lines, obj = category(lines, "cp", obj)
    lines, obj = category(lines, "cp_a", obj)
    lines, obj = category(lines, "cp_b", obj)

    while len(lines) > 0:
        line = lines.pop(0)
        obj["lines"].append(line.split("\t"))
    
    obj = invert_object(obj)

    write(newPath, obj)

def write(newPath, obj):
    lines = [
        obj["title"],
        "\ta:"
    ] + obj["a"] + ["\tb:"] + obj["b"] + ["\tcp:"] + obj["cp"] + ["\tcp a:"] + obj["cp_a"] + ["\tcp b:"] + obj["cp_b"] + obj["lines"]

    txt = ""

    for i in lines:
        txt += i + "\n"
    
    with open(newPath, 'w') as newFile:
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

    return (lines, obj)

def invert_object(obj: dict):

    obj["c"] = obj["a"]
    obj["a"] = obj["b"]
    obj["b"] = obj["c"]

    obj["cp_c"] = obj["cp_a"]
    obj["cp_a"] = obj["cp_b"]
    obj["cp_b"] = obj["cp_c"]

    for i in range(0, len(obj["lines"])):
        line = obj["lines"][i]

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
        
        strLine = ""
        for g in line:
            strLine += g + "\t"
        
        strLine.removesuffix("\t")

        obj["lines"][i] = strLine
    
    return obj


if __name__ == '__main__':
    invert(sys.argv[1], sys.argv[2])