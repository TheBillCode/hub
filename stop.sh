#!/bin/bash
echo "Stopping Plant Studio HUB"
docker-compose down
echo "Stopping Plant Studio Manager"
docker-compose -f psconfig.yaml -p manage down
echo "All Stopped !!"
