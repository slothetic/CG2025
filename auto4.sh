#!/bin/sh

ls challenge_instances_cgshop25/simple-polygon-exterior_*.json | while read line
do
    python3 exterior.py $line
done