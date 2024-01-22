#!/usr/bin/python3

import requests
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
import modules.h1vars as h1vars
import modules.neo4jDatabase as database

def addProgram(programData):
    #Adds le programs
    programData["rightNow"] = datetime.datetime.now().isoformat()
    programData["lastActive"] = datetime.datetime.now().isoformat()
    programData["isActive"] = True

    with database.getDriver().session() as session:
        query = "MERGE (p:Program {programId: $programId}) ON CREATE SET p.firstAdded = $rightNow SET"
        for key in programData:
            if key == "rightNow" or key == "programId":
                continue
            query += " p.%s = $%s,"%(key, key)
        query = query[:-1]

        session.run(query, programData)

    print("[+] %s"%programData["handle"])

start = datetime.datetime.now()
def deactivateOldPrograms():
    #Mark isActive as false for programs where lastActive is more than 10 days old
    global start
    timeThreshold = start - datetime.timedelta(days=10)
    timeThreshold = timeThreshold.isoformat()
    with database.getDriver().session() as session:
        query = "MATCH (p:Program) WHERE p.isActive and p.lastActive < $timeThreshold SET p.isActive = false RETURN p"
        result = session.run(query, {"timeThreshold": timeThreshold})
        print("[-] Programs marked as inactive: %s"%(len([record for record in result])))

if __name__ == "__main__":
    auth = h1vars.getH1Auth()
    added = 0

    page = 1
    url = "https://api.hackerone.com/v1/hackers/programs?page%5Bsize%5D=100"

    while url:
        r = requests.get(url, auth=auth)

        returned = json.loads(r.text)
        data = returned["data"]
        
        for program in data:
            programData = {}

            programData["programId"] = program["id"]
            programData["type"] = program["type"]
            programData.update(program["attributes"])

            if programData["state"] == "public_mode": programData["isPrivate"] = False
            else: programData["isPrivate"] = True

            addProgram(programData)
            added += 1

        url = None
        links = returned["links"]
        if 'next' in links:
            url = links['next']
            page += 1

    deactivateOldPrograms()
    print("[*] %s programs added or updated"%added)
