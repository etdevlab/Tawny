#!/bin/bash

fleetName="subfinderFleet$(openssl rand -hex 10)"
numFleet=6

bash /home/admin/Tawny/backend/scripts/Axiom/initFleet.sh $fleetName $numFleet

python3 ../../processing/getwildcards.py
axiom-scan input.txt --fleet "$fleetName*" --rm-when-done -m custom/subfinder -o /dev/null
axiom-rm "$fleetName*"

rm input.txt
python3 ../../processing/cleanup.py
