#!/usr/bin/python3

"""
This will clean up the Hosts database to get rid of hosts that aren't active anymore
"""

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

if __name__ == "__main__":
    #Deactivate old hosts
    start = datetime.datetime.now()

    timeThreshold = start - datetime.timedelta(days=10)
    timeThreshold = timeThreshold.isoformat()

    aql = """
    FOR host in Hosts
        filter host.lastDiscovered < @time
        UPDATE {_key: host._key, isActive: false} in Hosts
        return host._key
    """
    queryResult = database.getDatabase().AQLQuery(aql, bindVars={"time": timeThreshold})
   
    if not queryResult:
        print("[-] No hosts deactivated")
    else:
        print("[-] %s hosts deactivated: %s"%(len(queryResult), queryResult))

