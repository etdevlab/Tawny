#!/usr/bin/python3

"""
Cleans up asset identifiers to create a regex object
"""

import re
import argparse
from urllib.parse import urlparse
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

def getIdentifierFromScopeId(scopeId):
    col = database.getCollection("Scopes")

    try:
        scope = col[scopeId]
    except:
        print("[-] No such scope with id %s exists!"%scopeId)
        exit(1)

    if(scope["asset_type"] != "URL"):
        print("[-] Scope with id %s is not a URL type"%scopeId)
        exit(1)

    return scope["asset_identifier"]

def addAsset(netloc, scopeId):
    db = database.getDatabase()

    isWildcard = False
    if "*" in netloc: isWildcard = True
    data = {"_key": netloc, "scopeId": scopeId, "isActive": True, "lastActive": datetime.datetime.now().isoformat(), "isWildcard": isWildcard}

    aql = "UPSERT @search INSERT @insert UPDATE @update IN WebAssets"
    search = {'_key': netloc}

    insert = data.copy()
    insert["firstAdded"] = data["lastActive"]

    db.AQLQuery(aql, bindVars={'search': search, 'insert': insert, 'update': data})
    drawEdge(scopeId, netloc)

def dropEdges(scopeId):
    #Remove edges from scopeId to add them later
    db = database.getDatabase()
    scopeId = str(scopeId)

    aql = """
    FOR link IN ScopeWebAssetLinks
        FILTER link._from == @filter
        REMOVE {_key: link._key} IN ScopeWebAssetLinks
    """
    db.AQLQuery(aql, bindVars={'filter': 'Scopes/'+scopeId})

def drawEdge(scopeId, assetId):
    db = database.getDatabase()
    scopeId = str(scopeId)
    assetId = str(assetId)

    #Draw new edge
    element = {'_from': 'Scopes/'+scopeId, '_to': 'WebAssets/'+assetId}
    aql = """
    UPSERT @element INSERT @element UPDATE @element IN ScopeWebAssetLinks
    """
    db.AQLQuery(aql, bindVars={'element': element})

start = datetime.datetime.now()
def deactivateOldAssets(scopeId):
    #Mark isActive as false for programs where lastActive is more than 10 days old
    global start
    timeThreshold = start - datetime.timedelta(days=10)
    timeThreshold = timeThreshold.isoformat()

    aql = """
    FOR asset IN WebAssets
        filter asset.scopeId == @scopeId
        filter asset.lastActive < @time
        UPDATE {_key: asset._key, isActive: false} IN WebAssets
        return asset._key
    """

    queryResult = database.getDatabase().AQLQuery(aql, bindVars={'scopeId': scopeId, "time": timeThreshold})
    if(len(queryResult) > 0):
        print("[-] %s Assets marked as inactive: %s"%(len(queryResult), queryResult))

if __name__ == "__main__":
    #Parser stuff
    parser = argparse.ArgumentParser(
            prog="python3 cleanassets.py",
            description="Given a URL ScopeID, turns the asset identifier into cleaned asset(s)")
    parser.add_argument("-s", "--scopeid", type=int, required=True, help='ID for the scope whos asset identifier you want to clean')

    args = parser.parse_args()

    #Get identifier
    scopeId = int(args.scopeid)
    assetIdentifier = getIdentifierFromScopeId(scopeId)

    #Check for multiple urls
    assetIdentifiers = assetIdentifier.split(",")

    dropEdges(scopeId)
    for identifier in assetIdentifiers:
        #Add https if not there
        original = identifier

        if not identifier.startswith("http"):
            identifier = "https://"+identifier

        netloc = urlparse(identifier).netloc

        #Getting rid of the bruh moments
        if netloc == "*.*" or netloc == "*":
            continue
        if not netloc.replace("*", ""):
            continue

        addAsset(netloc, scopeId)
        print("[+] %s -> %s"%(original, netloc))

    deactivateOldAssets(scopeId)
