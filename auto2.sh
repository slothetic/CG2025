#!/bin/sh

ls opt_solutions/cgshop2025_examples_*extract*.json | while read line
do
    /bin/python3 main.py $line
done
