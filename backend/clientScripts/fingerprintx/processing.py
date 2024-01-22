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

    data['_key'] = "%s:%s"%(ip, port)

    col = database.getCollection("Fingerprintx")
    col.importBulk(data)

if __name__ == "__main__":
    with open("results.txt", "r") as f:
        lines = f.readlines()
        for line in lines:
            jsonData = json.loads(line)
            processData(jsonData)
