#!/bin/bash

fleetName="naabuFleet$(openssl rand -hex 10)"
numFleet=15

bash /home/admin/Tawny/backend/scripts/Axiom/initFleet.sh $fleetName $numFleet

python3 getips.py
axiom-scan input.txt --fleet "$fleetName*" --rm-when-done -m custom/naabu -o /dev/null
axiom-rm "$fleetName*"

rm input.txt
