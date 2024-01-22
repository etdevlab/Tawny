#!/usr/bin/python3

"""
This will be used to get the structured assets from organizations
- assets put into arangodb
- connections made between assets and their parent organization
"""

import requests
import json
import argparse
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
import modules.h1vars as h1vars

def getHandleFromOrganizationId(organizationId):
    col = database.getCollection("Organizations")
    
    try:
        return col[organizationId]["handle"]
    except:
        print("[-] OrganizationId %s does not exist!"%organizationId)
        exit(0)

def addAsset(data):
    db = database.getDatabase()
    
    data["lastActive"] = datetime.datetime.now().isoformat()
    data["isActive"] = True

    aql = "UPSERT @search INSERT @insert UPDATE @update IN Assets"

    search = {"_key": data["_key"]}
    
    insert = data.copy()
    insert["firstAdded"] = data["lastActive"]

    db.AQLQuery(aql, bindVars={"search": search, "insert": insert, "update": data})
    drawEdge(data["_key"], data["organizationId"])

def drawEdge(assetId, organizationId):
    db = database.getDatabase()
    assetId = str(assetId)
    organizationId = str(organizationId)

    # Remove all edges connected to the asset
    aql = """
    FOR link IN OrganizationAssetEdges
        FILTER link._to == @filter
        REMOVE {_key: link._key} IN OrganizationAssetEdges
    """
    db.AQLQuery(aql, bindVars={"filter": "Assets/"+assetId})

    # Draw new edge
    element = {"_from": "Organizations/"+organizationId, "_to": "Assets/"+assetId}
    aql = "INSERT @element INTO OrganizationAssetEdges"
    db.AQLQuery(aql, bindVars={"element": element})

start = datetime.datetime.now()
def deactivateOldAssets(organizationId):
    #Mark isActive as false for organizations where lastActive is more than 10 days old
    global start
    timeThreshold = start - datetime.timedelta(days=10)
    timeThreshold = timeThreshold.isoformat()

    aql = """
    FOR asset in Assets
        filter asset.organizationId == @organizationId
        filter asset.lastActive < @time
        UPDATE {_key: asset._key, isActive: false} in Assets
        return asset.asset_identifier
    """
    queryResult = database.getDatabase().AQLQuery(aql, bindVars={"organizationId": organizationId, "time": timeThreshold})
    return queryResult

if __name__ == "__main__":
    #Parser stuff
    parser = argparse.ArgumentParser(
        prog = 'python3 getassets.py',
        description = 'Gets structured assets from HackerOne given organization id and stores them in the ArangoDB')
    parser.add_argument('-o', '--organizationid', required=True, help='ID for the organization whos structured assets you want')
   
    args = parser.parse_args()

    #HackerOne auth
    auth = h1vars.getH1Auth()

    organizationId = args.organizationid
    handle = getHandleFromOrganizationId(organizationId)

    #Actually getting the h1 data
    url = 'https://api.hackerone.com/v1/hackers/programs/%s'%(handle)
            
    try:
        r = requests.get(url, auth=auth)
        returned = json.loads(r.text)
    except:
        print("[-] Error with %s"%handle)

    added = 0
    if 'relationships' in returned:
        datas = returned['relationships']    
        for data in datas['structured_scopes']['data']:
            dataToAdd = data['attributes']
            dataToAdd['type'] = data['type']
            dataToAdd['_key'] = "H1_"+data['id']
            dataToAdd['organizationId'] = organizationId
        
            addAsset(dataToAdd)
            added += 1

    queryResult = deactivateOldAssets(organizationId)
    lastStr = ""
    if(queryResult):
        lastStr = "\t|\tDeactivated: %s"%queryResult
    print("[+] %s: %s added or updated%s"%(handle, added, lastStr))
