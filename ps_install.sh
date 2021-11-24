#!/bin/bash
sudo apt-get update && sudo apt-get -y upgrade
curl -fsSL https://get.docker.com -o get-docker.sh
sudo bash get-docker.sh
sudo usermod -aG docker $(whoami)
sudo apt install python3-pip -y
sudo pip3 install docker-compose
git clone https://github.com/plant-studio/hub.git
(crontab -l 2>/dev/null; echo "@reboot /home/pi/hub/execpipe.sh") | crontab -
sudo reboot