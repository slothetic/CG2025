#!/bin/sh

ls example_instances/cgshop2025_examples_ortho_*.json | while read line
do
    python3 main.py -d $line
done