#!/usr/bin/python3

import os

with open("../wildcards.txt", "r") as f:
    for line in f.readlines():
        line = line.replace("*.", "")
        line = line.strip()
        if not line: continue
        os.system("echo '%s' | anew ../subdomains.txt"%line) 
