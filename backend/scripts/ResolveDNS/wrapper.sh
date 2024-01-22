#!/bin/bash

fleetName="massdnsFleet$(openssl rand -hex 10)"
numFleet=8

bash /home/admin/Tawny/backend/scripts/Axiom/initFleet.sh $fleetName $numFleet

python3 gethosts.py
axiom-scan input.txt --fleet "$fleetName*" --rm-when-done -m custom/massdns -o /dev/null
axiom-rm "$fleetName*"

rm input.txt
#TODO cleanup
