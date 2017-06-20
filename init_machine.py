#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Usage:
    init_machine.py hostname

最好做到py2 py3兼容？

"""

from __future__ import print_function

import os
import sys

print(sys.version)

os.system('useradd -m qbtrade')
os.system('usermod -aG sudo qbtrade')


def system_run(cmd):
    os.system(cmd)


def ensure_line(line, file):
    if line in open(file).read():
        pass
    else:
        open(file, 'a').write(line + '\n')


system_run('apt-get update')
system_run('apt-get upgrade -y')
system_run('apt-get install -y vim git zsh curl wget htop tmux ifstat lrzsz')
system_run('apt-get install -y libxml2-dev libxslt1-dev python-dev')
system_run('apt-get install -y make build-essential libssl-dev zlib1g-dev')
system_run('apt-get install -y libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev')
system_run('apt-get install -y python-pip python3 python3-pip')
system_run('pip install docopt')
system_run('pip3 install docopt')

system_run('curl -fsSL https://get.docker.com/ | sh')

hostname = 'alihz-debug'

system_run('echo {} | sudo tee /etc/hostname'.format(hostname))
system_run('hostname {}'.format(hostname))

ensure_line("127.0.1.1 {}".format(hostname), '/etc/hosts')
