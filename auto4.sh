#!/bin/sh

ls opt_solutions/simple-polygon-exterior_250_*.json | while read line
do
    python3 autodelete.py $line
done
ls opt_solutions/simple-polygon-exterior-20_*.json | while read line
do
    python3 autodelete.py $line
done