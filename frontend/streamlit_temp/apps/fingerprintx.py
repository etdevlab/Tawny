import streamlit as st
import matplotlib.pyplot as plt
import json

import sys
import os
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    os.pardir,
    "backend")
)
sys.path.append(PROJECT_ROOT)

import modules.arangodb as database


def app():
    st.title("FingerprintX Results")

    @st.cache_resource(ttl=600)
    def get_data():
        db = database.getDatabase()

        #aql = """
        #FOR finger IN Fingerprintx
        #    COLLECT port = finger.port INTO fingersByPort
        #    SORT COUNT(fingersByPort[*]) DESC
        #    RETURN{
        #        port,
        #        count: COUNT(fingersByPort[*])
        #    }
        #"""
        aql = """
        FOR out IN Outputs
            FILTER out.batchId == "fingerprintxAbb1"
            return out.stdout
        """

        results = db.AQLQuery(aql, rawResults=True)
        return list(results)

    items = get_data()
    itemDict = {}
    for item in items:
        item = item.strip()
        if not item: continue

        item = json.loads(item)
        if item['port'] not in itemDict:
            itemDict[item['port']] = 0
        itemDict[item['port']] += 1

    st.bar_chart(itemDict)
    st.dataframe([json.loads(i) for i in items if i.strip()])

