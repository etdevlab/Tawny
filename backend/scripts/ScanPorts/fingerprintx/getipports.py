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

def getIpPorts():
    db = database.getDatabase()

    aql = """
    FOR ip IN IPs
        FILTER ip.isActive
        FILTER COUNT(ip.ports) > 0
        FOR port IN ip.ports
            RETURN CONCAT(ip._key, ":", port)
    """

    return db.AQLQuery(aql, rawResults=True, batchSize=100)

if __name__ == "__main__":
    #Input Mode
    ipPortsBatch = getIpPorts()

    #Pre retrieve batches
    ipPorts = []
    for ipPort in ipPortsBatch:
        ipPorts.append(ipPort)

    with open("input.txt", "w") as f:
        for ipPort in ipPorts:
            f.write(ipPort+"\n")
