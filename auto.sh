#!/bin/sh

ls example_instances/cgshop2025_examples_simple-polygon_.json | while read line
do
    /bin/python3 main.py $line
done

ls example_instances/cgshop2025_examples_ortho*.json | while read line
do
    /bin/python3 main.py $line
done