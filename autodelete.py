import MyNum
from data import *
import os
import sys
import pdb 
import faulthandler; faulthandler.enable()
import random

sys.setrecursionlimit(100000)
# parser = argparse.ArgumentParser()
# parser.add_argument("--data", "-d", required=False, default="")
# args = parser.parse_args()
if __name__=="__main__":
    i = 0
    argument = sys.argv
    inp = argument[1]
    dt = Data(inp)
    print(f"{dt.instance_name} Start!!!!")
    if "challenge_instances_cgshop25" in inp:
        dt.triangulate()
        dt.delaunay_triangulate()
        dt.DrawResult("step")
        # dt.WriteData()
    dt.DrawResult()
    cnt = 1
    c = ""
    if "opt_solutions" in inp:
        obt, spt = dt.score_imp()
    else:
        opt = Data("opt_solutions/"+ dt.instance_name + ".solution.json")
        obt, spt = opt.score_imp()
    # dt.WriteData()
    # score = (n_obs, n_pts)
    # score = dt.score()
    # if score > 0.5:
    #     lim = len(dt.pts) - dt.fp_ind - 1
    # else:
    #     lim = len(dt.pts) - dt.fp_ind + 20
    #dt.DrawPoint()
    while True:
        cnt+=1
        pt_num = random.randint(dt.fp_ind, len(dt.pts)-1)
        pt = dt.pts[pt_num]
        dt.delete_steiner(pt_num)
        nobt, nspt = dt.score_imp()
        if obt<nobt:
            dt.add_steiner(pt)
        else:
              dt.WriteData()
              obt = nobt
              spt = nspt
        dt.DrawResult("step")
        print(f"[{dt.instance_name}] {cnt}")
        print(f"number of obtuse: {obt}")  
        print(f"number of steiner pts: {spt-dt.fp_ind}")  
        dt.WriteData()