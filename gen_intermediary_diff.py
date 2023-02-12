import json
import re


def gen_diff(temp: str, upstream: str):
    temp_dict = {}
    upstream_dict = {}

    with open(temp, 'r') as tempFile:
        tempFile.readline()

        for i in tempFile.readlines():
            *key, value = i.strip("\n").split("\t")
            if not re.match("[a-zA-Z/$]+(_0)?_[0-9]+", value):
                continue
            temp_dict[tuple(key)] = value
    with open(upstream, 'r') as upstreamFile:
        upstreamFile.readline()

        for i in upstreamFile.readlines():
            *key, value = i.strip("\n").split("\t")
            if not re.match("[a-zA-Z/$]+(_0)?_[0-9]+", value):
                continue
            upstream_dict[tuple(key)] = value

    final_dict = {}
    for i in temp_dict.keys():
        if i not in upstream_dict.keys():
            print("Missing upstream:", i, temp_dict[i])
            continue

        key = temp_dict[i]

        if '/' in key:
            if '$' in key:
                key = key.split("$")[-1]
            else:
                key = key.split("/")[-1]

        val = upstream_dict[i]

        if '/' in val:
            if '$' in val:
                val = val.split("$")[-1]
            else:
                val = val.split("/")[-1]

        final_dict[key] = val

    with open("diff.json", 'w') as diffFile:
        diffFile.write(json.dumps(final_dict))


if __name__ == "__main__":
    import sys
    gen_diff(sys.argv[1], sys.argv[2])
