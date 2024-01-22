#!/bin/bash

if [ "$1" == "" ]; then
	echo "Need number of workers, i.e ./addWorkers.sh 10"
	exit 1
fi

numFleet=$1
fleetName="workerFleet$(openssl rand -hex 10)"

axiom-fleet $fleetName -i $numFleet
axiom-exec --fleet "$fleetName*" mkdir /home/op/custom
axiom-scp -r /home/admin/Tawny/backend/clientScripts "$fleetName*":/home/op/custom/
axiom-scp -r /home/admin/Tawny/backend/modules "$fleetName*":/home/op/custom/
axiom-exec --fleet "$fleetName*" pip3 install -r /home/op/custom/modules/requirements.txt
axiom-exec --fleet "$fleetName*" python3 /home/op/custom/clientScripts/client.py
