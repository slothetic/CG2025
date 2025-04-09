import MyNum
from data import *
import os
import sys
import pdb 
import faulthandler; faulthandler.enable()
import random
import datetime
sys.setrecursionlimit(100000)
# parser = argparse.ArgumentParser()
# parser.add_argument("--data", "-d", required=False, default="")
# args = parser.parse_args()
Narg = 2
if __name__=="__main__":
    i = 0
    argument = sys.argv
    inp = argument[1]
    if "extract" in inp:
        pass
    else:
        dt = Data(inp)
        now = datetime.datetime.now()
        print(f"{dt.instance_name} Start!!!! "+now.strftime("%H:%M"))
        cnt = 1
        obt, spt = dt.score_imp()
        pobt, psbt = dt.score_imp()
        # dt.WriteData()
        # score = (n_obs, n_pts)
        # score = dt.score()
        # if score > 0.5:
        #     lim = len(dt.pts) - dt.fp_ind - 1
        # else:
        #     lim = len(dt.pts) - dt.fp_ind + 20
        #dt.DrawPoint()
        NargWeight = 2
        while cnt<2*(len(dt.pts)-dt.fp_ind):
            if (len(dt.pts)-dt.fp_ind)>200:break
            if cnt > (len(dt.pts)-dt.fp_ind):
                NargWeight += 1
                cnt = 0
            Narg = NargWeight*random.random()
            
            
            # Narg = 10*random.random()*cnt/(len(dt.pts)-dt.fp_ind)
            cnt+=1
            pt_num = random.randint(dt.fp_ind, len(dt.pts)-1)
            dlist = [(sqdist(dt.pts[pt_num], dt.pts[i]), i) for i in range(dt.fp_ind, len(dt.pts))]
            dlist.sort()
            sdist = dlist[1][0]
            for i in range(len(dlist)):
                if dlist[i][0]>sdist*Narg:
                    break
            dinds = [dlist[j][1] for j in range(i)]
            pts = [dt.pts[i] for i in dinds]
            dinds.sort(reverse=True)
            for ind in dinds:
                dt.delete_steiner(ind)
                nobt, nspt = dt.score_imp()
                if nobt<=obt:
                    break
            if obt<nobt:
                solved = False
                for _ in range(len(dinds)-1):
                    dt.step()
                    nobt, nspt = dt.score_imp()
                    if nobt<=obt:
                        solved = True
                        break
                if solved:
                    dt.WriteData()
                    obt = nobt
                    #print(f"[{dt.instance_name}] {cnt}")
                    #print(f"number of obtuse: {pobt} -> {obt}")  
                    #print(f"number of steiner pts: {spt - dt.fp_ind} -> {nspt-dt.fp_ind}")  
                    spt = nspt
                    
                    cnt=0
                else:
                    for _ in range(nspt+len(dinds)-spt):
                        dt.delete_steiner(len(dt.pts)-1)
                    for pt in pts:
                        dt.add_steiner(pt)

                    
            else:
                dt.WriteData()
                obt = nobt
                #print(f"[{dt.instance_name}] {cnt}")
                #print(f"number of obtuse: {pobt} -> {obt}")  
                #print(f"number of steiner pts: {spt - dt.fp_ind} -> {nspt-dt.fp_ind}")  
                spt = nspt
                cnt=0
        now = datetime.datetime.now()
        
        print(f"[{dt.instance_name}] "+now.strftime("%H:%M"))
        print(f"Obtuse Change: {pobt} -> {obt}")  
        print(f"Steiner Pts Change: {psbt - dt.fp_ind} -> {spt-dt.fp_ind}")  
        print("-----------------------------------------------------")