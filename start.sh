#!/bin/bash
echo "Starting PlantStudio Hub"
docker-compose up -d
echo "Waiting 5 seconds"
sleep 5
echo "Starting PlantStudio Manager"
docker-compose -f psconfig.yaml -p manage up -d
echo "Have a nice day :-)"
