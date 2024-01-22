go install github.com/praetorian-inc/fingerprintx/cmd/fingerprintx@latest
echo "[+] Starting fingerprintx"
fingerprintx -l input --json -o results.txt
echo "[+] Processing data"
/usr/bin/python3 /home/op/custom/clientScripts/fingerprintx/processing.py
