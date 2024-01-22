from requests.auth import HTTPBasicAuth
import json

import sys
import os
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir)
)

sys.path.append(PROJECT_ROOT)
import modules.secrets as secrets

def getH1Auth():
    return HTTPBasicAuth(secrets.h1User, secrets.h1API)

HEADERS = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0', 'X-HackerOne' : 'HackerOne Crawler'}
