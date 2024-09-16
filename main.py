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



def none_obtuse_iter(dt:Data, lim=50):
    global best_dt
    global total_num
    global __
    dt.triangles = set()
    dt.triangulate()
    dt.DrawPoint()
    dt.delaunay_triangulate()
    dt.WriteData()
    dt.DrawResult()
    cnt = 0
    dt.make_non_obtuse_boundary()
    n_obs = 0
    for t in dt.triangles:
        if dt.is_obtuse(t):
            n_obs += 1
    score = dt.score()
    maxcnt = 30
    dt.DrawResult("best")
    dt.WriteData("best")
    while True:  
        if cnt>=maxcnt:
            break
        if len(dt.pts) - dt.fp_ind >= lim:
            print(f"{dt.instance_name} Iteration: ({cnt}/{maxcnt})[{__}/{total_num}] score: {dt.score()} (best: {best_dt.score()})")
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
            dt.DrawResult("step")
            dt.make_non_obtuse_boundary()
            dt.DrawResult("step")
        if dt.score() > score:
            score = dt.score()
            dt.DrawResult("best")
            dt.WriteData("best")

        dt.step()
        dt.DrawResult("step")
        if dt.done:
            print(f"Base sol: {best_dt.score(True)}")
            print(f"Adding sol: {dt.score(True)}")
            best_dt.merge_result(dt)
            print(f"Result sol: {best_dt.score(True)}")
            best_dt.WriteData()
            maxcnt = maxcnt//2
    if dt.done:
        dt.WriteData("nonobs")
        dt.DrawResult("nonobs")
    

if __name__=="__main__":
    argument = sys.argv
    if len(argument)>=2:
        inp = argument[1]
    else:
        inp = "example_instances/cgshop2025_examples_ortho_10_ff68423e.instance.json"
    total_num = 30
    print(inp)
    for __ in range(total_num):
        dt = Data(inp)
        dt.triangulate()
        dt.WriteData()
        print(f"{dt.instance_name} Start!!!!")
        if os.path.isfile(f"opt_solutions/{dt.instance_name}.solution.json"):
            best_dt = Data("opt_solutions/"+dt.instance_name+".solution.json")
            best_score = best_dt.score()
            print(f"Previous Best: {best_score}")
            none_obtuse_iter(dt, lim = int((len(best_dt.pts)-best_dt.fp_ind)*0.8))
            print(f"Base sol: {best_dt.score(True)}")
            print(f"Adding sol: {dt.score(True)}")
            best_dt.merge_result(dt)
            print(f"Result sol: {best_dt.score(True)}")
            best_dt.WriteData()
            del dt


            '''
            if best_score>0.5:
                print(f"{dt.instance_name} is Already non-obtuse")
                total_true = False
                maxcnt = 1000
                best_dt_copy:Data = best_dt.copy()
                i_list = list(range(best_dt_copy.fp_ind, len(best_dt_copy.pts)))
                random.shuffle(i_list)
                ind = 0
                for _ in range(1000):
                    # pdb.set_trace()
                    score = best_dt_copy.score()
                    print(f"{best_dt_copy.instance_name} Iteration: [{_}/{maxcnt}] score: {score} (best: {best_score})")
                    i = i_list[ind]
                    best_dt_copy.delete_steiner(i)
                    # best_dt_copy.delaunay_triangulate()
                    ob = False
                    for t in best_dt_copy.triangles:
                        if best_dt_copy.is_obtuse(t):
                            ob = True
                            break
                    if ob:
                        del best_dt_copy
                        best_dt_copy = best_dt.copy()
                        ind += 1
                    else:
                        best_dt_copy.WriteData()
                        del best_dt
                        best_dt = best_dt_copy.copy()
                        ind = 0
                        i_list = list(range(best_dt_copy.fp_ind, len(best_dt_copy.pts)))
                        random.shuffle(i_list)

            else:
                none_obtuse_iter(dt)
            '''
        else:
            none_obtuse_iter(dt)
            


                
            
        # else:
        #     best_score = 0
        # if "example_instances" in inp:
        #     dt.triangulate()
        #     dt.DrawPoint()
        #     dt.delaunay_triangulate()
        #     dt.WriteData()
        # dt.DrawResult()
        # cnt = 0
        # c = ""
        # lim = 20
        # dt.make_non_obtuse_boundary()
        # n_obs = 0
        # n_pts = len(dt.pts) - dt.fp_ind
        # for t in dt.triangles:
        #     if dt.is_obtuse(t):
        #         n_obs += 1
        # # score = (n_obs, n_pts)
        # score = dt.score()
        # maxcnt = 100
        # dt.DrawResult("best")
        # dt.WriteData("best")
        # while True:
        #     # print("score:", score)
            
        #     if cnt>maxcnt:
        #         break
        #     if len(dt.pts) - dt.fp_ind >= lim:
        #         for _ in range(5):
        #             p = random.randint(dt.fp_ind, len(dt.pts) - 1)
        #             dt.delete_steiner(p)
        #         for _ in range(10):
        #             mini = dt.fp_ind
        #             mind = sqdist(dt.pts[dt.fp_ind], dt.pts[0])
        #             for i in range(dt.fp_ind, len(dt.pts)):
        #                 for j in range(len(dt.pts)):
        #                     if i == j:
        #                         continue
        #                     if sqdist(dt.pts[i], dt.pts[j]) < mind:
        #                         mini = i
        #                         mind = sqdist(dt.pts[i], dt.pts[j])
        #             dt.delete_steiner(mini)
        #         if cnt % 5 == 0:
        #             lim += 10
        #         cnt += 1
        #         print(f"{dt.instance_name} Iteration: [{cnt}/{maxcnt}] score: {score} (best: {best_score})")
        #         for t in dt.triangles:
        #             del t
        #         dt.triangles = set()
        #         dt.triangulate()
        #         dt.delaunay_triangulate()
        #         dt.DrawResult("step")
        #         dt.make_non_obtuse_boundary()
        #         dt.DrawResult("step")
        #     n_obs = 0
        #     n_pts = len(dt.pts) - dt.fp_ind
        #     for t in dt.triangles:
        #         if dt.is_obtuse(t):
        #             n_obs += 1
        #     if dt.score() > score:
        #         score = dt.score()
        #         dt.DrawResult("best")
        #         dt.WriteData("best")
                
        #     #c = input("Take a step?(y/n/r): ")
        #     #dt.DrawResult("prev")
        #     # if c == "n":
        #     #     break
        #     #if c == "y":
        #     dt.step()
        #     #if c == "r":
        #         #dt.resolve_dense_pts()
        #     #print("step", cnt)
        #     dt.DrawResult("step")
        #     #input()
        #     #dt.DrawResult(str(cnt))
        #     if dt.done:
        #         total_true = False
        #         break
        # if dt.done:
        #     dt.WriteData("nonobs")
        #     dt.DrawResult("nonobs")
        #     total_true = False

