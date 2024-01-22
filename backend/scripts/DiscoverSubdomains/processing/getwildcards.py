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
    assetsBatch = getWildcardAssets()

    #Pre retrieve batches
    assets = []
    for asset in assetsBatch:
        assets.append(asset)

    with open("input.txt", "w") as f:
        for asset in assets:
            #Remove wildcard identifier things
            asset = asset.replace("*.", "")
            asset = asset.replace("*", "")

            f.write(asset+"\n")
