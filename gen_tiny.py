#!/usr/bin/env python3

import urllib.request as request
import os
import json
import subprocess
import invert_match
import gen_intermediary_diff
import propagate_names

stitch_url = "https://maven.legacyfabric.net/net/legacyfabric/stitch/{}/stitch-{}-all.jar"

client_path = "./versions/{}/{}-client.jar"
server_path = "./versions/{}/{}-server.jar"
merged_path = "./versions/{}/{}-merged.jar"
tiny_path = "./mappings/{}.tiny"
match_path = "./temp/{}-{}.match"

match_url = "./matches/matches/merged/{}/{}#{}.match"

counter_arg = "-Dstitch.counter=./mappings/counter.txt"


def gen_tiny():
    main_info: dict = read_info()
    infos: list[dict] = main_info["order"]
    renames: dict = main_info["renames"]

    check_stitch()
    if not os.path.exists("./mappings"):
        os.mkdir("./mappings")
    
    for a in os.listdir("./mappings"):
        os.remove("./mappings/{}".format(a))

    if not os.path.exists("./temp"):
        os.mkdir("./temp")

    for info in infos:
        i_from: str = None
        if "from" in info.keys():
            i_from = info["from"]

        i_to: str = info["to"]

        i_conflicts: list[int] = []
        if "conflicts" in info.keys():
            i_conflicts = info["conflicts"]

        i_inverted = False
        if "inverted" in info.keys():
            i_inverted = info["inverted"]

        print("Generating from", i_from, "to", i_to)

        if not i_from == None:
            get_merged_jar(i_from)
        get_merged_jar(i_to)

        if i_from == None:
            generate_intermediary(i_to)
        else:
            i_fol = "april-fools"
            if "fol" in info.keys():
                i_fol = info["fol"]
            update_intermediary(i_from, i_to, i_conflicts, i_inverted, i_fol)

    fix_inner_classes_all()

    for i in renames:
        rename(i, renames[i])

    print("Generate diff between upstream and legacy fabric")
    gen_intermediary_diff.gen_diff("./mappings/18w43b.tiny", "./18w43b-fabricmc.tiny")
    os.remove("./mappings/18w43b.tiny")

    print("Propagating upstream names")
    # propagate_names.propagate_names("./diff.json", "./mappings")
    print("Done")


def update_intermediary(from_name: str, to_name: str, conflicts: list[int], inverted: bool, fol: str):
    print("Generating", to_name, "tiny from", from_name, "one")

    if os.path.exists(tiny_path.format(to_name)):
        os.remove(tiny_path.format(to_name))

    matchPath = match_url.format(fol, from_name, to_name)

    if inverted:
        matchPath = match_path.format(from_name, to_name)

    if inverted:
        invert_match.invert(
            match_url.format(fol, to_name, from_name),
            match_path.format(from_name, to_name)
        )

    args = ["java", counter_arg, "-jar", "./stitch.jar", "updateIntermediary",
            merged_path.format(from_name, from_name),
            merged_path.format(to_name, to_name),
            tiny_path.format(from_name),
            tiny_path.format(to_name),
            matchPath
            ]

    if len(conflicts) > 0:
        conf = None
        for i in conflicts:
            if conf == None:
                conf = str(i)
            else:
                conf = conf + " " + str(i)
        args.append("-c")
        args.append(conf)

    subprocess.run(args)

    if inverted:
        os.remove(match_path.format(from_name, to_name))


def generate_intermediary(version_name: str):
    print("Generating", version_name, "tiny")

    if os.path.exists(tiny_path.format(version_name)):
        os.remove(tiny_path.format(version_name))

    subprocess.run(["java", counter_arg, "-jar", "./stitch.jar", "generateIntermediary",
                    merged_path.format(version_name, version_name),
                    tiny_path.format(version_name)
                    ])


