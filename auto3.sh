#!/bin/sh

ls opt_solutions/cgshop2025_examples_simple-polygon*soluti*.json | while read line
do

    /bin/python3 merge.py $line

done

