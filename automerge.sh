#!/bin/sh

ls opt_solutions/ortho*.json | while read line
do

    python3 merge.py $line

done

ls opt_solutions/simple-polygon_*.json |while read line
do 
		python3 merge.py $line
done
