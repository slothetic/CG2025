#!/bin/sh

ls example_instances/*.json | while read line
do
    ./ALG $line
done