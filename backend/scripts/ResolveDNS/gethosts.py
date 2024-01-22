#!/usr/bin/python3

"""
Generates the input file
"""

import re
import datetime

import sys
import os
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    os.pardir)
)
sys.path.append(PROJECT_ROOT)

import modules.arangodb as database
import modules.scoper as scoper

def getHosts():
    db = database.getDatabase()

    aql = """
    FOR host IN Hosts
        FILTER host.isActive
        RETURN host._key
    """

    return db.AQLQuery(aql, rawResults=True, batchSize=100)

if __name__ == "__main__":
    #Input Mode
    hostsBatch = getHosts()

    #Pre retrieve batches
    hosts = []
    for host in hostsBatch:
        hosts.append(host)

    with open("input.txt", "w") as f:
        for host in hosts:
            #Remove wildcard identifier things
            host = host.replace("*.", "")
            host = host.replace("*", "")

            f.write(host+"\n")
