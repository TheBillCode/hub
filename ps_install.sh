#!/bin/bash
sudo apt-get update && sudo apt-get -y upgrade
sudo apt install git -y
curl -fsSL https://get.docker.com -o get-docker.sh
sudo bash get-docker.sh
sudo usermod -aG docker $(whoami)
sudo apt install python3-pip -y
sudo pip3 install docker-compose
git clone https://github.com/plant-studio/hub.git
mkfifo /home/pi/hub/mypipe
sudo mv /home/pi/hub/ps-startup.service /etc/systemd/system/ps-startup.service
chmod 664 /etc/systemd/system/host-ip.sh
sudo systemctl daemon-reload
sudo systemctl enable host-ip.service
sudo reboot
