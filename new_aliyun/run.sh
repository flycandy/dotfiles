#!/usr/bin/env bash

# exec by
# bash <(curl -s https://raw.githubusercontent.com/qbtrade/dotfiles/master/new_aliyun/run.sh)
# install docker
sudo apt update
sudo apt upgrade
sudo mkdir -p /opt/bin
sudo wget https://raw.githubusercontent.com/qbtrade/dotfiles/master/new_aliyun/new_user.py -O /opt/bin/new_user.py
sudo wget https://raw.githubusercontent.com/qbtrade/dotfiles/master/new_aliyun/zshrc.sh.j2 -O /opt/bin/new_user.py


