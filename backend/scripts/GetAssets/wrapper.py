#!/usr/bin/python3

"""
Wrapper for now, used to get the strucuted assets of all organizations with bounties
"""

import subprocess
import concurrent.futures
import time

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
    subprocess.call(['python3', 'getassets.py', '-o', data])

def getOrganizationIds():
    db = database.getDatabase()

    aql = """
    FOR organization IN Organizations
        FILTER organization.isActive == true
        FILTER organization.submission_state == 'open'
        FILTER organization.offers_bounties == true
        RETURN organization._key
    """
    queryResults = db.AQLQuery(aql, rawResults=True, batchSize=100)
    return queryResults

if __name__ == "__main__":
    organizationIdsBatch = getOrganizationIds()

    #Pre retrieve batches
    organizationIds = []
    for organizationId in organizationIdsBatch:
        organizationIds.append(organizationId)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker, item) for item in organizationIds]
        concurrent.futures.wait(futures)

    print("[*] Updated assets for %s organizations"%len(organizationIds))
