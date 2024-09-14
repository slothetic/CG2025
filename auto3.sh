#!/bin/sh

ls opt_solutions/cgshop2025_examples_ortho_*soluti*.json | while read line
do
    ls */*soluti*.json | while read line2
    do
        /bin/python3 merge.py $line $line2
    done
    ls ../../sloth/CGSHOP2025/*/*soluti*.json | while read line2
    do
        /bin/python3 merge.py $line $line2
    done
done

ls opt_solutions/cgshop2025_examples_simple-polygon_*soluti*.json | while read line
do
    ls */*soluti*.json | while read line2
    do
        /bin/python3 merge.py $line $line2
    done
    ls ../../sloth/CGSHOP2025/*/*soluti*.json | while read line2
    do
        /bin/python3 merge.py $line $line2
    done
done