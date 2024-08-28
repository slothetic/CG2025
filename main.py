import MyNum
from data import *
import os
import argparse
import sys
import random

parser = argparse.ArgumentParser()

parser.add_argument("--data", "-d", required=False, default="")
args = parser.parse_args()
if __name__=="__main__":
    if args.data:
        inp = args.data
    else:
        inp = "example_instances/cgshop2025_examples_ortho_10_ff68423e.instance.json"
    random.seed(0)
    dt = Data(inp)
    dt.triangulate()
    dt.minmax_triangulate()
    dt.add_steiner(Point(4000,4000))
    dt.add_steiner(Point(8032,MyNum(8855,2)))
    dt.DrawResult("addSt")
    dt.delete_steiner(len(dt.pts)-1)
    dt.DrawResult("deleteSt")
    dt.WriteData()
    dt.DrawResult()
    cnt = 0
    while True:
        c = input("Take a step?(y/n): ")
        if c == "n":
            break
        if c == "y":
            dt.step()
        dt.DrawResult(str(cnt))
        cnt += 1
    dt.WriteData()
    dt.DrawResult("nonobs")
