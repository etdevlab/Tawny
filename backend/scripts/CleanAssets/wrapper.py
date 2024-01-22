#!/usr/bin/python3

"""
Wrapper for now, used to clean all the URL scopes with bounties
"""

import subprocess
import concurrent.futures

import sys
import os
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    os.pardir)
)
sys.path.append(PROJECT_ROOT)

import modules.arangodb as database

def worker(data):
    subprocess.call(['python3', 'cleanassets.py', '-s', data])

def getProgramIds():
    db = database.getDatabase()

    aql = """
    FOR scope IN Scopes
        FILTER scope.isActive == true
        FILTER scope.asset_type == 'URL'
        FILTER scope.eligible_for_bounty == true
        FILTER scope.eligible_for_submission == true
        RETURN scope._key
    """
    queryResults = db.AQLQuery(aql, rawResults=True, batchSize=100)
    return queryResults

if __name__ == "__main__":
    scopeIdsBatch = getProgramIds()

    #Pre retrieve batches
    scopeIds = []
    for scopeId in scopeIdsBatch:
        scopeIds.append(scopeId)

    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(worker, item) for item in scopeIds]
        concurrent.futures.wait(futures)

    print("[*] Cleaned assets for %s scopes"%len(scopeIds))
