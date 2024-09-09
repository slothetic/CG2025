#!/bin/sh

ls opt_sloth/*.json | while read line
do
    /bin/python3 main.py $line
done