#!/bin/bash
while true; do eval "$(cat /home/pi/hub/mypipe)" &> /home/pi/hub/output.txt; done
