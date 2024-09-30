#!/bin/sh

ls opt_solutions/*.json | while read line
do

    /bin/python3 merge.py $line

done
