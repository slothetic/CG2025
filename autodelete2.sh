#!/bin/sh

ls best_zip/*.json | while read line
do
    python3 autodelete_final_discrete.py $line
done