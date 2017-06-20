#!/bin/bash 

if [ "$#" -eq 1 ]
then
    if [[ $1 == /Users/tyz/Dropbox/qb/* ]]
    then
        old=/Users/tyz/Dropbox/qb/
        new=/home/tyz/qb/
        echo copy single file $1
        rsync $1 alihk-debug.qbtrade.org:${1/$old/$new}
    fi
else
    echo copy all
    rsync -a --delete --exclude='.git/' ../qb alihk-debug.qbtrade.org:/home/tyz/
    rsync -a --delete --exclude='.git/' ../qb alihz-debug.qbtrade.org:/home/tyz/
fi



