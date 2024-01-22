#!/usr/bin/python3

"""
Arango db connection and related functions
"""

from pyArango.connection import *
import pyArango

import os
import sys
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir)
)

sys.path.append(PROJECT_ROOT)
import modules.secrets as secrets

connection = None
def getConnection():
    global connection
    if not connection: 
        connection = Connection(username=secrets.arangoUser, password=secrets.arangoPass, arangoURL=secrets.arangoURL)
    return connection

def getDatabase(name="Tawny"):
    try:
        return getConnection().createDatabase(name=name)
    except pyArango.theExceptions.CreationError:
        return getConnection()[name]

def getCollection(name, dbname="Tawny"):
    try:
        return getDatabase(dbname).createCollection(name=name)
    except pyArango.theExceptions.CreationError:
        return getDatabase(dbname)[name]

def getDocument(name):
    aql = "RETURN DOCUMENT(@name)"
    return getDatabase().AQLQuery(aql, rawResults=True, bindVars={"name": name})
