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
        dt.DrawPoint()
        dt.delaunay_triangulate()
        dt.WriteData()
    dt.DrawResult()
    cnt = 1
    c = ""
    score = dt.score()
    dt.WriteData()
    dt.make_non_obtuse_boundary()
    # score = (n_obs, n_pts)
    score = dt.score()
    if score > 0.5:
        lim = len(dt.pts) - dt.fp_ind - 1
    else:
        lim = len(dt.pts) - dt.fp_ind + 10
    maxcnt = 1000
    progress = False
    eqcnt = 0
    while True:
        # print("score:", score)
        
        
        if len(dt.pts) - dt.fp_ind > lim:
            if cnt>maxcnt:
                break
            n_del = (len(dt.pts) - dt.fp_ind) // 10
            p = random.randint(dt.fp_ind, len(dt.pts) - 1)
            dlist = [(sqdist(dt.pts[p], dt.pts[i]), i) for i in range(dt.fp_ind, len(dt.pts))]
            dlist.sort()
            dinds = [dlist[i][1] for i in range(n_del)]
            dinds.sort(reverse = True)
            for q in dinds:
                dt.delete_steiner(q)
            for _ in range(5):
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
        ptlen = len(dt.pts)
        dt.step()
        if ptlen == len(dt.pts):
            eqcnt += 1
            if eqcnt == 5:
                increase_IMP()
                print("impreciseness:", IMP, MINDIST)
                eqcnt = 0
        else:
            eqcnt = 0
        dt.DrawResult("step")
        curscore = dt.score()
        if curscore > score:
            score = curscore
            # dt.DrawResult("best")
            dt.WriteData()
            progress = True
            if curscore > 0.5:
                break
        print(f"current score: {curscore}")    
        if curscore < score * 0.001:
            break
        if dt.done:
            lim = len(dt.pts) - dt.fp_ind - 1 
    if dt.done:
        dt.WriteData()
        dt.DrawResult()