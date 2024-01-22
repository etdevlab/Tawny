/usr/bin/amass enum -df input -active -config /home/op/custom/clientScripts/amass/config.ini -rf /home/op/custom/clientScripts/amass/resolvers.txt -dns-qps 1000 | anew output
/usr/bin/python3 /home/op/custom/clientScripts/processing/processHosts.py -t amass
