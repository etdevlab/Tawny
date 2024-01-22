from neo4j import GraphDatabase
import json

import os
import sys
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir)
)
sys.path.append(PROJECT_ROOT)

import modules.secrets as secrets

driver = GraphDatabase.driver(secrets.neo4jUrl, auth=(secrets.neo4jUser, secrets.neo4jPass))

def getDriver():
    global driver
    return driver
