#!/bin/sh

ls example_instances/cgshop2025_examples_ortho_*.json | while read line
do
    /bin/python3 main.py $line
done