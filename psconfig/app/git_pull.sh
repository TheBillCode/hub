#!/bin/bash
echo 'git fetch' > /hostpipe
echo 'git reset --hard HEAD' > /hostpipe
echo "git merge '@{u}'" > /hostpipe
echo 'git pull https://github.com/plant-studio/hub.git' > /hostpipe
