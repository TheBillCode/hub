#!/bin/bash
cd /home/pi/hub
/sbin/ip route|awk '/default/ { print $9 }' > psconfig/app/host_ip
while true; do eval "$(cat /home/pi/hub/mypipe)" &> /home/pi/hub/output.txt; done
