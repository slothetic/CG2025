#!/bin/sh

ls challenge_instances_cgshop25/ortho*.json | while read line
do
    python3 main.py $line
done
