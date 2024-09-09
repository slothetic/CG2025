#!/bin/sh

ls example_instances/*.json | while read line
do
    /bin/python3 main.py $line
done