#!/bin/sh

ls example_instances/cgshop2025_examples_simple-polygon-exterior_*.json | while read line
do
    /bin/python3 exterior.py $line
done