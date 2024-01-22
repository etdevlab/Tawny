cat input | while read line; do /home/op/go/bin/subfinder -silent -d $line | anew output; done
/usr/bin/python3 /home/op/custom/clientScripts/processing/processHosts.py -t subfinder
