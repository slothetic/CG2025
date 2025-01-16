import MyNum
from data import *
import os
import sys
import pdb 
from random import randint
import faulthandler; faulthandler.enable()

sys.setrecursionlimit(100000)
# parser = argparse.ArgumentParser()
# parser.add_argument("--data", "-d", required=False, default="")
# args = parser.parse_args()
pts_num = [0,0,0,0,0,0,0,0,0,0]
if __name__=="__main__":
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
        score = dt.score()
    else:
        opt = Data("opt_solutions/"+ dt.instance_name + ".solution.json")
        score = opt.score()
    # dt.WriteData()
    # score = (n_obs, n_pts)
    # score = dt.score()
    # if score > 0.5:
    #     lim = len(dt.pts) - dt.fp_ind - 1
    # else:
    #     lim = len(dt.pts) - dt.fp_ind + 20
    dt.DrawPoint()
    while True:
        s = randint(1,40)
        if s%15==0:
            dt.step_proj()
        else:
            dt.step()
        pts_num.pop(0)
        pts_num.append(len(dt.pts))
        dt.make_non_obtuse_boundary()
        if pts_num[0]==pts_num[-1]:
            increase_IMP()
        dt.DrawResult("step")
        curscore = dt.score()
        if curscore > score:
            score = curscore
            # dt.DrawResult("best")
            dt.WriteData()
        print(f"current score: {curscore}")  
        print(f"number of pts: {len(dt.pts)}") 
        if  score>0.5:
            break