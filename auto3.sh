#!/bin/sh

ls challenge_instances_cgshop25/point-set*.json | while read line
do

    /bin/python3 main2.py $line

done

