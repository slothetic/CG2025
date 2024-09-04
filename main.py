import MyNum
from data import *
import os
import argparse
import sys
import random

sys.setrecursionlimit(100000)

sys.setrecursionlimit(100000)

# parser = argparse.ArgumentParser()

# parser.add_argument("--data", "-d", required=False, default="")
# args = parser.parse_args()
if __name__=="__main__":
    argument = sys.argv
    if len(argument)>=2:
        inp = argument[1]
    else:
        inp = "example_instances/cgshop2025_examples_ortho_10_ff68423e.instance.json"
    dt = Data(inp)
    print(f"{dt.instance_name} Start!!!!")
    if "example_instances" in inp:
        dt.triangulate()
        dt.DrawPoint()
        dt.delaunay_triangulate()
        dt.WriteData()
    dt.DrawResult()
    cnt = 0
    c = ""
    lim = 20
    dt.make_non_obtuse_boundary()
    n_obs = 0
    n_pts = len(dt.pts) - dt.fp_ind
    for t in dt.triangles:
        if dt.is_obtuse(t):
            n_obs += 1
    # score = (n_obs, n_pts)
    score = dt.score()
    maxcnt = 100
    dt.DrawResult("best")
    dt.WriteData("best")
    while True:
        # print("score:", score)
        
        if cnt>maxcnt:
            break
        if len(dt.pts) - dt.fp_ind >= lim:
            for _ in range(5):
                p = random.randint(dt.fp_ind, len(dt.pts) - 1)
                dt.delete_steiner(p)
            for _ in range(10):
                mini = dt.fp_ind
                mind = sqdist(dt.pts[dt.fp_ind], dt.pts[0])
                for i in range(dt.fp_ind, len(dt.pts)):
                    for j in range(len(dt.pts)):
                        if i == j:
                            continue
                        if sqdist(dt.pts[i], dt.pts[j]) < mind:
                            mini = i
                            mind = sqdist(dt.pts[i], dt.pts[j])
                dt.delete_steiner(mini)
            if cnt % 5 == 0:
                lim += 10
            cnt += 1
            print(f"{dt.instance_name} Iteration: [{cnt}/{maxcnt}] score: {score}")
            for t in dt.triangles:
                del t
            dt.triangles = set()
            dt.triangulate()
            dt.delaunay_triangulate()
            dt.DrawResult("step")
            dt.make_non_obtuse_boundary()
            dt.DrawResult("step")
        n_obs = 0
        n_pts = len(dt.pts) - dt.fp_ind
        for t in dt.triangles:
            if dt.is_obtuse(t):
                n_obs += 1
        if dt.score() > score:
            score = dt.score()
            dt.DrawResult("best")
            dt.WriteData("best")
            
        #c = input("Take a step?(y/n/r): ")
        #dt.DrawResult("prev")
        # if c == "n":
        #     break
        #if c == "y":
        dt.step()
        #if c == "r":
            #dt.resolve_dense_pts()
        #print("step", cnt)
        dt.DrawResult("step")
        #input()
        #dt.DrawResult(str(cnt))
        if dt.done:
            break
    if dt.done:
        dt.WriteData("nonobs")
        dt.DrawResult("nonobs")