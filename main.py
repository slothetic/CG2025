import MyNum
from data import *
import os
import sys
import pdb 
import faulthandler; faulthandler.enable()

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
    cnt = 1
    c = ""
    score = dt.score()
    dt.make_non_obtuse_boundary()
    # score = (n_obs, n_pts)
    score = dt.score()
    if score > 0.5:
        lim = len(dt.pts) - dt.fp_ind - 1
    else:
        lim = len(dt.pts) - dt.fp_ind + 10
    maxcnt = 10
    progress = False
    while True:
        # print("score:", score)
        
        
        if len(dt.pts) - dt.fp_ind > lim:
            if cnt>maxcnt:
                break
            for _ in range(5):
                if len(dt.pts) > dt.fp_ind:
                    p = random.randint(dt.fp_ind, len(dt.pts) - 1)
                    dt.delete_steiner(p)
            for _ in range(10):
                if len(dt.pts) > dt.fp_ind:
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
            if score <= 0.5 and cnt % 5 == 0:
                lim += 10
            print(f"{dt.instance_name} Iteration: [{cnt}/{maxcnt}] score: {score}")
            if progress:
                cnt = 1
            else:
                cnt += 1
            progress = False
            for t in dt.triangles:
                del t
            print("deletion done!")
            dt.triangles = set()
            dt.triangulate()
            dt.delaunay_triangulate()
            # dt.DrawResult("step")
            dt.make_non_obtuse_boundary()
            print("nonobtbound done!")
            # dt.DrawResult("step")
        curscore = dt.score()
        if curscore > score:
            score = curscore
            # dt.DrawResult("best")
            dt.WriteData()
            progress = True
            
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
            lim = len(dt.pts) - dt.fp_ind - 1 
    if dt.done:
        dt.WriteData()
        dt.DrawResult()