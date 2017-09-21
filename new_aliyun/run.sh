#!/usr/bin/env bash
# first
# export REGION=alihz
# exec by
# bash <(curl -s https://raw.githubusercontent.com/qbtrade/dotfiles/master/new_aliyun/run.sh)
# install docker
sudo apt update
sudo apt upgrade -y
sudo apt install wget curl ifstat htop python python3 python-pip python3-pip -y
sudo mkdir -p /opt/bin
sudo pip install docopt
sudo pip3 install docopt
sudo wget https://raw.githubusercontent.com/qbtrade/dotfiles/master/new_aliyun/new_user.py -O /opt/bin/new_user.py
sudo wget https://raw.githubusercontent.com/qbtrade/dotfiles/master/new_aliyun/change_hosts.py -O /opt/bin/change_hosts.py
sudo wget https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh -O /opt/bin/oh-my-zsh.sh
sudo wget https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer -O /opt/bin/pyenv-installer
sudo chmod +x /opt/bin/new_user.py
sudo chmod +x /opt/bin/oh-my-zsh.sh
sudo chmod +x /opt/bin/pyenv-installer
sudo chmod +x /opt/bin/change_hosts.py

sudo wget https://raw.githubusercontent.com/qbtrade/dotfiles/master/new_aliyun/zshrc.sh -O /home/zshrc
sudo sed -i -e "s/{{REGION}}/$REGION/g" /home/zshrc
sudo sed -i -e "s/{{REGION}}/$REGION/g" /opt/bin/new_user.py
sudo pip install docopt

