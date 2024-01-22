#!/usr/bin/python3

"""
Process results and add them to the db
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

def processData(data):
    ip = data['ip']
    port = data['port']

    db = database.getDatabase()
    aql = """
    LET ip = DOCUMENT(@ip)
    UPDATE {_key: ip._key, lastNaabuScan: @now, ports: APPEND(ip.ports, [@port], true)} IN IPs
    """

    db.AQLQuery(aql, bindVars={"ip": "IPs/"+str(ip), "now": datetime.datetime.now().isoformat(), "port": port})

if __name__ == "__main__":
    with open("results.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            jsonData = json.loads(line)
            try:
                processData(jsonData)
                print("[+]", jsonData['ip'], jsonData['port'])
            except Exception as e:
                print("[-]", jsonData['ip'], jsonData['port'])
