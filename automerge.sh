#!/bin/sh

ls example_instances/cgshop2025_examples_simple-polygon_*.json | while read line
do

    /bin/python3 merge.py $line

done
