#!/bin/bash
echo 'cd /home/pi' > /hostpipe
echo 'git fetch' > /hostpipe
echo 'git reset --hard HEAD' > /hostpipe
echo 'git pull https://github.com/plant-studio/hub.git' > /hostpipe
