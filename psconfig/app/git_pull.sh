#!/bin/bash
echo 'git clone https://github.com/plant-studio/hub.git temp' > /hostpipe
echo 'mv temp/.git hub/.git' > /hostpipe
echo 'rm -rf temp' > /hostpipe
