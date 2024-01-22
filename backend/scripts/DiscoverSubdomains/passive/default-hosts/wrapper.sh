#!/bin/bash
python3 getdefaulthosts.py
python3 /home/admin/Tawny/backend/clientScripts/processing/processHosts.py -t default -f input.txt
rm input.txt
python3 ../../processing/cleanup.py
