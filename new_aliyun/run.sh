#!/usr/bin/env bash

# exec by
# bash <(curl -s https://raw.githubusercontent.com/qbtrade/dotfiles/master/new_aliyun/run.sh)
# install docker
sudo apt update
sudo apt upgrade
sudo apt install wget curl ifstat htop -y
sudo mkdir -p /opt/bin
sudo pip install docopt
sudo pip3 install docopt
sudo wget https://raw.githubusercontent.com/qbtrade/dotfiles/master/new_aliyun/new_user.py -O /opt/bin/new_user.py
sudo chmod +x /opt/bin/new_user.py
sudo wget https://raw.githubusercontent.com/qbtrade/dotfiles/master/new_aliyun/zshrc.sh.j2 -O /home/zshrc
sudo sed -i -e 's/{{REGION}}/alihz/g' /home/zshrc


