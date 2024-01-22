#!/usr/bin/python3

import json

with open("results.txt", "r") as f:
    for line in f.readlines():
        jsonData = json.loads(line)
        if jsonData["status"] != "NOERROR":
            if jsonData["status"] == "NXDOMAIN":
                #TODO set resolves to false in db
                print("[-]", jsonData["name"])
        elif "data" in jsonData: 
            if "answers" in jsonData["data"]:
                for answer in jsonData["data"]["answers"]:
                    if answer["type"] == "A":
                        #TODO database stuff
                        print("[+]", answer["name"], "->", answer["data"])
                    elif answer["type"] == "CNAME":
                        #TODO database stuff
                        print("[*]", answer["name"], "->", answer["data"])
                    else:
                        print("[!] NEW TYPE: %s"%answer["type"])
             
            if "additionals" in jsonData["data"]:
                for additional in jsonData["data"]["additionals"]:
                    if additional["type"] == "A":
                        #TODO database stuff
                        print("[+]", additional["name"], "->", additional["data"])
                    elif additional["type"] == "AAAA":
                        #TODO database stuff
                        print("[+]", additional["name"], "->", additional["data"])
                    elif additional["type"] == "41":
                        #Sus but im just gonna pass for now
                        pass
                    else:
                        print("[!] NEW TYPE: %s"%additional["type"])
