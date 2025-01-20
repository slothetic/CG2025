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
    if "extract" in inp:
        pass
    else:
        dt = Data(inp)
        print(f"{dt.instance_name} Start!!!!")
        cnt = 1
        lcnt = 1
        obt, spt = dt.score_imp()
        # dt.WriteData()
        # score = (n_obs, n_pts)
        # score = dt.score()
        # if score > 0.5:
        #     lim = len(dt.pts) - dt.fp_ind - 1
        # else:
        #     lim = len(dt.pts) - dt.fp_ind + 20
        #dt.DrawPoint()
        while lcnt < len(dt.pts)-dt.fp_ind:
            lcnt+=1
            pt_num = random.randint(dt.fp_ind, len(dt.pts)-1)
            pt:Point = dt.pts[pt_num]
            dt.delete_steiner(pt_num)
            dt.add_steiner(Point(pt.x-MyNum(102,101), pt.y))
            nobt, nspt = dt.score_imp()
            if obt<nobt:
                dt.delete_steiner(len(dt.pts)-1)
                dt.add_steiner(pt)
            else:
                while nobt<=obt:
                    pt = dt.pts[len(dt.pts)-1]
                    dt.delete_steiner(pt_num)
                    dt.add_steiner(Point(pt.x-1, pt.y))
                    nobt, nspt = dt.score_imp()
                dt.delete_steiner(len(dt.pts)-1)
                dt.add_steiner(pt)
                dt.WriteData()
                print(f"{pt_num} moved!!")
                dt.DrawResult("left_step")
                obt = nobt
                spt = nspt
            
        while cnt<len(dt.pts)-dt.fp_ind:
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
                print(f"[{dt.instance_name}] {cnt}")
                print(f"number of obtuse: {obt}")  
                print(f"number of steiner pts: {spt-dt.fp_ind}")  
                cnt=0