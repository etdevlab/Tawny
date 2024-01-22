#!/usr/bin/python3

"""
Used to get the scope from a given domain netloc
"""

from urllib.parse import urlparse
import re

import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.path.pardir)
)
sys.path.append(PROJECT_ROOT)

import modules.arangodb as database

def findScope(url):
    #Finds the scope based off url, will try to format to get the netloc
    
    #Format the data
    netloc = cleanUrl(url)

    #Non wildcards first
    db = database.getDatabase()
    aql = """
    FOR asset IN WebAssets
        FILTER asset.isWildcard == false
        FILTER asset._key == @netloc
        RETURN asset
    """

    results = db.AQLQuery(aql, bindVars={'netloc': netloc}, rawResults=True)
    if(results):
        for result in results:
            return result

    #Check wildcards
    aql = """
    FOR webAsset IN webAssetView
        SEARCH ANALYZER(webAsset._key IN TOKENS(@netloc, "webAssetAnalyzer"), "webAssetAnalyzer")
        FILTER webAsset.isWildcard == true
        SORT BM25(webAsset) DESC
        LIMIT 20
        RETURN webAsset
    """

    results = db.AQLQuery(aql, bindVars={'netloc': netloc}, rawResults=True)
    if(results):
        for result in results:
            #Transform to regex
            reString = wildcardToRegex(result["_key"])

            if(re.match(reString, netloc)):
                return result

    return False

def cleanUrl(url):
    if not url.startswith("http"):
        url = "https://" + url

    return urlparse(url).netloc

def wildcardToRegex(wildcard):
    reString = wildcard.replace("*.", "*")
    reString = reString.replace(".", "\\.")
    reString = reString.replace("*", ".*")

    return reString
