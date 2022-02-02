#!/usr/bin/env python3

import urllib.request as request
import os
import json
import subprocess
import invert_match

# stitch_url = "https://maven.fabricmc.net/net/fabricmc/stitch/{}/stitch-{}-all.jar"
stitch_url = "https://jitpack.io/com/github/arthurbambou/stitch/{}/stitch-{}-all.jar"

client_path = "./versions/{}/{}-client.jar"
server_path = "./versions/{}/{}-server.jar"
merged_path = "./versions/{}/{}-merged.jar"
tiny_path = "./mappings/{}.tiny"
match_path = "./matches/{}-{}.match"

counter_arg = "-Dstitch.counter=./mappings/counter.txt"

def gen_tiny():
    infos: list[dict] = read_info()["order"]
    check_stitch()
    if not os.path.exists("./mappings"):
        os.mkdir("./mappings")

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
            update_intermediary(i_from, i_to, i_conflicts, i_inverted)

def update_intermediary(from_name: str, to_name: str, conflicts: list[int], inverted: bool):
    print("Generating", to_name, "tiny from", from_name, "one")

    if os.path.exists(tiny_path.format(to_name)):
        os.remove(tiny_path.format(to_name))
    
    if inverted:
        invert_match.invert(
            match_path.format(to_name, from_name),
            match_path.format(from_name, to_name)
        )

    args = ["java", counter_arg, "-jar", "./stitch.jar", "updateIntermediary",
                merged_path.format(from_name, from_name),
                merged_path.format(to_name, to_name),
                tiny_path.format(from_name),
                tiny_path.format(to_name),
                match_path.format(from_name, to_name)
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
        with request.urlopen('https://raw.githubusercontent.com/skyrising/mc-versions/main/data/version/{}.json'.format(version_name)) as response:
            versionStr = response.read().decode('utf-8');
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
        with request.urlopen("https://maven.fabricmc.net/net/fabricmc/stitch/maven-metadata.xml") as response:
            metadata = response.read().decode('utf-8')
            # stitch_version = metadata.split("<latest>")[1].split("</latest>")[0]
            stitch_version = "55c648c8d8"
            with request.urlopen(stitch_url.format(stitch_version, stitch_version)) as response:
                with open("./stitch.jar", 'wb') as stitch:
                    stitch.write(response.read())
                    stitch.close()
                    print("Stitch downloaded")

if __name__ == '__main__':
    gen_tiny()