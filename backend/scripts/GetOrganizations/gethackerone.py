#!/usr/bin/python3

"""
Get programs from HackerOne and put them into ArangoDB
"""

import requests
import json
import datetime
import base64

import sys
import os
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    os.pardir)
)

sys.path.append(PROJECT_ROOT)
import modules.h1vars as h1vars
import modules.arangodb as database

def getBase64Image(url):
    r = requests.get(url)
    if r.ok:
        base64Content = base64.b64encode(r.content).decode("utf-8")
        if len(base64Content) > 20000:
            return None
        return "data:image/png;base64,%s"%base64Content
    else:
        return None
def addProgram(programData):
    #Adds le programs
    programData["lastActive"] = datetime.datetime.now().isoformat()
    programData["isActive"] = True
    programData["_key"] = "H1_"+str(programData["programId"])
    programData["source"] = "HackerOne"
    programData.pop("programId")

    db = database.getDatabase()

    aql = "UPSERT @search INSERT @insert UPDATE @update IN Organizations"
    search = {"_key": str(programData["_key"])}
    
    insert = programData.copy()
    insert["firstAdded"] = programData["lastActive"]

    db.AQLQuery(aql, bindVars={"search": search, "insert": insert, "update": programData})

    print("[+] %s"%programData["handle"])

start = datetime.datetime.now()
def deactivateOldPrograms():
    #Mark isActive as false for programs where lastActive is more than 60 days old
    global start
    timeThreshold = start - datetime.timedelta(days=60)
    timeThreshold = timeThreshold.isoformat()
   
    aql = "for organization in Organizations\nfilter organization.lastActive < @time\nUPDATE {_key: organization._key, isActive: false} in Organizations\nreturn organization.handle"
    queryResult = database.getDatabase().AQLQuery(aql, bindVars={"time": str(timeThreshold)})

    print("[-] HackerOne Organizations marked as inactive: %s"%(len(queryResult)))

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
            programData["base64Image"] = getBase64Image(program["attributes"]["profile_picture"])
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
