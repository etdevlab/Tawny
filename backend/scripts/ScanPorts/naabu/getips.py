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
    os.pardir,
    os.pardir)
)
sys.path.append(PROJECT_ROOT)

import modules.arangodb as database
import modules.scoper as scoper

def getIps():
    db = database.getDatabase()

    aql = """
    FOR ip IN IPs
        FILTER ip.isActive
        RETURN ip._key
    """

    return db.AQLQuery(aql, rawResults=True, batchSize=100)

if __name__ == "__main__":
    #Input Mode
    ipsBatch = getIps()

    #Pre retrieve batches
    ips = []
    for ip in ipsBatch:
        ips.append(ip)

    with open("input.txt", "w") as f:
        for ip in ips:
            #Remove wildcard identifier things
            ip = ip.replace("*.", "")
            ip = ip.replace("*", "")

            f.write(ip+"\n")
