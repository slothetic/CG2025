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
    fail = 0
    # dt.DrawResult("best")
    # dt.WriteData("best")
    # dt.fp_ind+=stn
    while True:  
        lennum = len(dt.pts)
        if cnt>=maxcnt:
            break
        if len(dt.pts) - dt.fp_ind >= lim:
            print(f"{dt.instance_name} Iteration: ({cnt}/{maxcnt}) score: {dt.score()} (best: {best_dt.score()})")
            best_dt.merge_result(dt)
            print(f"Result sol: {best_dt.score()}")
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

        dt.step()
        if lennum==len(dt.pts): fail+=1
        if fail>30: increase_IMP()
        dt.DrawResult("step")
        if dt.score()>0.5:
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
            break
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
        dts = dt.partial_datas()
        
        for d in dts:
            st_pt = []
            d.triangulate()
            d.DrawResult()
            # pdb.set_trace()
            best_dt = d.copy()
            it = 0
            while none_obtuse_iter(d):
                it+=1
                if it>100:
                    break
            for p in best_dt.pts[best_dt.fp_ind:]:
                st_pt.append(p)
            dt.add_steiners(st_pt)
            dt.WriteData()
            

        

        # for __ in range(total_num):
        #     dt = Data(inp)
        #     dt.triangulate()
        #     for p in st_pt:
        #         dt.add_steiner(p)
        #         dt.DrawResult()
        #     dt.WriteData()
        #     print(f"{dt.instance_name} Start!!!!")
        #     best_dt = Data("opt_solutions/"+dt.instance_name+".solution.json")
        #     best_score = best_dt.score()
        #     print(f"Previous Best: {best_score}")
        #     none_obtuse_iter(dt, lim = int((len(best_dt.pts)-best_dt.fp_ind)*0.8), stn=stn)
        #     del dt
