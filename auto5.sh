#!/bin/sh

ls best_zip/*.solution.json | while read line
do
    
    python3 json_update.py $line
done