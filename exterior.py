import MyNum
from data import *
import os
import sys
import pdb 
import glob
import faulthandler; faulthandler.enable()

sys.setrecursionlimit(100000)

def none_obtuse_iter(dt, triaguled = False):
    if "example_instances" in inp and not triaguled:
        dt.triangulate()
        dt.DrawPoint()
        dt.delaunay_triangulate()
        dt.WriteData()
        dt.make_non_obtuse_boundary()
    dt.WriteData()
    dt.DrawResult()
    cnt = 0
    c = ""
    lim = len(dt.pts) - dt.fp_ind+20
    dt.make_non_obtuse_boundary()
    n_obs = 0
    n_pts = len(dt.pts) - dt.fp_ind
    for t in dt.triangles:
        if dt.is_obtuse(t):
            n_obs += 1
    # score = (n_obs, n_pts)
    score = dt.score()
    maxcnt = 1000
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
            print(f"{dt.instance_name} Iteration: [{cnt}/{maxcnt}] score: {score} (best: {best_score})")
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
            total_true = False
            break
    if dt.done:
        dt.WriteData("nonobs")
        dt.DrawResult("nonobs")
        total_true = False

# parser = argparse.ArgumentParser()

# parser.add_argument("--data", "-d", required=False, default="")
# args = parser.parse_args()
if __name__=="__main__":
    # argument = sys.argv
    # if len(argument)>=2:
    #     inp = argument[1]
    Lee_folder = "/home/jagunlee/CG2025/example_instances/*exterior_*.json"
    for inp in glob.glob(Lee_folder):
        print(inp)
        dt = Data(inp)
        dt.triangulate()
        dt.DrawPoint()

        dt.exterior_solver()
    # total_true = True
    # while total_true:
    #     dt = Data(inp)
    #     # pdb.set_trace()
    #     print(f"{dt.instance_name} Start!!!!")
        
    #     if os.path.isfile(f"opt_solutions/{dt.instance_name}.solution.json"):
    #         with open("opt_solutions/"+dt.instance_name+".solution.json", "r", encoding="utf-8") as f:
    #             root = json.load(f)
    #             if "score" in root.keys():
    #                 best_score = root["score"]
    #             else:
    #                 best_dt = Data("opt_solutions/"+dt.instance_name+".solution.json")
    #                 best_score = best_dt.score()
    #         if not dt.triangles:
    #             dt.triangulate()
    #         dt.DrawPoint()
    #         dt.exterior_non_obtuse_triangulate()
    #         print(f"Previous Best: {best_score}")
    #         if best_score>0.5:
    #             print(f"{dt.instance_name} is Already non-obtuse")
    #             total_true = False
    #             maxcnt = 1000
    #             best_dt_copy:Data = best_dt.copy()
    #             i_list = list(range(best_dt_copy.fp_ind, len(best_dt_copy.pts)))
    #             random.shuffle(i_list)
    #             ind = 0
    #             for _ in range(1000):
    #                 # pdb.set_trace()
    #                 score = best_dt_copy.score()
    #                 print(f"{best_dt_copy.instance_name} Iteration: [{_}/{maxcnt}] score: {score} (best: {best_score})")
    #                 i = i_list[ind]
    #                 best_dt_copy.delete_steiner(i)
    #                 # best_dt_copy.delaunay_triangulate()
    #                 ob = False
    #                 for t in best_dt_copy.triangles:
    #                     if best_dt_copy.is_obtuse(t):
    #                         ob = True
    #                         break
    #                 if ob:
    #                     del best_dt_copy
    #                     best_dt_copy = best_dt.copy()
    #                     ind += 1
    #                 else:
    #                     best_dt_copy.WriteData()
    #                     del best_dt
    #                     best_dt = best_dt_copy.copy()
    #                     ind = 0
    #                     i_list = list(range(best_dt_copy.fp_ind, len(best_dt_copy.pts)))
    #                     random.shuffle(i_list)

    #         else:
    #             none_obtuse_iter(dt, triaguled=True)
    #     else:
    #         break

