import MyNum
from data import *
import os
import argparse
import sys

parser = argparse.ArgumentParser()

parser.add_argument("--data", "-d", required=False, default="")
args = parser.parse_args()
if __name__=="__main__":
    if args.data:
        input = args.data
    else:
        input = "example_instances/cgshop2025_examples_ortho_10_ff68423e.instance.json"
    dt = Data(input)
    dt.triangulate()
    dt.minmax_triangulate()
    dt.WriteData()
    dt.DrawResult()