def get_merged_jar(version_name: str):
    if not os.path.exists("./versions"):
        os.mkdir("./versions")
    if not os.path.exists("./versions/{}".format(version_name)):
        os.mkdir("./versions/{}".format(version_name))

    if not os.path.exists(merged_path.format(version_name, version_name)):
        with open("./matches/mc-versions/data/version/{}.json".format(version_name), 'r') as response:
            versionStr = response.read()
            versionJson = json.loads(versionStr)
            downloads = versionJson["downloads"]
            client_jar = downloads["client"]["url"]
            server_jar = downloads["server"]["url"]

            if not os.path.exists(client_path.format(version_name, version_name)):
                print("Downloading", version_name, "client")
                with request.urlopen(client_jar) as response:
                    with open(client_path.format(version_name, version_name), 'wb') as client:
                        client.write(response.read())
                        client.close()
                        print("Client downloaded")

            if not os.path.exists(server_path.format(version_name, version_name)):
                print("Downloading", version_name, "server")
                with request.urlopen(server_jar) as response:
                    with open(server_path.format(version_name, version_name), 'wb') as server:
                        server.write(response.read())
                        server.close()
                        print("Server downloaded")

            print("Merging", version_name, "client and server")
            subprocess.run(["java", "-jar", "./stitch.jar", "mergeJar",
                            client_path.format(version_name, version_name),
                            server_path.format(version_name, version_name),
                            merged_path.format(version_name, version_name),
                            "--removeSnowman", "--syntheticparams"
                            ])


def read_info():
    dic = {}
    with open("./gen_tiny_info.json", 'r') as info:
        dic = json.load(info)
        info.close()
    return dic


def check_stitch():
    if not os.path.exists("./stitch.jar"):
        print("Downloading stitch")
        with request.urlopen("https://maven.legacyfabric.net/net/legacyfabric/stitch/maven-metadata.xml") as response:
            metadata = response.read().decode('utf-8')
            stitch_version = metadata.split("<latest>")[1].split("</latest>")[0]
            with request.urlopen(stitch_url.format(stitch_version, stitch_version)) as response:
                with open("./stitch.jar", 'wb') as stitch:
                    stitch.write(response.read())
                    stitch.close()
                    print("Stitch downloaded")


def fix_inner_classes_all():
    print("Fixing inner classes...")
    for i in os.listdir("./mappings"):
        if i.endswith(".tiny"):
            fix_inner_classes(i)


def fix_inner_classes(file_name: str):
    with open("./mappings/{}".format(file_name), 'r') as read_file:
        content = read_file.read()
        read_file.close()
        content_array = content.split("\n")
        class_array = {}
        content_array_array = []

        for i in content_array:
            content_array_array.append(i.split("\t"))

        for i in range(len(content_array_array)):
            ii = content_array_array[i]

            if ii[0] == "CLASS":
                class_array[ii[1]] = ii[2]

        for i in class_array.keys():
            if "$" in i:
                o_parts: list[str] = i.split("$")
                d_full: str = class_array[i]

                d_last = ""
                if "$" in d_full:
                    d_last = d_full.split("$").pop()
                else:
                    d_last = d_full.split("/").pop()

                o_parts.pop()
                class_array[i] = class_array["$".join(o_parts)] + "$" + d_last

        content_array.clear()
        for i in range(len(content_array_array)):
            ii = content_array_array[i]

            if ii[0] == "CLASS":
                ii[2] = class_array[ii[1]]

            content_array.append("\t".join(ii))

        file_content = "\n".join(content_array)

        with open("./mappings/{}".format(file_name), 'w') as writable:
            writable.write(file_content)
            writable.close()


def rename(old_name: str, new_name: str):
    if os.path.exists(tiny_path.format(new_name)):
        os.remove(tiny_path.format(new_name))
    if os.path.exists(tiny_path.format(old_name)):
        os.rename(tiny_path.format(old_name), tiny_path.format(new_name))


if __name__ == '__main__':
    gen_tiny()
