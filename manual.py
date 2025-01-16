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
        i = ""
        i = input("what should i do? (0: make non obtuse boundary, 1: step, 2: del nearest, 3: step_proj, 4: draw point, 5: increase prec, 6: write data, 7: undo last insert, 8: exit): ")
        if i == "0":
            dt.make_non_obtuse_boundary()
        elif i=="":
            dt.step()
        elif i == "1":
            j = int(input("how much?: "))
            for _ in range(j):
                dt.step()
                # dt.make_non_obtuse_boundary()
                dt.DrawResult("step")
        elif i == "2":
            j = int(input("which vertex?: "))
            dt.del_nearest(j)
        elif i == "3":
            dt.step_proj()
        elif i == "4":
            dt.DrawPoint()
        elif i == "5":
            increase_IMP()
        elif i == "6":
            dt.WriteData()
        elif i == "7":
            dt.delete_steiner(len(dt.pts)-1)
        elif i == "8":
            break
        dt.DrawResult("step")
        curscore = dt.score()
        if curscore > score:
            score = curscore
            # dt.DrawResult("best")
            dt.WriteData()
        print(f"current score: {curscore}")  
        print(f"number of pts: {len(dt.pts)}")  