docker run --rm -i --mount type=bind,source="$(pwd)",target=/data axiom/assetfinder < input | tee output
/usr/bin/python3 /home/op/custom/clientScripts/processing/processHosts.py -t assetfinder
