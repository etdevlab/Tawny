#!/bin/bash

fleetName="fingerprintxFleet$(openssl rand -hex 10)"
numFleet=30

bash /home/admin/Tawny/backend/scripts/Axiom/initFleet.sh $fleetName $numFleet

python3 getipports.py
axiom-scan input.txt --fleet "$fleetName*" --rm-when-done -m custom/fingerprintx -o /dev/null
axiom-rm "$fleetName*"

rm input.txt
