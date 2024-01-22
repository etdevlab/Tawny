#!/usr/bin/python3

"""
Gets default hosts from the database, i.e non wildcard hosts and wildcard hosts with the *. stuff stripped
"""

import re
import datetime

import sys
import os
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    os.pardir,
    os.pardir,
    os.pardir)
)
sys.path.append(PROJECT_ROOT)

import modules.arangodb as database
import modules.scoper as scoper

def getNonWildcardAssets():
    db = database.getDatabase()

    aql = """
    FOR asset IN WebAssets
        FILTER NOT asset.isWildcard
        RETURN asset._key
    """

    return db.AQLQuery(aql, rawResults=True, batchSize=100)

def getWildcardAssets():
    db = database.getDatabase()

    aql = """
    FOR asset IN WebAssets
        FILTER asset.isWildcard
        RETURN asset._key
    """

    return db.AQLQuery(aql, rawResults=True, batchSize=100)

if __name__ == "__main__":
    #Input Mode
    nonWildcardAssetsBatch = getNonWildcardAssets()
    wildcardAssetsBatch = getWildcardAssets()

    #Pre retrieve batches
    nonWildcardAssets = []
    wildcardAssets = []

    for asset in nonWildcardAssetsBatch:
        nonWildcardAssets.append(asset)
    for asset in wildcardAssetsBatch:
        wildcardAssets.append(asset)

    with open("input.txt", "w") as f:
        for asset in nonWildcardAssets:
            f.write(asset+"\n")

        for asset in wildcardAssets:
            #Remove wildcard identifier things
            if asset.startswith("*."):
                asset = asset[2:]
            asset = asset.replace("*", "")

            f.write(asset+"\n")
