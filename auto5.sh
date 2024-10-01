#!/bin/sh

ls challenge_instances_cgshop25/*extract.instance.json | while read line
do
    python3 main3.py $line
done