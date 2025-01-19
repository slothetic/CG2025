#!/bin/sh

ls best_zip/*.json | while read line
do
    python3 autodelete.py $line
done