from flask import Flask, request, Response
from functools import wraps
import base64
import json

import sys
import os
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), 
    os.pardir)
    )
)

import modules.arangodb as database
import modules.secrets as secrets

app = Flask(__name__)

#Function that defines authorization, basic auth for now
def requiresAuthentication(f):
    @wraps(f)
    def wrapped_view(**kwargs):
        if 'Authorization' in request.headers:
            authHeader = request.headers.get('Authorization').split(" ")

            if len(authHeader) == 2 and authHeader[0] == "Basic":
                auth = base64.b64decode(authHeader[1]).decode('utf-8').split(":")
                if(auth[0] == secrets.arangoUser and auth[1] == secrets.arangoPass):
                    return f(**kwargs)

        return Response(json.dumps({"success": False, "error": "Unauthorized"}), status=401, mimetype="application/json")
    return wrapped_view

#Options (no auth)
@app.route("/api/v1", methods=["OPTIONS"])
def options():
    #Set headers for coors
    resp = Response()
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
    return resp

#Routes (require auth)
@app.route("/api/v1", methods=["GET", "POST"])
@requiresAuthentication
def index(**kwargs):
    if request.method == "GET":
        return Response(json.dumps({"success": True}), status=200, mimetype="application/json")
    elif request.method == "POST":
        #Get json object from request
        jsonRequest = request.json
        
        #All actions are based on 'action' in the json object
        if 'action' not in jsonRequest:
            return Response(json.dumps({"success": False, "error": "No action specified"}), status=400, mimetype="application/json")
        
        action = jsonRequest['action']
        if action == "getOrganizations":
            #AQL query to get 20 random organizations
            aql = """
            FOR org IN Organizations
                SORT TO_NUMBER(REGEX_MATCHES(org._key, "_([0-9]*)", false)[1]) ASC
                RETURN org
            """
            #Execute query
            result = list(database.getDatabase().AQLQuery(aql, rawResults=True))

            #Return result
            return Response(json.dumps({"success": True, "data": result}), status=200, mimetype="application/json")
        elif action == "getOrganizationData":
            #AQL query to get organization data from id
            aql = """
            LET org = Document(@doc)
            RETURN org
            """

            #Check if organization id is specified
            if 'organizationId' not in jsonRequest:
                return Response(json.dumps({"success": False, "error": "No organization id specified"}), status=400, mimetype="application/json")
            organizationId = jsonRequest['organizationId']

            #Execute query
            result = list(database.getDatabase().AQLQuery(aql, bindVars={"doc": "Organizations/" + organizationId}, rawResults=True))

            #Return result
            return Response(json.dumps({"success": True, "data": result}), status=200, mimetype="application/json")
        elif action == "getOrganizationAssets":
            #Check if organization id is specified
            if 'organizationId' not in jsonRequest:
                return Response(json.dumps({"success": False, "error": "No organization id specified"}), status=400, mimetype="application/json")
            organizationId = jsonRequest['organizationId']

            #AQL query to get all the assets for an organization
            aql = """
            LET org = Document(@doc)
            FOR v,e,p IN 1..1 OUTBOUND org._id OrganizationAssetEdges
            RETURN {
                "vertex": v,
                "edge": e
            }
            """
            #Execute query
            result = list(database.getDatabase().AQLQuery(aql, bindVars={"doc": "Organizations/" + organizationId}, rawResults=True))

            #Return result
            return Response(json.dumps({"success": True, "data": result}), status=200, mimetype="application/json")

        return Response(json.dumps({"success": True}), status=200, mimetype="application/json")

if __name__ == "__main__":
    hostName = "localhost"
    serverPort = 5000
    app.run(host=hostName, port=serverPort, debug=False)
