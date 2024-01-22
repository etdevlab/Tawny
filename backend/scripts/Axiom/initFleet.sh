#!/bin/bash

if [ "$1" == "" ]; then 
	echo "Need a fleet name, i.e ./initFleet.sh epicFleet 10"
	exit 1
fi
if [ "$2" == "" ]; then
	echo "Need a fleet number, i.e ./initFleet.sh epicFleet 10"
	exit 1
fi

fleetName=$1
numFleet=$2

axiom-fleet $fleetName -i $numFleet
axiom-exec --fleet "$fleetName*" mkdir /home/op/custom
axiom-scp /home/admin/Tawny/backend/clientScripts "$fleetName*":/home/op/custom/
axiom-scp /home/admin/Tawny/backend/modules "$fleetName*":/home/op/custom/
axiom-exec --fleet "$fleetName*" pip3 install -r /home/op/custom/modules/requirements.txt
