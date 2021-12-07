#!/bin/bash
sudo /sbin/ip route|awk '/default/ { print $9 }' > /home/pi/hub/psconfig/app/host_ip
echo "Create ps-net docker network"
docker network create ps-net
echo "Starting PlantStudio Hub"
docker-compose up -d
echo "Starting PlantStudio Manager"
docker-compose -f psconfig.yaml -p manage up -d
echo "Have a nice day :-)"
