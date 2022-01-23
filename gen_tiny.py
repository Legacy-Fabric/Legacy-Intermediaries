#!/usr/bin/env python3

import urllib.request as request
import os
import json
import subprocess

client_path = "./versions/{}/{}-client.jar"
server_path = "./versions/{}/{}-server.jar"
merged_path = "./versions/{}/{}-merged.jar"

counter_arg = "--stitch.counter=./mappings/counter.txt"

def gen_tiny():
    infos: list[dict] = read_info()["order"]
    check_stitch()

    for info in infos:
        i_from: str = None
        if "from" in info.keys():
            i_from = info["from"]
        
        i_to: str = info["to"]

        i_conflicts: list[int] = []
        if "conflicts" in info.keys():
            i_conflicts = info["conflicts"]
        
        print("Generating from", i_from, "to", i_to)

        if not i_from == None:
            get_merged_jar(i_from)
        get_merged_jar(i_to)

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
            stitch_version = metadata.split("<latest>")[1].split("</latest>")[0]
            with request.urlopen("https://maven.fabricmc.net/net/fabricmc/stitch/{}/stitch-{}-all.jar".format(stitch_version, stitch_version)) as response:
                with open("./stitch.jar", 'wb') as stitch:
                    stitch.write(response.read())
                    stitch.close()
                    print("Stitch downloaded")

if __name__ == '__main__':
    gen_tiny()