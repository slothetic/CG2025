#!/bin/sh

while :
do
    /bin/python3 main.py example_instances/cgshop2025_examples_ortho_250_d9594e89.instance.json
    /bin/python3 main.py example_instances/cgshop2025_examples_ortho_150_a39ede60.instance.json
    /bin/python3 main.py example_instances/cgshop2025_examples_ortho_100_5b9b478f.instance.json
done