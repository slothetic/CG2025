import MyNum
from data import *
import os
import sys
import pdb 
import faulthandler; faulthandler.enable()

sys.setrecursionlimit(100000)

def sqdist1(px, py, qx, qy):
    xd = px-qx
    yd = py-qy
    return xd * xd + yd * yd

def closest_pair(dt:Data):
    dist = float("INF")
    mini = 0
    for i in range(dt.fp_ind, len(dt.pts)-1):
        for j in range(i,len(dt.pts)-1):
            newdist = sqdist1(float(dt.pts[i].x),float(dt.pts[i].y),float(dt.pts[j].x),float(dt.pts[j].y))
            if newdist<dist:
                dist = newdist
                mini = i
    return mini



def none_obtuse_iter(dt:Data, lim=50, stn = 0):
    global best_dt
    # global total_num
    # global __
    # best_dt = dt.copy()
    dt.triangles = set()
    dt.triangulate()
    # dt.DrawPoint()
    dt.delaunay_triangulate()
    dt.make_non_obtuse_boundary()
    cnt = 0
    n_obs = 0
    for t in dt.triangles:
        if dt.is_obtuse(t):
            n_obs += 1
    score = best_dt.score()
    maxcnt = 30
    # dt.DrawResult("best")
    # dt.WriteData("best")
    # dt.fp_ind+=stn
    while True:  
        if cnt>=maxcnt:
            break
        if len(dt.pts) - dt.fp_ind >= lim:
            print(f"{dt.instance_name} Iteration: ({cnt}/{maxcnt}) score: {dt.score()} (best: {best_dt.score()})")
            best_dt.merge_result(dt)
            print(f"Result sol: {best_dt.score(True)}")
            best_dt.WriteData()
            del_num = min(30, len(dt.pts) - int(len(best_dt.pts)*0.6))
            random_del_num = random.randint(0, del_num)
            dt.delete_random_steiner(random_del_num)
            del_num -= random_del_num
            while del_num:
                ndn = random.randint(1,del_num)
                del_num -= ndn
                mini = closest_pair(dt)
                dt.delete_random_steiner_query(mini, ndn)
            if cnt % 5 == 0:
                lim += 10
                if best_dt.score()>0.5:
                    lim = min(lim, len(best_dt.pts)-dt.fp_ind)
            cnt += 1
            for t in dt.triangles:
                del t
            dt.triangles = set()
            dt.triangulate()
            dt.delaunay_triangulate()
            dt.merge_result(best_dt)
            # dt.DrawResult("step")
            # dt.make_non_obtuse_boundary()
            # dt.DrawResult("step")
        # dt.fp_ind-=stn
        if dt.score() > score:
            score = dt.score()
            # dt.DrawResult("best")
            # dt.WriteData("best")
            del best_dt
            best_dt = dt.copy()
        # dt.fp_ind+=stn

        dt.step(False)
        dt.DrawResult("step")
        if dt.done:
            # dt.fp_ind-=stn
            # print(f"Base sol: {best_dt.score(True)}")
            # print(f"Adding sol: {dt.score(True)}")
            # best_dt.merge_result(dt)
            # print(f"Result sol: {best_dt.score(True)}")
            # dt.WriteData()
            # dt.fp_ind+=stn
            # maxcnt = maxcnt//2
            del best_dt
            best_dt = dt.copy()
            return True
    if dt.done:
        del best_dt
        best_dt = dt.copy()
        return True
        # dt.fp_ind-=stn
        # dt.WriteData("nonobs")
        # dt.DrawResult("nonobs")
        # dt.fp_ind+=stn
    

if __name__=="__main__":
    argument = sys.argv
    if len(argument)>=2:
        inp = argument[1]
    else:
        inp = "example_instances/cgshop2025_examples_ortho_10_ff68423e.instance.json"
    if "extract" not in inp:
        total_num = 30
        print(inp)
        with open(inp, "r", encoding="utf-8") as f:
            root = json.load(f)
            instance_name = root["instance_uid"]
        extract_sol = f"opt_solutions/{instance_name}_extract.solution.json"
        with open(extract_sol, "r", encoding="utf-8") as f:
            root = json.load(f)
            x = root["steiner_points_x"]
            y = root["steiner_points_y"]
            # print(x,y)
            st_pt = []
            for i in range(len(x)):
                st_pt.append(Point(x[i], y[i])) 
                # print(st_pt)
        stn = len(st_pt)     
        dt = Data(inp)
        dt.triangulate()
        dt.add_steiners(st_pt)
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
        