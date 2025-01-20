#!/bin/sh

ls opt_solutions/*.json | while read line
do
    python3 autodelete2.py $line
done