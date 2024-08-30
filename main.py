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
    dt = Data(inp)
    dt.triangulate()
    dt.delaunay_triangulate()
    dt.WriteData()
    dt.DrawResult()
    cnt = 0
    c = ""
    while True:
        print("score:", len(dt.pts) - dt.fp_ind)
        if dt.done or len(dt.pts) - dt.fp_ind >= 200:
            break
        #c = input("Take a step?(y/n/r): ")
        #dt.DrawResult("prev")
        if c == "n":
            break
        #if c == "y":
        dt.step()
        #if c == "r":
            #dt.resolve_dense_pts()
        #print("step", cnt)
        #dt.DrawResult("next")
        #dt.DrawResult(str(cnt))
        cnt += 1
    if dt.done:
        dt.WriteData()
    dt.DrawResult("nonobs")
