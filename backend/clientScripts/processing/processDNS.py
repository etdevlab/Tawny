#!/usr/bin/python3

#TODO cleanup

"""
Process the results from massdns and add them to the database
"""

import json
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

def cleanName(name):
    if name.endswith("."):
        return name[:-1]

def setHostResponse(name, response=False, data=None, isAdditional=False):
    name = cleanName(name)

    db = database.getDatabase()
    if not response:
        aql = """
        UPDATE @key WITH {hostResolves: false} IN Hosts
        """
        try:
            db.AQLQuery(aql, bindVars={"key": name})
        except database.pyArango.theExceptions.AQLQueryError as e:
            #Document not found, not gonna bother with hosts that don't resolve to try and check their scope
            pass
    else:
        isCNAME = False
        if data["type"] == "CNAME":
            isCNAME = True

        aql = """
        UPDATE @key WITH {hostResolves: true, lastResolved: @now, isCNAME: @isCNAME} IN Hosts
        """
        try:
            db.AQLQuery(aql, bindVars={"key": name, "now": datetime.datetime.now(), "isCNAME": isCNAME})
        except database.pyArango.theExceptions.AQLQueryError as e:
            #If its some additional data, ignore it, otherwise keep the IP still bc it could be in scope
            if isAdditional:
                return
            else:
                name = cleanName(data["ogName"])
                try:
                    db.AQLQuery(aql, bindVars={"key": name, "now": datetime.datetime.now(), "isCNAME": isCNAME})
                except database.pyArango.theExceptions.AQLQueryError as e:
                    print("[!]", e)
                    return

        if not isCNAME:
            addIpEntry(data, name)
        else:
            drawEdge(data, name)

def addIpEntry(data, name):
    db = database.getDatabase()

    ipType = "ipv4"
    if data["type"] == "AAAA":
        ipType = "ipv6"

    aql = """
    UPSERT @search INSERT @insert UPDATE @update IN IPs
    """
    search = {"_key": data["data"]}
    update = {"_key": data["data"], "lastDiscovered": datetime.datetime.now().isoformat(), "isActive": True, "type": ipType}
    insert = update.copy()
    insert["firstDiscovered"] = insert["lastDiscovered"]

    db.AQLQuery(aql, bindVars={"search": search, "insert": insert, "update": update})

    #Append host and discoveredBy
    db = database.getDatabase()
    aql = """
    LET ip = DOCUMENT(@ip)
    UPDATE {_key: ip._key, discoveredBy: APPEND(ip.discoveredBy, [@discovery], true), hosts: APPEND(ip.hosts, [@host], true)} IN IPs
    """
    db.AQLQuery(aql, bindVars={"ip": "IPs/"+str(data["data"]), "discovery": "MassDNS", "host": name})
    drawEdge(data, name)

def drawEdge(data, name):
    db = database.getDatabase()
    
    ipType = data["type"]
    aql = """
    UPSERT @search INSERT @insert UPDATE @update IN DNSEdges
    """

    to = "IPs/"+data["data"]
    if ipType == "CNAME":
        to = "Hosts/"+cleanName(data["data"])

    search = {"_to": to, "_from": "Hosts/"+name, "type": ipType}
    update = search.copy()
    update["lastFound"] = datetime.datetime.now()
    insert = update.copy()
    insert["firstFound"] = insert["lastFound"]

    db.AQLQuery(aql, bindVars={"search": search, "insert": insert, "update": update})

if __name__ == "__main__":
    with open("results.txt", "r") as f:
        for line in f.readlines():
            jsonData = json.loads(line)
            if jsonData["status"] != "NOERROR":
                if jsonData["status"] == "NXDOMAIN":
                    #Domains that don't resolve, just set hostResolves to false in arangodb
                    print("[-]", jsonData["name"])
                    setHostResponse(jsonData["name"])

            elif "data" in jsonData: 
                if "answers" in jsonData["data"]:
                    for answer in jsonData["data"]["answers"]:
                        if answer["type"] == "A":
                            print("[+]", answer["name"], "->", answer["data"])
                            answer["ogName"] = jsonData["name"]
                            setHostResponse(answer["name"], True, answer)
                        elif answer["type"] == "CNAME":
                            print("[*]", answer["name"], "->", answer["data"])
                            answer["ogName"] = jsonData["name"]
                            setHostResponse(answer["name"], True, answer)
                        else:
                            print("[!] NEW TYPE: %s"%answer["type"])
                 
                if "additionals" in jsonData["data"]:
                    for additional in jsonData["data"]["additionals"]:
                        if additional["type"] == "A":
                            print("[+]", additional["name"], "->", additional["data"])
                            setHostResponse(additional["name"], True, additional, True)
                        elif additional["type"] == "AAAA":
                            print("[+]", additional["name"], "->", additional["data"])
                            setHostResponse(additional["name"], True, additional, True)
                        elif additional["type"] == "41":
                            #Sus but im just gonna pass for now
                            pass
                        else:
                            print("[!] NEW TYPE: %s"%additional["type"])
