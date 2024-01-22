#!/usr/bin/python3

"""
Client script that gets a message from the queue, runs it, puts the result in the db for now
"""

import json
import subprocess
import datetime
import time

import os
import sys
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir)
)
sys.path.append(PROJECT_ROOT)

import modules.sqs as sqs
import modules.arangodb as database

#TODO
"""
- get message
- run it in bash
- delete or release message if error
- add results to db
- delete client if no messages for a while
"""

def addToOutputs(response):
    aql = "INSERT @response INTO Outputs"
    while True:
        try:
            database.getDatabase().AQLQuery(aql, bindVars={"response": response})
            break
        except:
            print("[-] Error adding to database... trying again in 20 seconds")
            time.sleep(20)

if __name__ == "__main__":
    #Get the aws id
    output = os.popen("ec2metadata").read()
    ec2Id = ""
    if not output:
        ec2Id = "N/A"
    else:
        for out in output.split('\n'):
            if out.startswith("public-hostname"):
                ec2Id = out.split(" ")[-1]

    print("[+] Starting Tawny Worker Client as %s"%ec2Id)

    while True:
        # Receive a message
        result = sqs.receive_message()
        if "Messages" not in result:
            print("[-] Queue is empty... sleeping for 3 minutes")
            time.sleep(180)
            continue

        # Do validation handling
        message = result.get("Messages", [])[0]
        rHandle = message["ReceiptHandle"]
        body = json.loads(message["Body"])
        print("[+]", body)
        if "action" not in body:
            print("[-] No action, deleting message")
            sqs.delete_message(rHandle)
            continue

        # Process the action
        if body["action"] == "bash":
            # Bash action, needs a command, optional stdin, runs the command
            if "command" not in body:
                print("[-] No command, deleting message")
           
            response = {"action": "bash", "command": body["command"], "startTime": datetime.datetime.now().isoformat(), "ec2hostname": ec2Id}
            process = subprocess.Popen(body["command"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            #stdin
            if "stdin" in body:
                response["stdin"] = body["stdin"]
                process.stdin.write(body["stdin"].encode())
            stdout, stderr = process.communicate()

            #add stdout and stderr to db
            response["endTime"] = datetime.datetime.now().isoformat()
            response["stdout"] = stdout.decode()
            response["stderr"] = stderr.decode()

            if "batchId" in body:
                response["batchId"] = body["batchId"]

            addToOutputs(response)

            sqs.delete_message(rHandle)
            print("[+] Command succesfully completed and added to database")
        else:
            print("[-] Unrecognized action, releasing message")
            sqs.release_message(rHandle)

        #TODO Remove this later
        #exit(0)
