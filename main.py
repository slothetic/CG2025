import MyNum
from data import *
import os
import argparse
import sys
import random

# parser = argparse.ArgumentParser()

# parser.add_argument("--data", "-d", required=False, default="")
# args = parser.parse_args()
if __name__=="__main__":
    argument = sys.argv
    if len(argument)>=1:
        inp = argument[1]
    else:
        inp = "example_instances/cgshop2025_examples_ortho_10_ff68423e.instance.json"
    dt = Data(inp)
    if "example_instances" in inp:
        dt.triangulate()
        dt.DrawPoint()
        dt.delaunay_triangulate()
        dt.WriteData()
    # dt.DrawResult()
    cnt = 0
    c = ""
    iter = 0
    max_iter = 1000
    # while True:
    #     iter+=1
    #     print(f"{dt.instance_name} -- Iteration [{iter:>4d}/{max_iter:>4d}]")
    #     # print("score:", len(dt.pts) - dt.fp_ind)
    #     if dt.done or len(dt.pts) - dt.fp_ind >= 200:
    #         dt.WriteData()
    #         break
    #     #c = input("Take a step?(y/n/r): ")
    #     #dt.DrawResult("prev")
    #     if c == "n":
    #         break
    #     #if c == "y":
    #     dt.step()
    #     #if c == "r":
    #         #dt.resolve_dense_pts()
    #     #print("step", cnt)
    #     #dt.DrawResult("next")
    #     #dt.DrawResult(str(cnt))
    #     cnt += 1
    # if dt.done:
    #     dt.WriteData()
    pdb.set_trace()
    dt.additional_triangulate()
    dt.WriteData()
    # dt.DrawResult("nonobs")
