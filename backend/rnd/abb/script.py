#!/usr/bin/python3

import json
from urllib.parse import urlparse

import sys
import os
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    os.pardir)
)
sys.path.append(PROJECT_ROOT)

import modules.sqs as sqs
import modules.arangodb as database

def assetfinder():
    command = "echo '%s' | docker run --rm -i --mount type=bind,source=\"$(pwd)\",target=/data axiom/assetfinder"

    with open("wildcards.txt", "r") as f:
        for line in f.readlines():
            line = line.strip()

            queueObj = {
                "action": "bash",
                "command": command%line,
                "batchId": "assetFinderAbb1"
            }
            sqs.send_message(queueObj)

def subfinder():
    command = "/home/op/go/bin/subfinder -d '%s'"

    with open("wildcards.txt", "r") as f:
        for line in f.readlines():
            line = line.replace("*.", "")
            line = line.strip()

            queueObj = {
                "action": "bash",
                "command": command%line,
                "batchId": "subFinderAbb3"
            }
            sqs.send_message(queueObj)

def outputSubdomains():
    aql = """
    FOR out IN Outputs
        FILTER out.batchId == "assetFinderAbb1"
        return out.stdout
    """

    assetfinderResults = list(database.getDatabase().AQLQuery(aql, rawResults=True))
    for result in assetfinderResults:
        for r in result.split("\n"):
            r = r.strip()
            if not r: continue
            os.system("echo '%s' | anew subdomains.txt"%r)

    aql = """
    FOR out IN Outputs
        FILTER out.batchId == "subFinderAbb3"
        return out.stdout
    """
    subfinderResults = list(database.getDatabase().AQLQuery(aql, rawResults=True))
    for result in subfinderResults:
        for r in result.split("\n"):
            r = r.strip()
            if not r: continue
            os.system("echo '%s' | anew subdomains.txt"%r)

def httprobe():
    command = "echo '%s' | httprobe"

    with open("subdomains.txt", "r") as f:
        for line in f.readlines():
            line = line.strip()

            queueObj = {
                "action": "bash",
                "command": command%line,
                "batchId": "httprobeAbb3"
            }
            sqs.send_message(queueObj)

def outputValidSubdomains():
    aql = """
    FOR out IN Outputs
        FILTER out.batchId == "httprobeAbb3"
        return out.stdout
    """

    httprobeResults = list(database.getDatabase().AQLQuery(aql, rawResults=True))
    for result in httprobeResults:
        for r in result.split("\n"):
            r = r.strip()
            r = r.replace("https://", "")
            r = r.replace("http://", "")
            if not r: continue
            os.system("echo '%s' | anew validSubdomains.txt"%r)

def naabu():
    command = "naabu -json -host %s"

    with open("validSubdomains.txt", "r") as f:
        for line in f.readlines():
            line = line.strip()

            queueObj = {
                "action": "bash",
                "command": command%line,
                "batchId": "naabuAbb1"
            }
            sqs.send_message(queueObj)

def outputHostPorts():
    aql = """
    FOR out IN Outputs
        FILTER out.batchId == "naabuAbb1"
        return out.stdout
    """

    naabuResults = list(database.getDatabase().AQLQuery(aql, rawResults=True))
    for result in naabuResults:
        for r in result.split("\n"):
            r = r.strip()

            if not r: continue
            jsonObj = json.loads(r)
            
            os.system("echo '%s:%s' | anew hostPorts.txt"%(jsonObj["host"], jsonObj["port"]))

def fingerprintx():
    command = "fingerprintx --json -t %s"

    with open("hostPorts.txt", "r") as f:
        for line in f.readlines():
            line = line.strip()

            queueObj = {
                "action": "bash",
                "command": command%line,
                "batchId": "fingerprintxAbb1"
            }
            sqs.send_message(queueObj)

def hakrawler():
    command = "echo '%s' | hakrawler -d 3 --json -t 10 -u"

    aql = """
    FOR out IN Outputs
        FILTER out.batchId == "fingerprintxAbb1"
        return out.stdout
    """

    fingerprintxResults = list(database.getDatabase().AQLQuery(aql, rawResults=True))
    for result in fingerprintxResults:
        for r in result.split("\n"):
            r = r.strip()

            if not r: continue
            jsonObj = json.loads(r)

            if not jsonObj["protocol"].startswith("http"): continue
            URL = "%s://%s:%s"%(jsonObj["protocol"], jsonObj["host"], jsonObj["port"])

            queueObj = {
                "action": "bash",
                "command": command%URL,
                "batchId": "hakrawlerAbb1"
            }
            sqs.send_message(queueObj)

def gau():
    command = "gau -json %s"

    with open("validSubdomains.txt", "r") as f:
        for line in f.readlines():
            line = line.strip()
            
            queueObj = {
                "action": "bash",
                "command": command%line,
                "batchId": "gauAbb2"
            }
            sqs.send_message(queueObj)

def outputEndpoints():
    aql = """
    FOR out IN Outputs
        FILTER out.batchId == "hakrawlerAbb1"
        FILTER out.stdout != ""
        return out.stdout
    """

    hakrawlerResults = list(database.getDatabase().AQLQuery(aql, rawResults=True))
    for result in hakrawlerResults:
        for r in result.split("\n"):
            r = r.strip()

            if not r: continue
            jsonObj = json.loads(r)
            url = jsonObj['URL']

            with open("wildcards.txt", "r") as f:
                hasBroken = False
                for line in f.readlines():
                    line = line.strip()
                    line = line.replace("*.", "")

                    if urlparse(url).netloc.endswith(line):
                        hasBroken = True
                        break
            
            if not hasBroken:
                continue

            os.system("echo '%s' | anew endpoints.txt"%(url))

def arjun():
    command = "arjun -u %s -t 20 -oJ output.json -q && cat output.json"

    with open("endpoints-queries.txt", "r") as f:
        for line in f.readlines():
            line = line.strip()
            
            queueObj = {
                "action": "bash",
                "command": command%line,
                "batchId": "arjunAbb2"
            }
            sqs.send_message(queueObj)

def nuclei():
    command = "nuclei -u %s -as -json"

    with open("validSubdomains.txt", "r") as f:
        for line in f.readlines():
            line = line.strip()

            queueObj = {
                "action": "bash",
                "command": command%("https://"+line),
                "batchId": "nucleiAbb1"
            }

            sqs.send_message(queueObj)

def analyzeNuclei():
    aql = """
    FOR out in Outputs
        FILTER out.batchId == "nucleiAbb1"
        FILTER out.stdout != ""
        return out.stdout
    """

    nucleiResults = list(database.getDatabase().AQLQuery(aql, rawResults=True))
    for result in nucleiResults:
        for r in result.split("\n"):
            r = r.strip()

            if not r: continue
            jsonObj = json.loads(r)

            if jsonObj['info']['severity'] == 'info': continue
            print(jsonObj['info']['severity'], jsonObj['info']['description'])
 
