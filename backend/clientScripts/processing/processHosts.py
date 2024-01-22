#!/usr/bin/python3

"""
Processes hosts for the output file in the same directory, adds them to the database. argv[1] is the name of service that found the host
"""

import re
from collections import deque
import datetime
import concurrent.futures
import argparse

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

lastIdentifiers = deque([None, None, None, None, None])
def addHost(host):
    global lastIdentifiers, tool

    #Clean host just in case
    cleanHost = scoper.cleanUrl(host) 

    found = False
    try:
        for identifier in lastIdentifiers:
            try:
                if identifier and re.match(scoper.wildcardToRegex(identifier), cleanHost):
                    hostIdentifier = identifier
                    found = True
                    break
            except Exception as e:
                continue
    except Exception as e:
        pass

    if not found:
        hostIdentifier = scoper.findScope(host)
        hostIdentifier = hostIdentifier["_key"] if hostIdentifier else hostIdentifier
        if hostIdentifier: 
            lastIdentifiers.appendleft(hostIdentifier)
            lastIdentifiers.pop()
    
    if not hostIdentifier: 
        print(host)
        return

    #Upsert entry
    db = database.getDatabase()

    aql = """
    UPSERT @search INSERT @insert UPDATE @update IN Hosts
    """
    search = {"_key": cleanHost}
    update = {"_key": cleanHost, "lastDiscovered": datetime.datetime.now().isoformat(), "isActive": True, "webAssetId": hostIdentifier}
    insert = update.copy()
    insert["firstDiscovered"] = insert["lastDiscovered"]

    db.AQLQuery(aql, bindVars={"search": search, "update": update, "insert": insert})

    #Append discovered by
    db = database.getDatabase()
    aql = """
    LET host = DOCUMENT(@host)
    UPDATE {_key: host._key, discoveredBy: APPEND(host.discoveredBy, [@tool], true)} IN Hosts
    """
    db.AQLQuery(aql, bindVars={"host": "Hosts/"+cleanHost, "tool": tool})

    #Draw Edge
    drawEdge(hostIdentifier, cleanHost)

def drawEdge(webAssetId, hostId):
    db = database.getDatabase()
    webAssetId = str(webAssetId)
    hostId = str(hostId)

    #upsert edge
    aql = """
    UPSERT @search INSERT @insert UPDATE @insert IN WebAssetHostLinks
    """

    search = {"_to": "Hosts/"+hostId}
    insert = {"_to": "Hosts/"+hostId, "_from": "WebAssets/"+webAssetId}

    db.AQLQuery(aql, bindVars={"search": search, "insert": insert})

tool = None
if __name__ == "__main__":
    #Output mode
    print("[+] Processing outputs...")

    #Parser stuff
    parser = argparse.ArgumentParser(
        prog = 'python3 processHosts.py',
        description = 'Process the output of hosts and add them to the arango db')
    parser.add_argument('-t', '--tool', type=str, required=True, help='Name of the tool that found the host')
    parser.add_argument('-f', '--file', type=str, required=False, help='Output file to process, by default ./output')
    args = parser.parse_args()
    
    tool = args.tool
    if not args.file:
        args.file = "./output"

    with open(args.file, "r") as f:
        lines = f.readlines()
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
        futures = [executor.submit(addHost, item.strip()) for item in lines]
        concurrent.futures.wait(futures, timeout=None)

    print("[+] Done!")
