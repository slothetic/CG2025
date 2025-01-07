from MyNum import MyNum
import os
import json
import cv2
import numpy as np
import random
from collections import deque
import pdb
import copy
import math
import collections
import shutil
# import feather

IMP = 1
GRID = 3
MINDIST = MyNum((GRID - (GRID // 2) + 1) * (GRID - (GRID // 2) + 1), IMP * IMP)

from typing import List
import sys
sys.setrecursionlimit(1000000) # to enable DFS

class Point:
    def __init__(self, x, y, id = None):
        # edge list 같이 사용. 리스트의 각 원소는 [pointID, bool] 꼴로, 
        # bool이 true면 constrained edge이고 false면 아님 
        self.incidentPoints = []

        if id == None:
            self.id = -1
        else:
            self.id = id

        if isinstance(x, str):
            a,b = map(int, x.split("/"))
            self.x = MyNum(a,b)
        else:
            self.x = MyNum(x)

        if isinstance(y, str):
            a,b = map(int, y.split("/"))
            self.y = MyNum(a,b)
        else:
            self.y = MyNum(y)

    def __eq__(self, p):
        return self.x==p.x and self.y==p.y
        
    def __str__(self):
        return "("+str(self.x)+", "+str(self.y)+")"
    
    def __ne__(self, p):
        return self.x != p.x or self.y != p.y
    
    def __lt__(self, p):
        return (self.x,self.y)<(p.x,p.y)
    
    def __le__(self, p):
        return (self.x,self.y)<=(p.x,p.y)
    
    def __gt__(self, p):
        return (self.x,self.y)>(p.x,p.y)
    
    def __ge__(self, p):
        return (self.x,self.y)>=(p.x,p.y)

    def print(self):
        print('(', self.x , self.y, ')')

class Triangle:
    def __init__(self, p:int, q:int, r:int):
        self.pts = [p, q, r]

        # neighboring triangles ?
        self.neis = [None, None, None]
    
    def get_ind(self, p:int):
        for i in range(3):
            if self.pts[i] == p:
                return i
            
        return -1
    
    def pt(self, i:int):
        return self.pts[i % 3]
    
    def nei(self, i:int):
        return self.neis[i % 3]

    def getOppositeNeiID(self, ptID):
        return (ptID + 1) % 3

    def getOppositeNei(self, ptID):
        return self.neis[(ptID + 1) % 3]

    # L is a list of points (Data.pts)
    def printPoints(self, L):
        print('\nprintPoints begin\n')
        for i in range(3):
            print('point', i, ",", "index", self.pts[i])
            L[self.pts[i]].print()
        print('\nprintPoints end\n')

    # L is a list of points (Data.pts)
    def printNeis(self, L):
        print('\nprintNeis begin\n')
        for i in range(3):
            if self.neis[i] is not None:
                print('neis', i)
                self.neis[i].printPoints(L)
        print('\nprintNeis end\n')

    # 삼각형의 (한 edge를 이루는) 두 vertex의 index가 주어졌을 때,
    # 나머지 vertex의 index를 반환해주는 함수
    def getThirdVertexID(self, vID1, vID2):
        for vID in self.pts:
            if vID != vID1 and vID != vID2:
                return vID

# free_point index?
# input이 있는 상황이니까 지금은 
# input을 넣어주고.
# triangle을 넣어주고.

# 그럼 해야 하는 게 디버그에서 self 안에 뭐 들어있는지? 아니 그건 당연하잖아.
# read data에서 뭘 하는지 보고 오기.
# 짧은 여행

class Data:
    def __init__(self, input, pts=None, constraints=None, bds=None, fp_ind=None, triangles = None):

        self.ban = set() # ban이 무엇인가

        if input:
            self.input = input #
            self.triangles = set() # triangle의 집합
            self.ReadData() # json 파일 받아오기
            self.done = False # 알고리즘이 완료돼서 올바른 결과를 얻었는지에 해당하는 flag인 듯 ?

        else: # input parameter 0개와 함께 호출된 경우
            self.input = ""
            self.instance_name = ""
            self.fp_ind = fp_ind
            self.pts = pts[:]
            self.region_boundary = bds.copy()
            self.num_constraints = len(constraints) # number of constraints
            self.constraints = constraints.copy() # constraints
            self.triangles = triangles.copy()
            self.done = False # finish flag ?
            self.const_dict = dict() # constraints stored in a dictionary?

            for con in self.constraints:
                self.const_dict[(con[0], con[1])] = (con[0], con[1])
        
    def copy(self):

        new_d = Data( input = "", 
                     pts = self.pts, 
                     constraints = self.constraints, 
                     bds = self.region_boundary, 
                     fp_ind = self.fp_ind, 
                     triangles=self.triangles )
        
        new_d.input = self.input
        new_d.instance_name = self.instance_name
        new_d.const_dict = self.const_dict.copy()
        new_d.done = self.done

        return new_d

    def score(self, p = False):

        obt = 0
        
        for t in self.triangles:
            if self.is_obtuse(t):
                obt+=1

        if obt:
            score = 0.5*(0.9)**(obt-1)

            if p:
                print(f"obtuse num: {obt}, steiner num: {len(self.pts)-self.fp_ind}")

            return score
        
        else:
            # 이거 보면 self.pts가 Steiner points 집합인 것 같고
            # self.fp_ind가 뭐인 것 같은데.

            spt = len(self.pts)- self.fp_ind+1
            score = 0.5+0.5/spt

            if p:
                print(f"obtuse num: {obt}, steiner num: {len(self.pts)-self.fp_ind}")

            return score

    def ReadData(self):
        # print("--------------------ReadData--------------------")

        # challenge instances 안에 있으므로.
        if "challenge_instances_cgshop25" in self.input or "extract_instances" in self.input:
            with open(self.input, "r", encoding="utf-8") as f:
                root = json.load(f)
                
                self.instance_name = root["instance_uid"] # instance 이름 
                self.fp_ind = int(root["num_points"]) # 왜 ind로 해 놓은지는 모르겠지만, point 개수 
                pts_x = root["points_x"] 
                pts_y = root["points_y"]
                self.pts = []

                for i in range(len(pts_y)):
                    self.pts.append(Point(pts_x[i], pts_y[i], i)) # 받아놓은 x들과 y들로 점 정보 저장 (pts에)

                self.region_boundary = deque(root["region_boundary"]) # deque인 이유는 convex hull을 triangulate 해야 돼서?
                self.num_constraints =  root["num_constraints"] # constraint 개수 
                self.constraints = set() 
                self.const_dict = dict() 

                for con in root["additional_constraints"]: # edge를 강제하는 거니까 point 2개로 나타내어짐
                    self.constraints.add((con[0], con[1])) # set 형태로도 추가하고
                    self.const_dict[(con[0], con[1])] = (con[0], con[1]) # dictionary 형태로도 추가

        else:

            with open(self.input, "r", encoding="utf-8") as f:
                root = json.load(f)
                self.instance_name = root["instance_uid"]
                # print(self.instance_name)
                inp = "./challenge_instances_cgshop25/"+self.instance_name+".instance.json"
                st_x = root["steiner_points_x"]
                st_y = root["steiner_points_y"]
                st_pt = []
                for i in range(len(st_x)):
                    st_pt.append(Point(st_x[i], st_y[i]))
                edges = root["edges"]

            with open(inp, "r", encoding="utf-8") as f:
                root = json.load(f)
                self.fp_ind = int(root["num_points"])
                pts_x = root["points_x"]
                pts_y = root["points_y"]
                self.pts = []
                for i in range(len(pts_y)):
                    self.pts.append(Point(pts_x[i], pts_y[i]))
                self.region_boundary = deque(root["region_boundary"])
                self.num_constraints =  root["num_constraints"]
                self.constraints = set()
                self.const_dict = dict()
                for con in root["additional_constraints"]:
                    self.constraints.add((con[0], con[1]))
                    self.const_dict[(con[0], con[1])] = (con[0], con[1])

            self.triangulate()
            self.delaunay_triangulate()
            self.add_steiners(st_pt)
            for e in edges:
                if self.find_triangle(e[0],e[1])==-1 and self.find_triangle(e[1],e[0])!=-1:
                    self.resolve_cross(e)

            self.DrawResult("old_data")    
    
    def MakeInstance(self):
        inst = dict()
        inst["instance_uid"] = self.instance_name
        inst["num_points"] = len(self.pts)
        inst["points_x"] = [p.x.toString() for p in self.pts]
        inst["points_y"] = [p.y.toString() for p in self.pts]
        inst["region_boundary"] = self.region_boundary
        inst["num_constraints"] = 0
        inst["additional_constraints"] = []
        with open("extract_instances/" + self.instance_name + ".instance.json", "w", encoding="utf-8") as f:
            json.dump(inst, f, indent='\t')

    def WriteData(self, name = "",self_update = False):

        print("--------------------WriteData START--------------------")

        if name:
            name = "_" + name

        inst = dict()
        inst["content_type"]="CG_SHOP_2025_Solution"
        inst["instance_uid"]=self.instance_name
        inst["steiner_points_x"] =  list(p.x.toString() for p in self.pts[self.fp_ind:])
        inst["steiner_points_y"] =  list(p.y.toString() for p in self.pts[self.fp_ind:])
        const_edges = []

        for e in self.constraints:
            const_edges.append(sorted(list(e)))

        for i in range(1,len(self.region_boundary)):
            const_edges.append(sorted([self.region_boundary[i-1],self.region_boundary[i]]))

        const_edges.append(sorted([self.region_boundary[-1],self.region_boundary[0]]))
        int_edges = []

        for t in self.triangles:
            e1 = sorted([t.pts[0],t.pts[1]])
            e2 = sorted([t.pts[0],t.pts[2]])
            e3 = sorted([t.pts[1],t.pts[2]])
            # if e1 not in const_edges and e1 not in int_edges:
            #     int_edges.append(e1)
            # if e2 not in const_edges and e2 not in int_edges:
            #     int_edges.append(e2)
            # if e3 not in const_edges and e3 not in int_edges:
            #     int_edges.append(e3)
            if e1 not in int_edges:
                int_edges.append(e1)
            if e2 not in int_edges:
                int_edges.append(e2)
            if e3 not in int_edges:
                int_edges.append(e3)

        obt = 0

        for t in self.triangles:
            if self.is_obtuse(t):
                obt+=1

        inst["edges"] = int_edges
        # print("indstance id: ", self.instance_name)
        # print("Steiner point: ", len(self.pts)-self.fp_ind)
        # print("Total Triangle: ", len(self.triangles))
        # print("Obtuse Triangle: ", obt)
        score = self.score()
        inst["score"] = score
        # print("Score: ", score)

        # print(inst)
        folder = "solutions"

        if self_update:
            with open(self.input, "w", encoding="utf-8") as f:
                json.dump(inst, f, indent='\t')

        with open(folder+"/" + self.instance_name + ".solution" + name + ".json", "w", encoding="utf-8") as f:
            json.dump(inst, f, indent='\t')

        path = "./opt_solutions"
        opt_list = os.listdir(path)
        already_exist = False

        for sol in opt_list:

            if self.instance_name + ".solution.json" in sol:
            # if self.instance_name in sol and "json" in sol:

                already_exist = True
                with open(path+"/"+sol, "r", encoding="utf-8") as ff:
                    root = json.load(ff)
                    if "score" in root:
                        old_score = root["score"]
                    else:
                        dt = Data(path+"/"+sol)
                        old_score = dt.score()

                if old_score<score:
                    print(f"New High Score!!! {old_score}->{score}")
                    os.remove(path+"/"+sol)
                    shutil.copyfile("solutions/" + self.instance_name + ".solution" + name + ".json", "opt_solutions/" + self.instance_name + ".solution.json")
                    # with open("opt_solutions/" + self.instance_name + ".solution.json", "w", encoding="utf-8") as f:
                    #     json.dump(inst, f, indent='\t')
                    self.DrawResult(folder="opt_solutions")

                else:
                    print("Not the best score, but we have done it")

                    # 지우고 다시 파일 적기
                    os.remove(path+"/"+sol)
                    shutil.copyfile("solutions/" + self.instance_name + ".solution" + name + ".json", "opt_solutions/" + self.instance_name + ".solution.json")
                    # with open("opt_solutions/" + self.instance_name + ".solution.json", "w", encoding="utf-8") as f:
                    #     json.dump(inst, f, indent='\t')
                    self.DrawResult(folder="opt_solutions")

                break

        if not already_exist:
            
            print("there was no solution. already_exist = false")

            shutil.copyfile("solutions/" + self.instance_name + ".solution" + name + ".json", "opt_solutions/" + self.instance_name + ".solution.json")
            # with open("opt_solutions/" + self.instance_name + ".solution.json", "w", encoding="utf-8") as f:
            #     json.dump(inst, f, indent='\t')
            self.DrawResult(folder="opt_solutions")

        print("--------------------WriteData END--------------------")

    # def WriteData(self, name = ""):
    #     if name:
    #         name = "_" + name
    #     # print("--------------------WriteData--------------------")
    #     inst = dict()
    #     inst["content_type"]="CG_SHOP_2025_Solution"
    #     inst["instance_uid"]=self.instance_name
    #     inst["steiner_points_x"] =  list(p.x.toString() for p in self.pts[self.fp_ind:])
    #     inst["steiner_points_y"] =  list(p.y.toString() for p in self.pts[self.fp_ind:])
    #     const_edges = []
    #     for e in self.constraints:
    #         const_edges.append(sorted(list(e)))
    #     for i in range(1,len(self.region_boundary)):
    #         const_edges.append(sorted([self.region_boundary[i-1],self.region_boundary[i]]))
    #     const_edges.append(sorted([self.region_boundary[-1],self.region_boundary[0]]))
    #     int_edges = []
    #     for t in self.triangles:
    #         e1 = sorted([t.pts[0],t.pts[1]])
    #         e2 = sorted([t.pts[0],t.pts[2]])
    #         e3 = sorted([t.pts[1],t.pts[2]])
    #         if e1 not in const_edges and e1 not in int_edges:
    #             int_edges.append(e1)
    #         if e2 not in const_edges and e2 not in int_edges:
    #             int_edges.append(e2)
    #         if e3 not in const_edges and e3 not in int_edges:
    #             int_edges.append(e3)
    #     obt = 0
    #     for t in self.triangles:
    #         if self.is_obtuse(t):
    #             obt+=1
    #     inst["edges"] = int_edges
    #     # print("indstance id: ", self.instance_name)
    #     # print("Steiner point: ", len(self.pts)-self.fp_ind)
    #     # print("Total Triangle: ", len(self.triangles))
    #     # print("Obtuse Triangle: ", obt)
    #     score = self.score()
    #     inst["score"] = score
    #     # print("Score: ", score)

    #     # print(inst)
    #     with open("solutions/" + self.instance_name + ".solution" + name + ".json", "w", encoding="utf-8") as f:
    #         json.dump(inst, f, indent='\t')
    #     path = "./opt_solutions"
    #     opt_list = os.listdir(path)
    #     already_exist = False
    #     for sol in opt_list:
    #         if self.instance_name in sol and "json" in sol:
    #             already_exist = True
    #             with open(path+"/"+sol, "r", encoding="utf-8") as ff:
    #                 root = json.load(ff)
    #                 if "score" in root:
    #                     old_score = root["score"]
    #                 else:
    #                     dt = Data(path+"/"+sol)
    #                     old_score = dt.score()
    #             if old_score<score:
    #                 print(f"New High Score!!! {old_score}->{score}")
    #                 os.remove(path+"/"+sol)
    #                 shutil.copyfile("solutions/" + self.instance_name + ".solution" + name + ".json", "opt_solutions/" + self.instance_name + ".solution.json")
    #                 # with open("opt_solutions/" + self.instance_name + ".solution.json", "w", encoding="utf-8") as f:
    #                 #     json.dump(inst, f, indent='\t')
    #                 self.DrawResult(folder="opt_solutions")
    #             break
    #     if not already_exist:
    #         shutil.copyfile("solutions/" + self.instance_name + ".solution" + name + ".json", "opt_solutions/" + self.instance_name + ".solution.json")
    #         # with open("opt_solutions/" + self.instance_name + ".solution.json", "w", encoding="utf-8") as f:
    #         #     json.dump(inst, f, indent='\t')
    #         self.DrawResult(folder="opt_solutions")
                    
    def DrawResult(self, name="", folder = ""):
        print("--------------------DrawResult START--------------------")
        if name:
            name = "_" + name
        minx = min(list(p.x for p in self.pts))
        miny = min(list(p.y for p in self.pts))
        maxx = max(list(p.x for p in self.pts))
        maxy = max(list(p.y for p in self.pts))
        width = int(maxx-minx)
        height = int(maxy-miny)
        rad = 1000/width
        width = int(width*rad)+40
        height = int(height*rad)+40
        minw = 20-int(minx*rad)
        minh = height + int(miny*rad)-20
        img = np.zeros((height, width, 3),dtype="uint8")+255
        rad = MyNum(rad)
        for t in self.triangles:
            if self.is_obtuse(t):
                pts = np.array([[minw+int(rad*self.pts[t.pts[0]].x), minh-int(rad*self.pts[t.pts[0]].y)],[minw+int(rad*self.pts[t.pts[1]].x), minh-int(rad*self.pts[t.pts[1]].y)],[minw+int(rad*self.pts[t.pts[2]].x), minh-int(rad*self.pts[t.pts[2]].y)]], dtype=np.int32).reshape(1,-1,2)
                # print(pts)
                cv2.fillPoly(img, pts, color = (random.randint(50,100),random.randint(50,100),random.randint(50,100)))
            else:
                pts = np.array([[minw+int(rad*self.pts[t.pts[0]].x), minh-int(rad*self.pts[t.pts[0]].y)],[minw+int(rad*self.pts[t.pts[1]].x), minh-int(rad*self.pts[t.pts[1]].y)],[minw+int(rad*self.pts[t.pts[2]].x), minh-int(rad*self.pts[t.pts[2]].y)]], dtype=np.int32).reshape(1,-1,2)
                # print(pts)
                cv2.fillPoly(img, pts, color = (random.randint(240,254),random.randint(240,254),random.randint(240,254)))
        const_edges = []
        for e in self.constraints:
            const_edges.append(sorted(e))
            cv2.line(img, (minw+int(rad*self.pts[e[0]].x),minh-int(rad*self.pts[e[0]].y)), (minw+int(rad*self.pts[e[1]].x),minh-int(rad*self.pts[e[1]].y)), (0,0,255), 2)
        for i in range(1,len(self.region_boundary)):
            const_edges.append(sorted([self.region_boundary[i-1],self.region_boundary[i]]))
            cv2.line(img, (minw+int(rad*self.pts[self.region_boundary[i-1]].x),minh-int(rad*self.pts[self.region_boundary[i-1]].y)), (minw+int(rad*self.pts[self.region_boundary[i]].x),minh-int(rad*self.pts[self.region_boundary[i]].y)), (0,0,0), 2)
        const_edges.append(sorted([self.region_boundary[-1],self.region_boundary[0]]))
        cv2.line(img, (minw+int(rad*self.pts[self.region_boundary[-1]].x),minh-int(rad*self.pts[self.region_boundary[-1]].y)), (minw+int(rad*self.pts[self.region_boundary[0]].x),minh-int(rad*self.pts[self.region_boundary[0]].y)), (0,0,0), 2)
        int_edges = []
        for t in self.triangles:
            e1 = sorted([t.pts[0],t.pts[1]])
            e2 = sorted([t.pts[0],t.pts[2]])
            e3 = sorted([t.pts[1],t.pts[2]])
            if e1 not in const_edges and e1 not in int_edges:
                int_edges.append(e1)
                cv2.line(img, (minw+int(rad*self.pts[e1[0]].x),minh-int(rad*self.pts[e1[0]].y)), (minw+int(rad*self.pts[e1[1]].x),minh-int(rad*self.pts[e1[1]].y)), (0,0,0), 2)
            if e2 not in const_edges and e2 not in int_edges:
                int_edges.append(e2)
                cv2.line(img, (minw+int(rad*self.pts[e2[0]].x),minh-int(rad*self.pts[e2[0]].y)), (minw+int(rad*self.pts[e2[1]].x),minh-int(rad*self.pts[e2[1]].y)), (0,0,0), 2)
            if e3 not in const_edges and e3 not in int_edges:
                int_edges.append(e3)
                cv2.line(img, (minw+int(rad*self.pts[e3[0]].x),minh-int(rad*self.pts[e3[0]].y)), (minw+int(rad*self.pts[e3[1]].x),minh-int(rad*self.pts[e3[1]].y)), (0,0,0), 2)

        # print([p.x for p in self.pts],[p.y for p in self.pts])
        for i,p in enumerate(self.pts):
            if i<self.fp_ind:
                # print(p)
                # print(rad*p.x)
                cv2.circle(img, (minw+int(rad*p.x),minh-int(rad*p.y)), 5,(0,0,0),-1)
                # print((minw+int(rad*p.x),minh-int(rad*p.y)))
            else:
                cv2.circle(img, (minw+int(rad*p.x),minh-int(rad*p.y)), 5,(255,0,0),-1)
        if folder:
            print("directory: ", folder+"/"+self.instance_name + ".solution" + name + ".png")
            cv2.imwrite(folder+"/"+self.instance_name + ".solution" + name + ".png", img)
        else:
            print("directory: ", "solutions/"+self.instance_name + ".solution" + name + ".png")
            cv2.imwrite("solutions/"+self.instance_name + ".solution" + name + ".png", img)

        print("--------------------DrawResult END--------------------")

    def DrawPoint(self, add = ""):
        fontFace = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 1
        color = (255, 0, 0)
        thickness = 2
        lineType = cv2.LINE_AA
        minx = min(list(p.x for p in self.pts))
        miny = min(list(p.y for p in self.pts))
        maxx = max(list(p.x for p in self.pts))
        maxy = max(list(p.y for p in self.pts))
        width = int(maxx-minx)
        height = int(maxy-miny)
        rad = 1000/width
        width = int(width*rad)+40
        height = int(height*rad)+40
        minw = 20-int(minx*rad)
        minh = height + int(miny*rad)-20
        img = np.zeros((height, width, 3),dtype="uint8")+255
        rad = MyNum(rad)
        const_edges = []
        for e in self.constraints:
            const_edges.append(sorted(e))
            cv2.line(img, (minw+int(rad*self.pts[e[0]].x),minh-int(rad*self.pts[e[0]].y)), (minw+int(rad*self.pts[e[1]].x),minh-int(rad*self.pts[e[1]].y)), (0,0,255), 2)
        for i in range(1,len(self.region_boundary)):
            const_edges.append(sorted([self.region_boundary[i-1],self.region_boundary[i]]))
            cv2.line(img, (minw+int(rad*self.pts[self.region_boundary[i-1]].x),minh-int(rad*self.pts[self.region_boundary[i-1]].y)), (minw+int(rad*self.pts[self.region_boundary[i]].x),minh-int(rad*self.pts[self.region_boundary[i]].y)), (0,0,0), 2)
        const_edges.append(sorted([self.region_boundary[-1],self.region_boundary[0]]))
        cv2.line(img, (minw+int(rad*self.pts[self.region_boundary[-1]].x),minh-int(rad*self.pts[self.region_boundary[-1]].y)), (minw+int(rad*self.pts[self.region_boundary[0]].x),minh-int(rad*self.pts[self.region_boundary[0]].y)), (0,0,0), 2)
        int_edges = []
        for t in self.triangles:
            e1 = sorted([t.pts[0],t.pts[1]])
            e2 = sorted([t.pts[0],t.pts[2]])
            e3 = sorted([t.pts[1],t.pts[2]])
            if e1 not in const_edges and e1 not in int_edges:
                int_edges.append(e1)
                cv2.line(img, (minw+int(rad*self.pts[e1[0]].x),minh-int(rad*self.pts[e1[0]].y)), (minw+int(rad*self.pts[e1[1]].x),minh-int(rad*self.pts[e1[1]].y)), (0,0,0), 2)
            if e2 not in const_edges and e2 not in int_edges:
                int_edges.append(e2)
                cv2.line(img, (minw+int(rad*self.pts[e2[0]].x),minh-int(rad*self.pts[e2[0]].y)), (minw+int(rad*self.pts[e2[1]].x),minh-int(rad*self.pts[e2[1]].y)), (0,0,0), 2)
            if e3 not in const_edges and e3 not in int_edges:
                int_edges.append(e3)
                cv2.line(img, (minw+int(rad*self.pts[e3[0]].x),minh-int(rad*self.pts[e3[0]].y)), (minw+int(rad*self.pts[e3[1]].x),minh-int(rad*self.pts[e3[1]].y)), (0,0,0), 2)

        for i,p in enumerate(self.pts):
            if i<self.fp_ind:
                # print(p)
                # print(rad*p.x)
                cv2.circle(img, (minw+int(rad*p.x),minh-int(rad*p.y)), 5,(0,0,0),-1)
                cv2.putText(img, str(i), (minw+int(rad*p.x)+10,minh-int(rad*p.y)+10), fontFace, fontScale, (0,0,0), thickness, lineType)
                # print((minw+int(rad*p.x),minh-int(rad*p.y)))
            else:
                cv2.circle(img, (minw+int(rad*p.x),minh-int(rad*p.y)), 5,(255,0,0),-1)
                cv2.putText(img, str(i), (minw+int(rad*p.x)+10,minh-int(rad*p.y)+10), fontFace, fontScale, (255,0,0), thickness, lineType)
            
        if add=="":
            cv2.imwrite("solutions/"+self.instance_name+".point.png", img)
        else:
            cv2.imwrite("solutions/"+self.instance_name+".point_"+add+".png", img)

    def is_obtuse(self, t:Triangle):
        q1 = self.pts[t.pts[0]]
        q2 = self.pts[t.pts[1]]
        q3 = self.pts[t.pts[2]]
        if (angle(q1,q2,q3) > MyNum(0)): return True
        if (angle(q2,q3,q1) > MyNum(0)): return True
        if (angle(q3,q1,q2) > MyNum(0)): return True
        return False

    def is_on(self, e1:int, e2:int, p:Point):
        q1 = self.pts[e1]
        q2 = self.pts[e2]
        if (turn(q1, q2, p) == MyNum(0)):
            if (q1.x == q2.x):
                y1 = min(q1.y, q2.y)
                y2 = max(q1.y, q2.y)
                return (y1 < p.y) and (p.y < y2)
            else:
                x1 = min(q1.x, q2.x)
                x2 = max(q1.x, q2.x)
                return (x1 < p.x) and (p.x < x2)
        else:
            return False
    
    def is_in(self, t:Triangle, p:Point):
        q1 = self.pts[t.pts[0]]
        q2 = self.pts[t.pts[1]]
        q3 = self.pts[t.pts[2]]
        z = MyNum(0)
        return (turn(q1,q2,p)>=z) and (turn(q2,q3,p)>=z) and (turn(q3,q1,p)>=z)

    def is_in_circumcircle(self, t:Triangle, q:Point):
        p1, p2, p3 = [self.pts[t.pts[i]] for i in range(3)]
        if p1.y == p2.y:
            p1, p2, p3 = p2, p3, p1
        if p2.y == p3.y:
            p1, p2, p3 = p3, p1, p2
        m12 = midpoint(p1, p2)
        m23 = midpoint(p2, p3)
        s12 = (p1.x - p2.x) / (p2.y - p1.y)
        b12 = m12.y - m12.x * s12
        s23 = (p2.x - p3.x) / (p3.y - p2.y)
        b23 = m23.y - m23.x * s23
        #print(p1, p2, p3)
        ox = (b23 - b12) / (s12 - s23)
        oy = s23 * ox + b23
        o = Point(ox, oy)
        return sqdist(o, q) < sqdist(o, p1)

    def is_on_circumcircle(self, t:Triangle, q:Point):
        p1, p2, p3 = [self.pts[t.pts[i]] for i in range(3)]
        if p1.y == p2.y:
            p1, p2, p3 = p2, p3, p1
        if p2.y == p3.y:
            p1, p2, p3 = p3, p1, p2
        m12 = midpoint(p1, p2)
        m23 = midpoint(p2, p3)
        s12 = (p1.x - p2.x) / (p2.y - p1.y)
        b12 = m12.y - m12.x * s12
        s23 = (p2.x - p3.x) / (p3.y - p2.y)
        b23 = m23.y - m23.x * s23
        #print(p1, p2, p3)
        ox = (b23 - b12) / (s12 - s23)
        oy = s23 * ox + b23
        o = Point(ox, oy)
        return sqdist(o, q) == sqdist(o, p1)


    def triangulate(self):
        check = [False] * len(self.pts)
        # self.triangulate_polygon(deque(self.region_boundary))
        for d in self.region_boundary:
            check[d] = True
        for i in range(len(self.pts)):
            if not check[i]:
                p = self.pts[i]
                for j in range(len(self.region_boundary)):
                    if self.is_on(self.region_boundary[j - 1], self.region_boundary[j], p):
                        self.region_boundary.insert(j, i)
                        check[i] = True
                        break
                for e in self.constraints:
                    if self.is_on(e[0], e[1], p):
                        self.constraints.add((e[0],i))
                        self.constraints.add((e[1],i))
                        self.const_dict[(e[0], i)] = self.const_dict[e]
                        self.const_dict[(e[1], i)] = self.const_dict[e]
                        del self.const_dict[e]
                        self.constraints.remove(e)
                        break
        self.triangulate_polygon(deque(self.region_boundary))
        for i in range(len(self.pts)):
            if not check[i]:
                self.insert_point(i)
        for con in self.constraints:
            self.resolve_cross(con)


    def triangulate_polygon(self, polygon:deque):
        if len(polygon) == 3:
            nt = Triangle(polygon[0], polygon[1], polygon[2])
            self.triangles.add(nt)
        else:
            while turn(self.pts[polygon[-1]], self.pts[polygon[0]], self.pts[polygon[1]]) <= MyNum(0):
                polygon.append(polygon.popleft())
            nt = Triangle(polygon[-1], polygon[0], polygon[1])
            c = -1
            q = self.pts[polygon[0]]
            cd = max(sqdist(q, self.pts[polygon[-1]]), sqdist(q, self.pts[polygon[1]]))
            for i in range(2, len(polygon) - 1):
                if self.is_in(nt, self.pts[polygon[i]]):
                    d = sqdist(q, self.pts[polygon[i]])
                    if d < cd:
                        cd = d
                        c = i
            if c == -1:
                self.triangles.add(nt)
                subp = deque(list(polygon)[1:])
                self.triangulate_polygon(subp)
                tt = self.find_triangle(nt.pts[0], nt.pts[2])
                nt.neis[2] = tt
                tt.neis[tt.get_ind(nt.pts[0])] = nt
            else:
                del nt
                poly1 = deque(list(polygon)[:c + 1])
                poly2 = deque(list(polygon)[c:])
                poly2.append(polygon[0])
                self.triangulate_polygon(poly1)
                t1 = self.find_triangle(polygon[c], polygon[0])
                self.triangulate_polygon(poly2)
                t2 = self.find_triangle(polygon[0], polygon[c])
                t1.neis[t1.get_ind(polygon[c])] = t2
                t2.neis[t2.get_ind(polygon[0])] = t1
    

    def insert_point(self, p:int):
        q = self.pts[p]
        for t in self.triangles:
            if self.is_in(t, q):
                break
        tt = None
        if self.is_on(t.pts[0], t.pts[1], q):
            i = 0
            tt = t.neis[0]
        elif self.is_on(t.pts[1], t.pts[2], q):
            i = 1
            tt = t.neis[1]
        elif self.is_on(t.pts[2], t.pts[0], q):
            i = 2
            tt = t.neis[2]
        if tt:
            j = tt.get_ind(t.pt(i + 1))
            t1 = Triangle(p, t.pt(i + 1), t.pt(i + 2))
            t1.neis[0] = tt
            ti = t.nei(i + 1)
            if ti:
                ti.neis[ti.get_ind(t1.pts[2])] = t1
            t1.neis[1] = ti
            t1.neis[2] = t
            t2 = Triangle(p, tt.pt(j + 1), tt.pt(j + 2))
            t2.neis[0] = t
            tj = tt.nei(j + 1)
            if tj:
                tj.neis[tj.get_ind(t2.pts[2])] = t2
            t2.neis[1] = tj
            t2.neis[2] = tt
            t.pts[(i + 1) % 3] = p
            t.neis[i] = t2
            t.neis[(i + 1) % 3] = t1
            tt.pts[(j + 1) % 3] = p
            tt.neis[j] = t1
            tt.neis[(j + 1) % 3] = t2
            self.triangles.add(t1)
            self.triangles.add(t2)
        else:
            t1 = Triangle(p, t.pts[1], t.pts[2])
            tt1 = t.neis[1]
            t1.neis[1] = tt1
            if tt1:
                tt1.neis[tt1.get_ind(t.pts[2])] = t1
            t2 = Triangle(p, t.pts[2], t.pts[0])
            tt2 = t.neis[2]
            t2.neis[1] = tt2
            if tt2:
                tt2.neis[tt2.get_ind(t.pts[0])] = t2
            t.pts[2] = p
            t.neis[1] = t1
            t.neis[2] = t2
            t1.neis[0] = t
            t1.neis[2] = t2
            t2.neis[0] = t1
            t2.neis[2] = t
            self.triangles.add(t1)
            self.triangles.add(t2)
    
    def resolve_cross(self, con:tuple, t=None):
        if not t:
            q1 = con[0]
            q2 = con[1]
            for t in self.triangles:
                i = t.get_ind(q1)
                if i != -1:
                    r1 = self.pts[q1]
                    r2 = self.pts[t.pt(i + 1)]
                    r3 = self.pts[t.pt(i + 2)]
                    r4 = self.pts[q2]
                    if (turn(r1, r2, r4) < 0 or turn(r1, r3, r4) > 0):
                        continue
                    if r2 == r4:
                        tt = t.neis[i]
                        t.neis[i] = None
                        tt.neis[tt.get_ind(q2)] = None
                    elif r3 == r4:
                        tt = t.nei(i + 2)
                        t.neis[(i + 2) % 3] = None
                        tt.neis[tt.get_ind(q1)] = None
                    else:
                        self.resolve_cross(con, t)
                    break
        else:
            q1 = con[0]
            q2 = con[1]
            i = t.get_ind(q1)
            self.flip(t, (i + 1) % 3)
            r = t.pt(i + 2)
            if (r == q2):
                tt = t.nei(i + 2)
                tt.neis[tt.get_ind(t.pts[i])] = None
                t.neis[(i + 2) % 3] = None
            elif (turn(self.pts[q2], self.pts[q1], self.pts[r]) < 0):
                return self.resolve_cross(con, t)
            else:
                return self.resolve_cross(con, t.nei(i + 2))

    def flip_old(self, t:Triangle, i:int):
        tt = t.neis[i]
        j = tt.get_ind(t.pt(i + 1))
        pi = t.pt(i + 2)
        pj = tt.pt(j + 2)
        bi = turn(self.pts[pi], self.pts[t.pts[i]], self.pts[pj]) > 0
        bj = turn(self.pts[pi], self.pts[tt.pts[j]], self.pts[pj]) < 0
        if bi and bj:
            ti = t.nei(i + 1)
            tj = tt.nei(j + 1)
            t.pts[(i + 1) % 3] = pj
            t.neis[i] = tj
            if tj:
                tj.neis[tj.get_ind(pj)] = t
            t.neis[(i + 1) % 3] = tt
            tt.pts[(j + 1) % 3] = pi
            tt.neis[j] = ti
            if ti:
                ti.neis[ti.get_ind(pi)] = tt
            tt.neis[(j + 1) % 3] = t
        elif not bi:
            ttt = tt.nei(j + 2)
            k = (ttt.get_ind(tt.pts[j]) + 2) % 3
            pk = ttt.pts[k]
            if turn(self.pts[pi], self.pts[tt.pts[j]], self.pts[pk]) >= 0:
                self.flip_old(ttt, (k + 2) % 3)
            else:
                self.flip_old(tt, (j + 2) % 3)
            return self.flip_old(t, i)
        else:
            ttt = tt.nei(j + 1)
            k = (ttt.get_ind(tt.pt(j + 2)) + 2) % 3
            pk = ttt.pts[k]
            if turn(self.pts[pi], self.pts[t.pts[i]], self.pts[pk]) <= 0:
                self.flip_old(ttt, k)
            else:
                self.flip_old(tt, (j + 1) % 3)
            return self.flip_old(t, i)

    def flip(self, t:Triangle, i:int):
        tt = t.neis[i]
        j = tt.get_ind(t.pt(i + 1))
        p = self.pts[t.pt(i + 2)]
        pr = self.pts[t.pts[i]]
        pl = self.pts[t.pt(i + 1)]
        q = self.pts[tt.pt(j + 2)]
        # self.print_triangle(t)
        # print("flipping in", i)
        # self.print_triangle(tt)
        while True:
            if turn(p, pr, q) <= 0:
                t = tt
                i = (j + 2) % 3
                pr = q
            elif turn(self.pts[t.pt(i + 2)], self.pts[t.pts[i]], q) <= 0:
                t = tt
                i = (j + 2) % 3
            elif turn(p, pl, q) >= 0:
                pl = q
                t = tt
                i = (j + 1) % 3
            elif turn(self.pts[t.pt(i + 2)], self.pts[tt.pts[j]], q) >= 0:
                t = tt
                i = (j + 1) % 3
            else:
                break
            tt = t.neis[i]
            j = tt.get_ind(t.pt(i + 1))
            q = self.pts[tt.pt(j + 2)]
            # self.print_triangle(t)
            # print("flipping in", i)
            # self.print_triangle(tt)
        ti = t.nei(i + 1)
        tj = tt.nei(j + 1)
        pi = t.pt(i + 2)
        pj = tt.pt(j + 2)
        t.pts[(i + 1) % 3] = pj
        t.neis[i] = tj
        if tj:
            tj.neis[tj.get_ind(pj)] = t
        t.neis[(i + 1) % 3] = tt
        tt.pts[(j + 1) % 3] = pi
        tt.neis[j] = ti
        if ti:
            ti.neis[ti.get_ind(pi)] = tt
        tt.neis[(j + 1) % 3] = t
        # print('Flip done!')
    
    # 주어진 triangulation을, flip을 통해 delaunay triangulation로 바꾸는 함수
    def delaunay_triangulate(self):
        while True:
            check = False
            for t in self.triangles:
                for i in range(3):
                    if t.neis[i]:
                        q = self.pts[t.neis[i].pt(t.neis[i].get_ind(t.pts[i]) + 1)]
                        if self.is_in_circumcircle(t, q):
                            self.flip(t, i)
                            check = True
                            break
                        elif self.is_on_circumcircle(t, q) and self.is_obtuse(t):
                            self.flip(t, i)
                            break
            if not check:
                break

    def minmax_triangulate(self):
        while True:
            maxang = MyNum(0)
            mt = None
            for t in self.triangles:
                ang = angle(self.pts[t.pts[2]], self.pts[t.pts[0]], self.pts[t.pts[1]])
                if ang > maxang:
                    mt = t
                    maxang = ang
                    i = 0
                ang = angle(self.pts[t.pts[0]], self.pts[t.pts[1]], self.pts[t.pts[2]])
                if ang > maxang:
                    mt = t
                    maxang = ang
                    i = 1
                ang = angle(self.pts[t.pts[1]], self.pts[t.pts[2]], self.pts[t.pts[0]])
                if ang > maxang:
                    mt = t
                    maxang = ang
                    i = 2
            if (not mt) or (not self.ear_cut(mt, i)):
                break
    
    def ear_cut(self, t:Triangle, i:int):
        q = self.pts[t.pts[i]]
        r = self.pts[t.pt(i + 1)]
        l = self.pts[t.pt(i + 2)]
        ang = angle(l, q, r)
        removed = set()
        inserted = set()
        l_neis = []
        r_neis = []
        l_chain = []
        r_chain = []
        works = set()
        removed.add(t)
        r_chain.append(t.pts[i])
        r_chain.append(t.pt(i + 1))
        l_chain.append(t.pts[i])
        l_chain.append(t.pt(i + 2))
        if t.neis[i]:
            r_neis.append((t.neis[i], t.neis[i].get_ind(t.pt(i + 1))))
        else:
            r_neis.append((None, 0))
        if t.nei(i + 2):
            l_neis.append((t.nei(i + 2), t.nei(i + 2).get_ind(t.pts[i])))
        else:
            l_neis.append((None, 0))
        tt = t.nei(i + 1)
        stop = [False]
        s = q
        j = i
        def cutright():
            if turn(self.pts[r_chain[-2]], self.pts[r_chain[-1]], s) <= 0 or angle(self.pts[r_chain[-2]], self.pts[r_chain[-1]], s) >= ang:
                stop[0] = True
            else:
                nt = Triangle(tt.pts[j], r_chain[-2], r_chain[-1])
                inserted.add(nt)
                nt.neis[2] = r_neis[-1][0]
                if nt.neis[2]:
                    works.add((nt.neis[2], r_neis[-1][1], nt))
                r_neis.pop()
                nt.neis[1] = r_neis[-1][0]
                if nt.neis[1]:
                    works.add((nt.neis[1], r_neis[-1][1], nt))
                r_neis.pop()
                r_neis.append((nt, 0))
                r_chain.pop()
        def cutleft():
            if turn(self.pts[l_chain[-2]], self.pts[l_chain[-1]], s) >= 0 or angle(self.pts[l_chain[-2]], self.pts[l_chain[-1]], s) >= ang:
                stop[0] = True
            else:
                nt = Triangle(l_chain[-1], l_chain[-2], tt.pts[j])
                inserted.add(nt)
                nt.neis[2] = l_neis[-1][0]
                if nt.neis[2]:
                    works.add((nt.neis[2], l_neis[-1][1], nt))
                l_neis.pop()
                nt.neis[0] = l_neis[-1][0]
                if nt.neis[0]:
                    works.add((nt.neis[0], l_neis[-1][1], nt))
                l_neis.pop()
                l_neis.append((nt, 1))
                l_chain.pop()
        def abort():
            for nt in inserted:
                del nt
        while True:
            if not tt:
                abort()
                return False
            stop[0] = False
            j = (tt.get_ind(r_chain[-1]) + 1) % 3
            s = self.pts[tt.pts[j]]
            removed.add(tt)
            ttt = tt.neis[j]
            if ttt:
                l_neis.append((ttt, ttt.get_ind(tt.pt(j + 1))))
            else:
                l_neis.append((None, 0))
            ttt = tt.nei(j + 2)
            if ttt:
                r_neis.append((ttt, ttt.get_ind(tt.pts[j])))
            else:
                r_neis.append((None, 0))
            if turn(q, r, s) <= 0:
                while not stop[0]:
                    cutright()
                r_chain.append(tt.pts[j])
                tt = l_neis[-1][0]
                l_neis.pop()
            elif turn(q, l, s) >= 0:
                while not stop[0]:
                    cutleft()
                l_chain.append(tt.pts[j])
                tt = r_neis[-1][0]
                r_neis.pop()
            else:
                while (not stop[0]) and len(r_chain) > 2:
                    cutright()
                stop[0] = False
                while (not stop[0]) and len(l_chain) > 2:
                    cutleft()
                rsgn = turn(self.pts[r_chain[-2]], self.pts[r_chain[-1]], s) <= 0 or angle(self.pts[r_chain[-2]], self.pts[r_chain[-1]], s) >= ang
                lsgn = turn(self.pts[l_chain[-2]], self.pts[l_chain[-1]], s) >= 0 or angle(self.pts[l_chain[-2]], self.pts[l_chain[-1]], s) >= ang
                if (not rsgn) and (not lsgn):
                    break
                elif not rsgn:
                    l = s
                    l_chain.append(tt.pts[j])
                    tt = r_neis[-1][0]
                    r_neis.pop()
                elif not lsgn:
                    r = s
                    r_chain.append(tt.pts[j])
                    tt = l_neis[-1][0]
                    l_neis.pop()
                else:
                    abort()
                    return False
        t1 = Triangle(r_chain[0], r_chain[1], tt.pts[j])
        t2 = Triangle(tt.pts[j], l_chain[1], l_chain[0])
        t1.neis[0] = r_neis[0][0]
        if t1.neis[0]:
            r_neis[0][0].neis[r_neis[0][1]] = t1
        t1.neis[1] = r_neis[1][0]
        if t1.neis[1]:
            r_neis[1][0].neis[r_neis[1][1]] = t1
        t1.neis[2] = t2
        t2.neis[0] = l_neis[1][0]
        if t2.neis[0]:
            l_neis[1][0].neis[l_neis[1][1]] = t2
        t2.neis[1] = l_neis[0][0]
        if t2.neis[1]:
            l_neis[0][0].neis[l_neis[0][1]] = t2
        t2.neis[2] = t1
        for dt in removed:
            self.triangles.discard(dt)
            inserted.discard(dt)
            del dt
        self.triangles.add(t1)
        self.triangles.add(t2)
        for nt in inserted:
            self.triangles.add(nt)
        for w1, w2, w3 in works:
            w1.neis[w2] = w3
        return True

    # 이게 unique하다는 얘기는, 변으로 맞닿아있는 두 triangle의 vertex 인덱스가 항상 둘다 CW 혹은 CCW임을 의미
    def find_triangle(self, q1:int, q2:int):
        for t in self.triangles:
            if t.pts[0] == q1 and t.pts[1] == q2:
                return t
            if t.pts[1] == q1 and t.pts[2] == q2:
                return t
            if t.pts[2] == q1 and t.pts[0] == q2:
                return t
        return None

    def addSteinerNoTriangulation(self, p:Point):
        
        self.pts.append(p)
        
        # constraint edge 위에 있다면 edge를 둘로 쪼개줌
        for e in self.constraints:
            if self.is_on(e[0], e[1], p):
                self.constraints.add((e[0],len(self.pts) - 1))
                self.constraints.add((e[1],len(self.pts) - 1))
                self.const_dict[(e[0], len(self.pts) - 1)] = self.const_dict[e]
                self.const_dict[(e[1], len(self.pts) - 1)] = self.const_dict[e]
                del self.const_dict[e]
                self.constraints.remove(e)
                break

    def add_steiner(self, p:Point, on_constraint = set()):

        # edge 위에 있으면 안 되므로
        for e in self.ban:
            if self.is_on(e[0], e[1], p):
                return
            
        self.pts.append(p)
        
        for i in range(len(self.region_boundary)):
            if self.is_on(self.region_boundary[i - 1], self.region_boundary[i], p):
                self.region_boundary.insert(i, len(self.pts) - 1)
                break
        
        for e in self.constraints:
            if self.is_on(e[0], e[1], p):
                self.constraints.add((e[0],len(self.pts) - 1))
                self.constraints.add((e[1],len(self.pts) - 1))
                self.const_dict[(e[0], len(self.pts) - 1)] = self.const_dict[e]
                self.const_dict[(e[1], len(self.pts) - 1)] = self.const_dict[e]
                del self.const_dict[e]
                self.constraints.remove(e)
                break

        for t in self.triangles:
            del t

        self.triangles = set()
        self.triangulate() # 다시 triangulate?
        self.delaunay_triangulate()

    def add_steiners(self, l:list):
        for p in l:
            cont = True
            for e in self.ban: # 아니 이게 뭔데 self.ban이
                if self.is_on(e[0], e[1], p):
                    cont = False
                    break
            if cont==False:
                continue
            self.pts.append(p)
            for i in range(len(self.region_boundary)):
                if self.is_on(self.region_boundary[i - 1], self.region_boundary[i], p):
                    self.region_boundary.insert(i, len(self.pts) - 1)
                    break
            for e in self.constraints:
                if self.is_on(e[0], e[1], p):
                    self.constraints.add((e[0],len(self.pts) - 1))
                    self.constraints.add((e[1],len(self.pts) - 1))
                    self.const_dict[(e[0], len(self.pts) - 1)] = self.const_dict[e]
                    self.const_dict[(e[1], len(self.pts) - 1)] = self.const_dict[e]
                    del self.const_dict[e]
                    self.constraints.remove(e)
                    break

        for t in self.triangles:
            del t
        self.triangles = set()
        self.triangulate()
        self.delaunay_triangulate()
        
    def delete_steiner(self, i:int):
        if i > len(self.pts):
            raise Exception("There is no such point to delete")
        if i < self.fp_ind:
            pass
        if i in self.region_boundary:
            self.region_boundary.remove(i)
        i_connect = []
        e_list = []
        for e in self.constraints:
            if e[0]==i:
                i_connect.append(e[1])
                e_list.append(e)
            if e[1]==i:
                i_connect.append(e[0])
                e_list.append(e)
        if i_connect:
            self.constraints.add(tuple(i_connect))
        for e in e_list:
            self.const_dict[tuple(i_connect)] = self.const_dict[e]
            self.constraints.remove(e)
            del self.const_dict[e]
        if i!=len(self.pts) - 1:
            self.pts[i] = self.pts[-1]
            # for t in self.triangles:
            #     if t.get_ind(len(self.pts) - 1) != -1:
            #         t.pts[t.get_ind(len(self.pts)-1)] = i
            for j in range(len(self.region_boundary)):
                if self.region_boundary[j] == len(self.pts) - 1:
                    self.region_boundary[j] = i
            delcon = set()
            newcon = set()
            for con in self.constraints:
                if con[0] == len(self.pts) - 1:
                    delcon.add(con)
                    newcon.add((i, con[1]))
                    self.const_dict[(i, con[1])] = self.const_dict[con]
                    del self.const_dict[con]
                elif con[1] == len(self.pts) - 1:
                    delcon.add(con)
                    newcon.add((con[0], i))
                    self.const_dict[(con[0], i)] = self.const_dict[con]
                    del self.const_dict[con]
            for con in delcon:
                self.constraints.remove(con)
            for con in newcon:
                self.constraints.add(con)
        self.pts.pop()
        for t in self.triangles:
           del t
        self.triangles = set()
        self.triangulate()
        self.delaunay_triangulate()

    def delete_steiners(self, l:list):
        l.sort(reverse=True)
        for i in l:
            if i > len(self.pts):
                raise Exception("There is no such point to delete")
        for i in l:
            if i < self.fp_ind:
                pass
            if i in self.region_boundary:
                self.region_boundary.remove(i)
            i_connect = []
            e_list = []
            for e in self.constraints:
                if e[0]==i:
                    i_connect.append(e[1])
                    e_list.append(e)
                if e[1]==i:
                    i_connect.append(e[0])
                    e_list.append(e)
            if i_connect:
                self.constraints.add(tuple(i_connect))
            for e in e_list:
                self.const_dict[tuple(i_connect)] = self.const_dict[e]
                self.constraints.remove(e)
                del self.const_dict[e]
            if i!=len(self.pts) - 1:
                self.pts[i] = self.pts[-1]
                # for t in self.triangles:
                #     if t.get_ind(len(self.pts) - 1) != -1:
                #         t.pts[t.get_ind(len(self.pts)-1)] = i
                for j in range(len(self.region_boundary)):
                    if self.region_boundary[j] == len(self.pts) - 1:
                        self.region_boundary[j] = i
                delcon = set()
                newcon = set()
                for con in self.constraints:
                    if con[0] == len(self.pts) - 1:
                        delcon.add(con)
                        newcon.add((i, con[1]))
                        self.const_dict[(i, con[1])] = self.const_dict[con]
                        del self.const_dict[con]
                    elif con[1] == len(self.pts) - 1:
                        delcon.add(con)
                        newcon.add((con[0], i))
                        self.const_dict[(con[0], i)] = self.const_dict[con]
                        del self.const_dict[con]
                for con in delcon:
                    self.constraints.remove(con)
                for con in newcon:
                    self.constraints.add(con)
            self.pts.pop()
        for t in self.triangles:
            del t
        self.triangles = set()
        self.triangulate()
        self.delaunay_triangulate()
                    
    def make_non_obtuse(self, t:Triangle):
        #print("resolve obtuse")
        #self.print_triangle(t)
        if (angle(self.pts[t.pts[2]], self.pts[t.pts[0]], self.pts[t.pts[1]]) > 0):
            i = 0
        if (angle(self.pts[t.pts[0]], self.pts[t.pts[1]], self.pts[t.pts[2]]) > 0):
            i = 1
        if (angle(self.pts[t.pts[1]], self.pts[t.pts[2]], self.pts[t.pts[0]]) > 0):
            i = 2
        #print("obtuse at", i)
        q = self.pts[t.pts[i]]
        r = self.pts[t.pt(i + 1)]
        l = self.pts[t.pt(i + 2)]
        l_neis = []
        r_neis = []
        l_chain = []
        r_chain = []
        self.triangles.remove(t)
        r_chain.append(t.pts[i])
        r_chain.append(t.pt(i + 1))
        l_chain.append(t.pts[i])
        l_chain.append(t.pt(i + 2))
        if t.neis[i]:
            r_neis.append((t.neis[i], t.neis[i].get_ind(t.pt(i + 1))))
        else:
            r_neis.append((None, 0))
        if t.nei(i + 2):
            l_neis.append((t.nei(i + 2), t.nei(i + 2).get_ind(t.pts[i])))
        else:
            l_neis.append((None, 0))
        tt = t.nei(i + 1)
        stop = [False]
        s = q
        j = i
        def cutright():
            if turn(self.pts[r_chain[-2]], self.pts[r_chain[-1]], s) <= 0 or angle(self.pts[r_chain[-2]], self.pts[r_chain[-1]], s) > 0:
                stop[0] = True
            else:
                nt = Triangle(tt.pts[j], r_chain[-2], r_chain[-1])
                self.triangles.add(nt)
                nt.neis[2] = r_neis[-1][0]
                if nt.neis[2]:
                    nt.neis[2].neis[r_neis[-1][1]] = nt
                r_neis.pop()
                nt.neis[1] = r_neis[-1][0]
                if nt.neis[1]:
                    nt.neis[1].neis[r_neis[-1][1]] = nt
                r_neis.pop()
                r_neis.append((nt, 0))
                r_chain.pop()
                #print("line 697")
                #self.print_triangle(nt)
        def cutleft():
            if turn(self.pts[l_chain[-2]], self.pts[l_chain[-1]], s) >= 0 or angle(self.pts[l_chain[-2]], self.pts[l_chain[-1]], s) > 0:
                stop[0] = True
            else:
                nt = Triangle(l_chain[-1], l_chain[-2], tt.pts[j])
                self.triangles.add(nt)
                nt.neis[2] = l_neis[-1][0]
                if nt.neis[2]:
                    nt.neis[2].neis[l_neis[-1][1]] = nt
                l_neis.pop()
                nt.neis[0] = l_neis[-1][0]
                if nt.neis[0]:
                    nt.neis[0].neis[l_neis[-1][1]] = nt
                l_neis.pop()
                l_neis.append((nt, 1))
                l_chain.pop()
                #print("line 715")
                #self.print_triangle(nt)
        while True:
            if not tt:
                break
            #self.print_triangle(tt)
            stop[0] = False
            j = (tt.get_ind(r_chain[-1]) + 1) % 3
            s = self.pts[tt.pts[j]]
            self.triangles.discard(tt)
            # self.DrawResult("step")
            #input("view next step:")
            ttt = tt.neis[j]
            if ttt:
                l_neis.append((ttt, ttt.get_ind(tt.pt(j + 1))))
            else:
                l_neis.append((None, 0))
            ttt = tt.nei(j + 2)
            if ttt:
                r_neis.append((ttt, ttt.get_ind(tt.pts[j])))
            else:
                r_neis.append((None, 0))
            if turn(q, r, s) <= 0:
                while not stop[0]:
                    cutright()
                r_chain.append(tt.pts[j])
                tt = l_neis[-1][0]
                l_neis.pop()
            elif turn(q, l, s) >= 0:
                while not stop[0]:
                    cutleft()
                l_chain.append(tt.pts[j])
                tt = r_neis[-1][0]
                r_neis.pop()
            else:
                while (not stop[0]) and len(r_chain) > 2:
                    cutright()
                stop[0] = False
                while (not stop[0]) and len(l_chain) > 2:
                    cutleft()
                rsgn = turn(self.pts[r_chain[-2]], self.pts[r_chain[-1]], s) <= 0 or angle(self.pts[r_chain[-2]], self.pts[r_chain[-1]], s) > 0
                lsgn = turn(self.pts[l_chain[-2]], self.pts[l_chain[-1]], s) >= 0 or angle(self.pts[l_chain[-2]], self.pts[l_chain[-1]], s) > 0
                if (not rsgn) and (not lsgn):
                    t1 = Triangle(r_chain[0], r_chain[1], tt.pts[j])
                    t2 = Triangle(tt.pts[j], l_chain[1], l_chain[0])
                    t1.neis[0] = r_neis[0][0]
                    if t1.neis[0]:
                        r_neis[0][0].neis[r_neis[0][1]] = t1
                    t1.neis[1] = r_neis[1][0]
                    if t1.neis[1]:
                        r_neis[1][0].neis[r_neis[1][1]] = t1
                    t1.neis[2] = t2
                    t2.neis[0] = l_neis[1][0]
                    if t2.neis[0]:
                        l_neis[1][0].neis[l_neis[1][1]] = t2
                    t2.neis[1] = l_neis[0][0]
                    if t2.neis[1]:
                        l_neis[0][0].neis[l_neis[0][1]] = t2
                    t2.neis[2] = t1
                    self.triangles.add(t1)
                    self.triangles.add(t2)
                    #print("line 785")
                    #self.print_triangle(t1)
                    #self.print_triangle(t2)
                    return
                elif not rsgn:
                    l = s
                    l_chain.append(tt.pts[j])
                    tt = r_neis[-1][0]
                    r_neis.pop()
                elif not lsgn:
                    r = s
                    r_chain.append(tt.pts[j])
                    tt = l_neis[-1][0]
                    l_neis.pop()
                else:
                    r_chain.append(tt.pts[j])
                    tt = l_neis[-1][0]
                    j = l_neis[-1][1]
                    l_neis.pop()
        #print(len(r_chain), len(l_chain))
        ri = 1
        while ri < len(r_chain) - 1 and turn(self.pts[r_chain[ri - 1]], self.pts[r_chain[ri]], self.pts[r_chain[ri + 1]]) > 0:
            ri += 1
        li = 1
        while li < len(l_chain) - 1 and turn(self.pts[l_chain[li - 1]], self.pts[l_chain[li]], self.pts[l_chain[li + 1]]) < 0:
            li += 1
        print(ri, li)
        while turn(self.pts[l_chain[li]], self.pts[r_chain[ri]], self.pts[r_chain[ri - 1]]) >= 0:
            li -= 1
        while turn(self.pts[l_chain[li - 1]], self.pts[l_chain[li]], self.pts[r_chain[ri]]) >= 0:
            ri -= 1
        print(ri, li)
        if ri < len(r_chain) - 1 or li < len(l_chain) - 1:
            farp = deque(r_chain[ri:] + l_chain[-1:li-1:-1])
            #print(len(farp))
            self.triangulate_polygon(farp)
            # self.DrawResult("step")
            #input("view next step:")
            if tt:
                ttt = self.find_triangle(r_chain[-1], l_chain[-1])
                ttt.neis[ttt.get_ind(r_chain[-1])] = tt
                tt.neis[j] = ttt
            #print('cutting done')
            while len(r_chain) - 1 > ri:
                ttt = self.find_triangle(r_chain[-2], r_chain[-1])
                ttt.neis[ttt.get_ind(r_chain[-2])] = r_neis[-1][0]
                if r_neis[-1][0]:
                    r_neis[-1][0].neis[r_neis[-1][1]] = ttt
                r_chain.pop()
                r_neis.pop()
            #print('rchain done')
            while len(l_chain) - 1 > li:
                ttt = self.find_triangle(l_chain[-1], l_chain[-2])
                ttt.neis[ttt.get_ind(l_chain[-1])] = l_neis[-1][0]
                if l_neis[-1][0]:
                    l_neis[-1][0].neis[l_neis[-1][1]] = ttt
                l_chain.pop()
                l_neis.pop()
            #print('lchain done')
            tt = self.find_triangle(l_chain[-1], r_chain[-1])
            j = tt.get_ind(l_chain[-1])
        flag = len(l_chain) == 2 and angle(self.pts[t.pts[i]], self.pts[l_chain[1]], self.pts[r_chain[-1]]) < 0
        flag = flag or (len(r_chain) == 2 and angle(self.pts[t.pts[i]], self.pts[r_chain[1]], self.pts[l_chain[-1]]) < 0)
        if flag:
            if not tt:
                cands = []
                pp = projection(self.pts[t.pts[i]], self.pts[l_chain[-1]], self.pts[r_chain[-1]])
                if self.is_on(l_chain[-1], r_chain[-1], pp) and self.is_in_circumcircle(t, pp):
                    cands.append(pp)
                if (l_neis[0][0] and self.is_obtuse(l_neis[0][0])) or len(l_chain) > 2:
                    lp = right_angle_point(self.pts[r_chain[1]], self.pts[t.pts[i]], self.pts[l_chain[-1]], self.pts[r_chain[-1]])
                    if lp and self.is_on(l_chain[-1], r_chain[-1], lp) and self.is_in_circumcircle(t, lp):
                        cands.append(lp)
                if (r_neis[0][0] and self.is_obtuse(r_neis[0][0])) or len(r_chain) > 2:
                    rp = right_angle_point(self.pts[l_chain[1]], self.pts[t.pts[i]], self.pts[l_chain[-1]], self.pts[r_chain[-1]])
                    if rp and self.is_on(l_chain[-1], r_chain[-1], rp) and self.is_in_circumcircle(t, rp):
                        cands.append(rp)
                if not cands or angle(self.pts[r_chain[-1]], self.pts[l_chain[-1]], self.pts[r_chain[-1]]) <= 0:
                    nt = Triangle(t.pts[i], r_chain[-1], l_chain[-1])
                    self.triangles.add(nt)
                    if len(l_chain) == 2:
                        nt.neis[2] = l_neis[-1][0]
                        if nt.neis[2]:
                            nt.neis[2].neis[l_neis[-1][1]] = nt
                        l_neis.pop()
                        l_chain.pop()
                        k = 0
                    else:
                        nt.neis[0] = r_neis[-1][0]
                        if nt.neis[0]:
                            nt.neis[0].neis[r_neis[-1][1]] = nt
                        r_neis.pop()
                        r_chain.pop()
                        k = 2
                    remaining = deque(r_chain + l_chain[-1:0:-1])
                    self.triangulate_polygon(remaining)
                    tttt = self.find_triangle(nt.pt(k + 1), nt.pts[k])
                    tttt.neis[tttt.get_ind(nt.pt(k + 1))] = nt
                    nt.neis[k] = tttt
                    #print("line 866")
                    #self.print_triangle(nt)
                    for i in range(len(r_chain) - 1):
                        tttt = self.find_triangle(r_chain[i], r_chain[i + 1])
                        l = tttt.get_ind(r_chain[i])
                        tttt.neis[l] = r_neis[i][0]
                        if r_neis[i][0]:
                            r_neis[i][0].neis[r_neis[i][1]] = tttt
                    for i in range(len(l_chain) - 1):
                        tttt = self.find_triangle(l_chain[i + 1], l_chain[i])
                        l = tttt.get_ind(l_chain[i + 1])
                        tttt.neis[l] = l_neis[i][0]
                        if l_neis[i][0]:
                            l_neis[i][0].neis[l_neis[i][1]] = tttt
                else:
                    stp = random.choice(cands)
                    self.insert_point_on(r_chain[-1], l_chain[-1], stp)
                    r_chain.append(len(self.pts) - 1)
                    remaining = deque(r_chain + l_chain[-1:0:-1])
                    self.triangulate_polygon(remaining)
                    for i in range(len(r_chain) - 2):
                        tttt = self.find_triangle(r_chain[i], r_chain[i + 1])
                        #self.print_triangle(tttt)
                        l = tttt.get_ind(r_chain[i])
                        tttt.neis[l] = r_neis[i][0]
                        if r_neis[i][0]:
                            r_neis[i][0].neis[r_neis[i][1]] = tttt
                    for i in range(len(l_chain) - 1):
                        tttt = self.find_triangle(l_chain[i + 1], l_chain[i])
                        l = tttt.get_ind(l_chain[i + 1])
                        tttt.neis[l] = l_neis[i][0]
                        if l_neis[i][0]:
                            l_neis[i][0].neis[l_neis[i][1]] = tttt
                return
            else:
                remaining = deque(r_chain + l_chain[-1:0:-1])
                self.triangulate_polygon(remaining)
                tttt = self.find_triangle(r_chain[-1], l_chain[-1])
                tttt.neis[tttt.get_ind(r_chain[-1])] = tt
                tt.neis[j] = tttt
                for i in range(len(r_chain) - 1):
                    tttt = self.find_triangle(r_chain[i], r_chain[i + 1])
                    l = tttt.get_ind(r_chain[i])
                    tttt.neis[l] = r_neis[i][0]
                    if r_neis[i][0]:
                        r_neis[i][0].neis[r_neis[i][1]] = tttt
                for i in range(len(l_chain) - 1):
                    tttt = self.find_triangle(l_chain[i + 1], l_chain[i])
                    l = tttt.get_ind(l_chain[i + 1])
                    tttt.neis[l] = l_neis[i][0]
                    if l_neis[i][0]:
                        l_neis[i][0].neis[l_neis[i][1]] = tttt
                if angle(self.pts[tt.pt(j + 1)], self.pts[tt.pts[j]], self.pts[tt.pt(j + 2)]) > 0 or angle(self.pts[tt.pts[j]], self.pts[tt.pt(j + 1)], self.pts[tt.pt(j + 2)]) > 0:
                    self.make_non_obtuse(tt)
                return
        cands = []
        r_neis.append((tt, j))
        neis = r_neis + l_neis[::-1]
        chain = r_chain + l_chain[:0:-1]
        for i in range(2, len(chain)):
            if not neis[i - 1][0]:
                pp = projection(self.pts[chain[0]], self.pts[chain[i - 1]], self.pts[chain[i]])
                if self.is_on(chain[i - 1], chain[i], pp) and self.is_in_circumcircle(t, pp):
                    cands.append((pp, i))
        if cands:
            stp, ind = random.choice(cands)
            self.insert_point_on(chain[ind - 1], chain[ind], stp)
            chain.insert(ind, len(self.pts) - 1)
            neis.insert(ind, (None, 0))
            remaining = deque(chain)
            self.triangulate_polygon(remaining)
            for i in range(len(chain)):
                tttt = self.find_triangle(chain[i - 1], chain[i])
                l = tttt.get_ind(chain[i - 1])
                tttt.neis[l] = neis[i - 1][0]
                if neis[i - 1][0]:
                    neis[i - 1][0].neis[neis[i - 1][1]] = tttt
        else:
            for i in range(len(chain)):
                for ii in range(i, len(chain)):
                    for pp in intersections_of_orthogonals(self.pts[chain[i - 1]], self.pts[chain[i]], self.pts[chain[ii - 1]], self.pts[chain[ii]]):
                        check = self.is_in_circumcircle(t, pp)
                        for iii in range(len(chain)):
                            if turn(self.pts[chain[iii - 1]], self.pts[chain[iii]], pp) <= 0 or sqdist(pp, self.pts[chain[iii]]) <= MINDIST:
                                check = False
                                break
                        if check:
                            cands.append(pp)
                    for pp in intersections_of_disks(midpoint(self.pts[chain[i - 1]], self.pts[chain[i]]), sqdist(self.pts[chain[i - 1]], self.pts[chain[i]]) / 4, midpoint(self.pts[chain[ii - 1]], self.pts[chain[ii]]), sqdist(self.pts[chain[ii - 1]], self.pts[chain[ii]]) / 4):
                        check = self.is_in_circumcircle(t, pp)
                        for iii in range(len(chain)):
                            if turn(self.pts[chain[iii - 1]], self.pts[chain[iii]], pp) <= 0 or sqdist(pp, self.pts[chain[iii]]) <= MINDIST:
                                check = False
                                break
                        if check:
                            cands.append(pp)
                    for pp in intersections_of_ortho_disk(self.pts[chain[i - 1]], self.pts[chain[i]], self.pts[chain[ii - 1]], self.pts[chain[ii]]):
                        check = self.is_in_circumcircle(t, pp)
                        for iii in range(len(chain)):
                            if turn(self.pts[chain[iii - 1]], self.pts[chain[iii]], pp) <= 0 or sqdist(pp, self.pts[chain[iii]]) <= MINDIST:
                                check = False
                                break
                        if check:
                            cands.append(pp)
            bcands = []
            bscore = 0
            for pp in cands:
                score = 0
                for i in range(len(chain)):
                    if angle(self.pts[chain[i]], self.pts[chain[i - 1]], pp) <= 0 and angle(self.pts[chain[i - 1]], self.pts[chain[i]], pp) <= 0 and angle(self.pts[chain[i]], pp, self.pts[chain[i - 1]]) <= 0:
                        score += 1
                if score < bscore:
                    continue
                if score > bscore:
                    bscore = score
                    bcands = []
                bcands.append(pp)
            stp = random.choice(bcands)
            self.pts.append(stp)
            t0 = Triangle(len(self.pts) - 1, chain[-1], chain[0])
            self.triangles.add(t0)
            t0.neis[1] = neis[-1][0]
            if neis[-1][0]:
                neis[-1][0].neis[neis[-1][1]] = t0
            pt = t0
            for i in range(1, len(chain)):
                nt = Triangle(len(self.pts) - 1, chain[i - 1], chain[i])
                self.triangles.add(nt)
                nt.neis[1] = neis[i - 1][0]
                if neis[i - 1][0]:
                    neis[i - 1][0].neis[neis[i - 1][1]] = nt
                nt.neis[0] = pt
                pt.neis[2] = nt
                pt = nt
            pt.neis[2] = t0
            t0.neis[0] = pt

    def make_non_obtuse2(self, t:Triangle):
        #print("resolve obtuse")
        #self.print_triangle(t)
        if (angle(self.pts[t.pts[2]], self.pts[t.pts[0]], self.pts[t.pts[1]]) > 0):
            i = 0
        if (angle(self.pts[t.pts[0]], self.pts[t.pts[1]], self.pts[t.pts[2]]) > 0):
            i = 1
        if (angle(self.pts[t.pts[1]], self.pts[t.pts[2]], self.pts[t.pts[0]]) > 0):
            i = 2
        #print("obtuse at", i)
        self.triangles.discard(t)
        q = self.pts[t.pts[i]]
        r = self.pts[t.pt(i + 1)]
        l = self.pts[t.pt(i + 2)]
        l_neis = []
        r_neis = []
        l_chain = []
        r_chain = []
        r_chain.append(t.pts[i])
        r_chain.append(t.pt(i + 1))
        l_chain.append(t.pts[i])
        l_chain.append(t.pt(i + 2))
        r_neis.append(t.neis[i])
        l_neis.append(t.nei(i + 2))
        tt = t.nei(i + 1)
        stop = [False]
        s = q
        j = i
        def cutright():
            if turn(self.pts[r_chain[-2]], self.pts[r_chain[-1]], s) <= 0 or angle(self.pts[r_chain[-2]], self.pts[r_chain[-1]], s) > 0:
                stop[0] = True
            else:
                nt = Triangle(tt.pts[j], r_chain[-2], r_chain[-1])
                self.triangles.add(nt)
                nt.neis[2] = r_neis[-1]
                r_neis.pop()
                nt.neis[1] = r_neis[-1]
                r_neis.pop()
                r_neis.append(nt)
                r_chain.pop()
                #print("line 697")
                #self.print_triangle(nt)
        def cutleft():
            if turn(self.pts[l_chain[-2]], self.pts[l_chain[-1]], s) >= 0 or angle(self.pts[l_chain[-2]], self.pts[l_chain[-1]], s) > 0:
                stop[0] = True
            else:
                nt = Triangle(l_chain[-1], l_chain[-2], tt.pts[j])
                self.triangles.add(nt)
                nt.neis[2] = l_neis[-1]
                l_neis.pop()
                nt.neis[0] = l_neis[-1]
                l_neis.pop()
                l_neis.append(nt)
                l_chain.pop()
                #print("line 715")
                #self.print_triangle(nt)
        while True:
            if not tt:
                break
            #self.print_triangle(tt)
            stop[0] = False
            j = (tt.get_ind(r_chain[-1]) + 1) % 3
            s = self.pts[tt.pts[j]]
            self.triangles.discard(tt)
            # self.DrawResult("step")
            l_neis.append(tt.neis[j])
            r_neis.append(tt.nei(j + 2))
            if turn(q, r, s) <= 0:
                while not stop[0]:
                    cutright()
                r_chain.append(tt.pts[j])
                tt = l_neis[-1]
                l_neis.pop()
            elif turn(q, l, s) >= 0:
                while not stop[0]:
                    cutleft()
                l_chain.append(tt.pts[j])
                tt = r_neis[-1]
                r_neis.pop()
            else:
                while (not stop[0]) and len(r_chain) > 2:
                    cutright()
                stop[0] = False
                while (not stop[0]) and len(l_chain) > 2:
                    cutleft()
                rsgn = turn(self.pts[r_chain[-2]], self.pts[r_chain[-1]], s) <= 0 or angle(self.pts[r_chain[-2]], self.pts[r_chain[-1]], s) > 0
                lsgn = turn(self.pts[l_chain[-2]], self.pts[l_chain[-1]], s) >= 0 or angle(self.pts[l_chain[-2]], self.pts[l_chain[-1]], s) > 0
                if not rsgn:
                    l = s
                    l_chain.append(tt.pts[j])
                    tt = r_neis[-1]
                    r_neis.pop()
                elif not lsgn:
                    r = s
                    r_chain.append(tt.pts[j])
                    tt = l_neis[-1]
                    l_neis.pop()
                else:
                    r_chain.append(tt.pts[j])
                    break
        #print(len(r_chain), len(l_chain))
        ri = 1
        while ri < len(r_chain) - 1 and turn(self.pts[r_chain[ri - 1]], self.pts[r_chain[ri]], self.pts[r_chain[ri + 1]]) > 0:
            ri += 1
        li = 1
        while li < len(l_chain) - 1 and turn(self.pts[l_chain[li - 1]], self.pts[l_chain[li]], self.pts[l_chain[li + 1]]) < 0:
            li += 1
        #print(ri, li)
        while turn(self.pts[l_chain[li]], self.pts[r_chain[ri]], self.pts[r_chain[ri - 1]]) >= 0:
            li -= 1
        while turn(self.pts[l_chain[li - 1]], self.pts[l_chain[li]], self.pts[r_chain[ri]]) >= 0:
            ri -= 1
        #print(ri, li)
        
        if ri < len(r_chain) - 1 or li < len(l_chain) - 1:
            r_chain = r_chain[:ri + 1]
            l_chain = l_chain[:li + 1]
            r_neis = r_neis[:ri]
            l_neis = l_neis[:li]
            tt = t
        flag = len(l_chain) == 2 and angle(self.pts[t.pts[i]], self.pts[l_chain[1]], self.pts[r_chain[-1]]) < 0
        flag = flag or (len(r_chain) == 2 and angle(self.pts[t.pts[i]], self.pts[r_chain[1]], self.pts[l_chain[-1]]) < 0)
        if flag:
            if not tt:
                cands = []
                pp = projection(self.pts[t.pts[i]], self.pts[l_chain[-1]], self.pts[r_chain[-1]])
                if self.is_on(l_chain[-1], r_chain[-1], pp) and self.is_in_circumcircle(t, pp):
                    cands.append(pp)
                if (l_neis[0] and self.is_obtuse(l_neis[0])) or len(l_chain) > 2:
                    lp = right_angle_point(self.pts[r_chain[1]], self.pts[t.pts[i]], self.pts[l_chain[-1]], self.pts[r_chain[-1]])
                    if lp and self.is_on(l_chain[-1], r_chain[-1], lp) and self.is_in_circumcircle(t, lp):
                        cands.append(lp)
                if (r_neis[0] and self.is_obtuse(r_neis[0])) or len(r_chain) > 2:
                    rp = right_angle_point(self.pts[l_chain[1]], self.pts[t.pts[i]], self.pts[l_chain[-1]], self.pts[r_chain[-1]])
                    if rp and self.is_on(l_chain[-1], r_chain[-1], rp) and self.is_in_circumcircle(t, rp):
                        cands.append(rp)
                stp = random.choice(cands)
                self.add_steiner(stp)
                return
            elif tt != t and self.is_obtuse(tt):
                for t in self.triangles:
                    del t
                self.triangles = set()
                self.triangulate()
                self.delaunay_triangulate()
                return
        cands = []
        r_neis.append(tt)
        neis = r_neis + l_neis[::-1]
        chain = r_chain + l_chain[:0:-1]
        for i in range(2, len(chain)):
            if not neis[i - 1] and angle(self.pts[chain[i - 1]], self.pts[chain[0]], self.pts[chain[i]]) > 0:
                pp = projection(self.pts[chain[0]], self.pts[chain[i - 1]], self.pts[chain[i]])
                if self.is_on(chain[i - 1], chain[i], pp) and self.is_in_circumcircle(t, pp):
                    cands.append(pp)
        if cands:
            stp = random.choice(cands)
            self.add_steiner(stp)
        else:
            for i in range(len(chain)):
                for ii in range(i, len(chain)):
                    for pp in intersections_of_orthogonals(self.pts[chain[i - 1]], self.pts[chain[i]], self.pts[chain[ii - 1]], self.pts[chain[ii]]):
                        check = self.is_in_circumcircle(t, pp)
                        for iii in range(len(chain)):
                            if turn(self.pts[chain[iii - 1]], self.pts[chain[iii]], pp) <= 0 or sqdist(pp, self.pts[chain[iii]]) <= MINDIST:
                                check = False
                                break
                        if check:
                            cands.append(pp)
                    for pp in intersections_of_disks(midpoint(self.pts[chain[i - 1]], self.pts[chain[i]]), sqdist(self.pts[chain[i - 1]], self.pts[chain[i]]) / 4, midpoint(self.pts[chain[ii - 1]], self.pts[chain[ii]]), sqdist(self.pts[chain[ii - 1]], self.pts[chain[ii]]) / 4):
                        check = self.is_in_circumcircle(t, pp)
                        for iii in range(len(chain)):
                            if turn(self.pts[chain[iii - 1]], self.pts[chain[iii]], pp) <= 0 or sqdist(pp, self.pts[chain[iii]]) <= MINDIST:
                                check = False
                                break
                        if check:
                            cands.append(pp)
                    for pp in intersections_of_ortho_disk(self.pts[chain[i - 1]], self.pts[chain[i]], self.pts[chain[ii - 1]], self.pts[chain[ii]]):
                        check = self.is_in_circumcircle(t, pp)
                        for iii in range(len(chain)):
                            if turn(self.pts[chain[iii - 1]], self.pts[chain[iii]], pp) <= 0 or sqdist(pp, self.pts[chain[iii]]) <= MINDIST:
                                check = False
                                break
                        if check:
                            cands.append(pp)
            bcands = []
            conedges = []
            for i in range(len(chain)):
                if not neis[i - 1] and ((chain[i], chain[i - 1]) in self.constraints or (chain[i - 1], chain[i]) in self.constraints):
                    conedges.append(i)
            bscore = (0, 0)
            for pp in cands:
                score = 0
                cscore = 0
                for i in conedges:
                    if angle(self.pts[chain[i]], pp, self.pts[chain[i - 1]]) <= 0:
                        cscore += 1
                for i in range(len(chain)):
                    if angle(self.pts[chain[i]], self.pts[chain[i - 1]], pp) <= 0 and angle(self.pts[chain[i - 1]], self.pts[chain[i]], pp) <= 0 and angle(self.pts[chain[i]], pp, self.pts[chain[i - 1]]) <= 0:
                        score += 1
                if (cscore, score) < bscore:
                    continue
                if (cscore, score) > bscore:
                    bscore = (cscore, score)
                    bcands = []
                bcands.append(pp)
            if bcands:
                stp = random.choice(bcands)
                self.add_steiner(stp)
            else:
                for t in self.triangles:
                    del t
                self.triangles = set()
                self.triangulate()
                self.delaunay_triangulate()

    def make_non_obtuse3(self, t:Triangle, on_constraint = set()):
        #print("resolve obtuse")
        #self.print_triangle(t)
        if angle(self.pts[t.pts[2]], self.pts[t.pts[0]], self.pts[t.pts[1]]) > 0:
            i = 0
        if angle(self.pts[t.pts[0]], self.pts[t.pts[1]], self.pts[t.pts[2]]) > 0:
            i = 1
        if angle(self.pts[t.pts[1]], self.pts[t.pts[2]], self.pts[t.pts[0]]) > 0:
            i = 2
        #print("obtuse at", i)
        if t.neis[i]:
            tt = t.neis[i]
            j = (tt.get_ind(t.pts[i]) + 1) % 3
            if angle(self.pts[tt.pt(j + 1)], self.pts[tt.pts[j]], self.pts[tt.pt(j + 2)]) > 0:
                return self.make_non_obtuse3(tt, on_constraint)
        if t.nei(i + 2):
            tt = t.nei(i + 2)
            j = (tt.get_ind(t.pt(i + 2)) + 1) % 3
            if angle(self.pts[tt.pt(j + 1)], self.pts[tt.pts[j]], self.pts[tt.pt(j + 2)]) > 0:
                return self.make_non_obtuse3(tt, on_constraint)
        self.triangles.discard(t)
        q = self.pts[t.pts[i]]
        r = self.pts[t.pt(i + 1)]
        l = self.pts[t.pt(i + 2)]
        l_neis = []
        r_neis = []
        l_chain = []
        r_chain = []
        r_chain.append(t.pts[i])
        r_chain.append(t.pt(i + 1))
        l_chain.append(t.pts[i])
        l_chain.append(t.pt(i + 2))
        r_neis.append(t.neis[i])
        l_neis.append(t.nei(i + 2))
        tt = t.nei(i + 1)
        stop = [False]
        s = q
        j = i

        def cutright():
            if turn(self.pts[r_chain[-2]], self.pts[r_chain[-1]], s) <= 0 or angle(self.pts[r_chain[-2]], self.pts[r_chain[-1]], s) > 0:
                stop[0] = True
            else:
                nt = Triangle(tt.pts[j], r_chain[-2], r_chain[-1])
                self.triangles.add(nt)
                nt.neis[2] = r_neis[-1]
                r_neis.pop()
                nt.neis[1] = r_neis[-1]
                r_neis.pop()
                r_neis.append(nt)
                r_chain.pop()
                #print("line 697")
                #self.print_triangle(nt)
        def cutleft():
            if turn(self.pts[l_chain[-2]], self.pts[l_chain[-1]], s) >= 0 or angle(self.pts[l_chain[-2]], self.pts[l_chain[-1]], s) > 0:
                stop[0] = True
            else:
                nt = Triangle(l_chain[-1], l_chain[-2], tt.pts[j])
                self.triangles.add(nt)
                nt.neis[2] = l_neis[-1]
                l_neis.pop()
                nt.neis[0] = l_neis[-1]
                l_neis.pop()
                l_neis.append(nt)
                l_chain.pop()
                #print("line 715")
                #self.print_triangle(nt)

        while True:
            if not tt:
                break
            #self.print_triangle(tt)
            stop[0] = False
            j = (tt.get_ind(r_chain[-1]) + 1) % 3
            s = self.pts[tt.pts[j]]
            self.triangles.discard(tt)
            # self.DrawResult("step")
            l_neis.append(tt.neis[j])
            r_neis.append(tt.nei(j + 2))
            if turn(q, r, s) <= 0:
                while not stop[0]:
                    cutright()
                r_chain.append(tt.pts[j])
                tt = l_neis[-1]
                l_neis.pop()
            elif turn(q, l, s) >= 0:
                while not stop[0]:
                    cutleft()
                l_chain.append(tt.pts[j])
                tt = r_neis[-1]
                r_neis.pop()
            else:
                while (not stop[0]) and len(r_chain) > 2:
                    cutright()
                stop[0] = False
                while (not stop[0]) and len(l_chain) > 2:
                    cutleft()
                rsgn = turn(self.pts[r_chain[-2]], self.pts[r_chain[-1]], s) <= 0 or angle(self.pts[r_chain[-2]], self.pts[r_chain[-1]], s) > 0
                lsgn = turn(self.pts[l_chain[-2]], self.pts[l_chain[-1]], s) >= 0 or angle(self.pts[l_chain[-2]], self.pts[l_chain[-1]], s) > 0
                if not rsgn:
                    l = s
                    l_chain.append(tt.pts[j])
                    tt = r_neis[-1]
                    r_neis.pop()
                elif not lsgn:
                    r = s
                    r_chain.append(tt.pts[j])
                    tt = l_neis[-1]
                    l_neis.pop()
                else:
                    r_chain.append(tt.pts[j])
                    break
        #print(len(r_chain), len(l_chain))
        ri = 1
        while ri < len(r_chain) - 1 and turn(self.pts[r_chain[ri - 1]], self.pts[r_chain[ri]], self.pts[r_chain[ri + 1]]) > 0:
            ri += 1
        li = 1
        while li < len(l_chain) - 1 and turn(self.pts[l_chain[li - 1]], self.pts[l_chain[li]], self.pts[l_chain[li + 1]]) < 0:
            li += 1
        #print(ri, li)
        while turn(self.pts[l_chain[li]], self.pts[r_chain[ri]], self.pts[r_chain[ri - 1]]) >= 0:
            li -= 1
        while turn(self.pts[l_chain[li - 1]], self.pts[l_chain[li]], self.pts[r_chain[ri]]) >= 0:
            ri -= 1
        #print(ri, li)
        
        if ri < len(r_chain) - 1 or li < len(l_chain) - 1:
            r_chain = r_chain[:ri + 1]
            l_chain = l_chain[:li + 1]
            r_neis = r_neis[:ri]
            l_neis = l_neis[:li]
            tt = t
        flag = len(l_chain) == 2 and angle(self.pts[t.pts[i]], self.pts[l_chain[1]], self.pts[r_chain[-1]]) < 0
        flag = flag or (len(r_chain) == 2 and angle(self.pts[t.pts[i]], self.pts[r_chain[1]], self.pts[l_chain[-1]]) < 0)
        if flag:
            if not tt:
                cands = []
                pp = projection(self.pts[t.pts[i]], self.pts[l_chain[-1]], self.pts[r_chain[-1]])
                if self.is_on(l_chain[-1], r_chain[-1], pp) and self.is_in_circumcircle(t, pp):
                    cands.append(pp)
                if (l_neis[0] and self.is_obtuse(l_neis[0])) or len(l_chain) > 2:
                    lp = right_angle_point(self.pts[r_chain[1]], self.pts[t.pts[i]], self.pts[l_chain[-1]], self.pts[r_chain[-1]])
                    if lp and self.is_on(l_chain[-1], r_chain[-1], lp) and self.is_in_circumcircle(t, lp):
                        cands.append(lp)
                if (r_neis[0] and self.is_obtuse(r_neis[0])) or len(r_chain) > 2:
                    rp = right_angle_point(self.pts[l_chain[1]], self.pts[t.pts[i]], self.pts[l_chain[-1]], self.pts[r_chain[-1]])
                    if rp and self.is_on(l_chain[-1], r_chain[-1], rp) and self.is_in_circumcircle(t, rp):
                        cands.append(rp)
                stp = random.choice(cands)
                self.add_steiner(stp, on_constraint)
                return
            elif tt != t and self.is_obtuse(tt):
                for t in self.triangles:
                    del t
                self.triangles = set()
                self.triangulate()
                self.delaunay_triangulate()
                return
        cands = []
        r_neis.append(tt)
        neis = r_neis + l_neis[::-1]
        chain = r_chain + l_chain[:0:-1]
        for i in range(2, len(chain)):
            if not neis[i - 1] and angle(self.pts[chain[i - 1]], self.pts[chain[0]], self.pts[chain[i]]) > 0:
                pp = projection(self.pts[chain[0]], self.pts[chain[i - 1]], self.pts[chain[i]])
                if self.is_on(chain[i - 1], chain[i], pp) and self.is_in_circumcircle(t, pp):
                    cands.append(pp)
        if cands:
            stp = random.choice(cands)
            self.add_steiner(stp, on_constraint)
        else:
            for i in range(len(chain)):
                for ii in range(i, len(chain)):
                    for pp in intersections_of_orthogonals(self.pts[chain[i - 1]], self.pts[chain[i]], self.pts[chain[ii - 1]], self.pts[chain[ii]]):
                        check = self.is_in_circumcircle(t, pp)
                        for iii in range(len(chain)):
                            if turn(self.pts[chain[iii - 1]], self.pts[chain[iii]], pp) <= 0 or sqdist(pp, self.pts[chain[iii]]) <= MINDIST:
                                check = False
                                break
                        if check:
                            cands.append(pp)
                    for pp in intersections_of_disks(midpoint(self.pts[chain[i - 1]], self.pts[chain[i]]), sqdist(self.pts[chain[i - 1]], self.pts[chain[i]]) / 4, midpoint(self.pts[chain[ii - 1]], self.pts[chain[ii]]), sqdist(self.pts[chain[ii - 1]], self.pts[chain[ii]]) / 4):
                        check = self.is_in_circumcircle(t, pp)
                        for iii in range(len(chain)):
                            if turn(self.pts[chain[iii - 1]], self.pts[chain[iii]], pp) <= 0 or sqdist(pp, self.pts[chain[iii]]) <= MINDIST:
                                check = False
                                break
                        if check:
                            cands.append(pp)
                    for pp in intersections_of_ortho_disk(self.pts[chain[i - 1]], self.pts[chain[i]], self.pts[chain[ii - 1]], self.pts[chain[ii]]):
                        check = self.is_in_circumcircle(t, pp)
                        for iii in range(len(chain)):
                            if turn(self.pts[chain[iii - 1]], self.pts[chain[iii]], pp) <= 0 or sqdist(pp, self.pts[chain[iii]]) <= MINDIST:
                                check = False
                                break
                        if check:
                            cands.append(pp)
            bcands = []
            conedges = []
            for i in range(len(chain)):
                if not neis[i - 1] and ((chain[i], chain[i - 1]) in self.constraints or (chain[i - 1], chain[i]) in self.constraints):
                    conedges.append(i)
            bscore = (0, 0)
            for pp in cands:
                score = 0
                cscore = 0
                for i in conedges:
                    if angle(self.pts[chain[i]], pp, self.pts[chain[i - 1]]) <= 0:
                        cscore += 1
                for i in range(len(chain)):
                    if angle(self.pts[chain[i]], self.pts[chain[i - 1]], pp) <= 0 and angle(self.pts[chain[i - 1]], self.pts[chain[i]], pp) <= 0 and angle(self.pts[chain[i]], pp, self.pts[chain[i - 1]]) <= 0:
                        score += 1
                if (cscore, score) < bscore:
                    continue
                if (cscore, score) > bscore:
                    bscore = (cscore, score)
                    bcands = []
                bcands.append(pp)
            if bcands:
                stp = random.choice(bcands)
                self.add_steiner(stp, on_constraint)
            else:
                for t in self.triangles:
                    del t
                self.triangles = set()
                self.triangulate()
                self.delaunay_triangulate()

    def make_non_obtuse_boundary(self):
        inserting = []

        # t: triangle
        # j : index
        # triangle의 pt는 시계 방향?
        def gen_cands(t, j):
            p = self.pts[t.pts[j]]
            lp = self.pts[t.pt(j + 1)]
            rp = self.pts[t.pt(j + 2)]

            cands = [projection(p, lp, rp)] # projection 구하고.

            rs = False
            if t.nei(j + 2):
                tt = t.nei(j + 2)
                k = (tt.get_ind(t.pt(j + 2)) + 1) % 3
                rs = angle(self.pts[tt.pt(k + 2)], self.pts[tt.pts[k]], self.pts[tt.pt(k + 1)]) > 0
            ls = False
            if t.neis[j]:
                tt = t.neis[j]
                k = (tt.get_ind(t.pts[j]) + 1) % 3
                ls = angle(self.pts[tt.pt(k + 2)], self.pts[tt.pts[k]], self.pts[tt.pt(k + 1)]) > 0
            if ls or rs:
                div = 2
                while ls or rs:
                    low = 1
                    high = div - 1
                    while low <= high:
                        mid = (low + high) // 2
                        pp = Point(lq.x * mid / div + rq.x * (div - mid) / div, lq.y * mid / div + rq.y * (div - mid) / div)
                        if turn(rp, p, pp) <= 0 or angle(lp, p, pp) > 0:
                            low = mid + 1
                        elif turn(lp, p, pp) >= 0 or angle(rp, p, pp) > 0:
                            high = mid - 1
                        else:
                            break
                    if low <= high:
                        if ls:
                            ln = mid + 1
                            pp = Point(lq.x * ln / div + rq.x * (div - ln) / div, lq.y * ln / div + rq.y * (div - ln) / div)
                            while turn(lp, p, pp) < 0 and angle(rp, p, pp) <= 0:
                                ln += 1
                                pp = Point(lq.x * ln / div + rq.x * (div - ln) / div, lq.y * ln / div + rq.y * (div - ln) / div)
                            ln -= 1
                            pp = Point(lq.x * ln / div + rq.x * (div - ln) / div, lq.y * ln / div + rq.y * (div - ln) / div)
                            if angle(p, pp, lp) >= 0:
                                cands.append(pp)
                                ls = False
                        if rs:
                            rn = mid - 1
                            pp = Point(lq.x * rn / div + rq.x * (div - rn) / div, lq.y * rn / div + rq.y * (div - rn) / div)
                            while turn(rp, p, pp) < 0 and angle(lp, p, pp) <= 0:
                                rn -= 1
                                pp = Point(lq.x * rn / div + rq.x * (div - rn) / div, lq.y * rn / div + rq.y * (div - rn) / div)
                            rn += 1
                            pp = Point(lq.x * rn / div + rq.x * (div - rn) / div, lq.y * rn / div + rq.y * (div - rn) / div)
                            if angle(p, pp, rp) >= 0:
                                cands.append(pp)
                                rs = False
                    div += 1
                    if div > 10000:
                        break
            return cands

        for i in range(len(self.region_boundary)):
            t = self.find_triangle(self.region_boundary[i - 1], self.region_boundary[i])
            j = (t.get_ind(self.region_boundary[i]) + 1) % 3
            if angle(self.pts[t.pt(j + 2)], self.pts[t.pts[j]], self.pts[t.pt(j + 1)]) > 0:
                lind = i - 1
                lq = self.pts[self.region_boundary[i - 1]]
                while lq.x.den != 1 or lq.y.den != 1:
                    lind -= 1
                    lind %= len(self.region_boundary)
                    lq = self.pts[self.region_boundary[lind]]
                rind = i
                rq = self.pts[self.region_boundary[i]]
                while rq.x.den != 1 or rq.y.den != 1:
                    rind += 1
                    rind %= len(self.region_boundary)
                    rq = self.pts[self.region_boundary[rind]]
                inserting.append(random.choice(gen_cands(t, j)))

        # print("boundary done!")
        for con in self.constraints:
            e1, e2 = con
            t1 = self.find_triangle(e1, e2)
            i1 = (t1.get_ind(e2) + 1) % 3
            t2 = self.find_triangle(e2, e1)
            i2 = (t2.get_ind(e1) + 1) % 3
            b1 = angle(self.pts[t1.pt(i1 + 1)], self.pts[t1.pts[i1]], self.pts[t1.pt(i1 + 2)]) > 0
            b2 = angle(self.pts[t2.pt(i2 + 1)], self.pts[t2.pts[i2]], self.pts[t2.pt(i2 + 2)]) > 0
            if b2 and not b1:
                e1, e2, t1, t2, i1, i2, b1, b2 = e2, e1, t2, t1, i2, i1, b2, b1
            li, ri = self.const_dict[con]
            if turn(self.pts[li], self.pts[t1.pts[i1]], self.pts[ri]) > 0:
                li, ri = ri, li
            lq = self.pts[li]
            rq = self.pts[ri]
            lp = self.pts[t1.pt(i1 + 1)]
            rp = self.pts[t1.pt(i1 + 2)]
            if b1 and not b2:
                cands = gen_cands(t1, i1)
                bcands = []
                bscore = 0
                for cand in cands:
                    score = 0
                    if angle(self.pts[t2.pts[i2]], cand, rp) <= 0:
                        score += 1
                    elif t2.neis[i2]:
                        tt = t2.neis[i2]
                        k = (tt.get_ind(t2.pts[i2]) + 1) % 3
                        if angle(self.pts[tt.pt(k + 1)], self.pts[tt.pts[k]], self.pts[tt.pt(k + 2)]) > 0:
                            score += 1
                    if angle(self.pts[t2.pts[i2]], cand, lp) <= 0:
                        score += 1
                    elif t2.nei(i2 + 2):
                        tt = t2.nei(i2 + 2)
                        k = (tt.get_ind(t2.pt(i2 + 2)) + 1) % 3
                        if angle(self.pts[tt.pt(k + 1)], self.pts[tt.pts[k]], self.pts[tt.pt(k + 2)]) > 0:
                            score += 1
                    if score < bscore:
                        continue
                    if score > bscore:
                        bscore = score
                    bcands.append(cand)
                inserting.append(random.choice(bcands))
                
            if b1 and b2:
                cands = gen_cands(t1, i1)
                rq, lq = lq, rq
                cands = cands + gen_cands(t2, i2)
                bcands = []
                bscore = (0, 0)
                for cand in cands:
                    ascore = 0
                    if angle(rp, self.pts[t1.pts[i1]], cand) <= 0:
                        ascore += 1
                    if angle(lp, self.pts[t1.pts[i1]], cand) <= 0:
                        ascore += 1
                    if angle(rp, self.pts[t2.pts[i2]], cand) <= 0:
                        ascore += 1
                    if angle(lp, self.pts[t2.pts[i2]], cand) <= 0:
                        ascore += 1
                    score = 0
                    if angle(self.pts[t1.pts[i1]], cand, rp) <= 0:
                        score += 1
                    elif t1.nei(i1 + 2):
                        tt = t1.nei(i1 + 2)
                        k = (tt.get_ind(t1.pt(i1 + 2)) + 1) % 3
                        if angle(self.pts[tt.pt(k + 1)], self.pts[tt.pts[k]], self.pts[tt.pt(k + 2)]) > 0:
                            score += 1
                    if angle(self.pts[t1.pts[i1]], cand, lp) <= 0:
                        score += 1
                    elif t1.neis[i1]:
                        tt = t1.neis[i1]
                        k = (tt.get_ind(t1.pts[i1]) + 1) % 3
                        if angle(self.pts[tt.pt(k + 1)], self.pts[tt.pts[k]], self.pts[tt.pt(k + 2)]) > 0:
                            score += 1
                    if angle(self.pts[t2.pts[i2]], cand, rp) <= 0:
                        score += 1
                    elif t2.neis[i2]:
                        tt = t2.neis[i2]
                        k = (tt.get_ind(t2.pts[i2]) + 1) % 3
                        if angle(self.pts[tt.pt(k + 1)], self.pts[tt.pts[k]], self.pts[tt.pt(k + 2)]) > 0:
                            score += 1
                    if angle(self.pts[t2.pts[i2]], cand, lp) <= 0:
                        score += 1
                    elif t2.nei(i2 + 2):
                        tt = t2.nei(i2 + 2)
                        k = (tt.get_ind(t2.pt(i2 + 2)) + 1) % 3
                        if angle(self.pts[tt.pt(k + 1)], self.pts[tt.pts[k]], self.pts[tt.pt(k + 2)]) > 0:
                            score += 1
                    if (ascore, score) < bscore:
                        continue
                    if (ascore, score) > bscore:
                        bscore = (ascore, score)
                    bcands.append(cand)
                inserting.append(random.choice(bcands))
        # print("constraints done!")
        self.add_steiners(list(inserting))
        # print("inserting done!")

    def make_non_obtuse_ortho(self):
        while True:
            done = True
            for t in self.triangles:
                if self.is_obtuse(t):
                    p0 = self.pts[t.pts[0]]
                    p1 = self.pts[t.pts[1]]
                    p2 = self.pts[t.pts[2]]
                    if angle(p2, p0, p1) > 0:
                        q, r = p0, p1
                        i = 0
                    elif angle(p0, p1, p2) > 0:
                        q, r = p1, p2
                        i = 1
                    else:
                        q, r = p2, p0
                        i = 2
                    if q.x <= r.x and q.y > r.y:
                        self.insert_grid_point(q, t, 0)
                    elif q.x < r.x and q.y <= r.y:
                        self.insert_grid_point(q, t, 1)
                    elif q.x >= r.x and q.y < r.y:
                        self.insert_grid_point(q, t, 2)
                    else:
                        self.insert_grid_point(q, t, 3)
                    done = False
                    break
            if done:
                break

    def make_non_obtuse_ortho2(self):
        while True:
            while True:
                npts = []
                for i in range(len(self.region_boundary)):
                    t = self.find_triangle(self.region_boundary[i - 1], self.region_boundary[i])
                    j = (t.get_ind(self.region_boundary[i]) + 1) % 3
                    p0 = self.pts[t.pts[j]]
                    p1 = self.pts[t.pt(j + 1)]
                    p2 = self.pts[t.pt(j + 2)]
                    if angle(p2, p0, p1) > 0:
                        npts.append(projection(self.pts[t.pts[j]], self.pts[t.pt(j + 1)], self.pts[t.pt(j + 2)]))
                    else:
                        if p1.x == p2.x or p1.y == p2.y:
                            continue
                        elif (p1.x < p2.x) == (p1.y < p2.y):
                            q = Point(p1.x, p2.y)
                            if p1.x < p2.x:
                                d = 1
                            else:
                                d = 3
                        else:
                            q = Point(p2.x, p1.y)
                            if p1.x < p2.x:
                                d = 0
                            else:
                                d = 2
                if npts:
                    self.add_steiners(npts)
                else:
                    break
            done = True
            for t in self.triangles:
                if self.is_obtuse(t):
                    p0 = self.pts[t.pts[0]]
                    p1 = self.pts[t.pts[1]]
                    p2 = self.pts[t.pts[2]]
                    if angle(p2, p0, p1) > 0:
                        q, r = p0, p1
                        i = 0
                    elif angle(p0, p1, p2) > 0:
                        q, r = p1, p2
                        i = 1
                    else:
                        q, r = p2, p0
                        i = 2
                    if q.x <= r.x and q.y > r.y:
                        self.insert_grid_point(q, t, 0)
                    elif q.x < r.x and q.y <= r.y:
                        self.insert_grid_point(q, t, 1)
                    elif q.x >= r.x and q.y < r.y:
                        self.insert_grid_point(q, t, 2)
                    else:
                        self.insert_grid_point(q, t, 3)
                    done = False
                    break
            self.DrawResult("step")
            print(self.score())
            #input()
            if done:
                break
    
    def insert_grid_point(self, p:Point, t:Triangle, d:int):
        p0, p1, p2 = [self.pts[t.pts[i]] for i in range(3)]
        # print(p, p0, p1, p2, d)
        # input()
        midx = p0.x + p1.x + p2.x - min(p0.x, p1.x, p2.x) - max(p0.x, p1.x, p2.x)
        midy = p0.y + p1.y + p2.y - min(p0.y, p1.y, p2.y) - max(p0.y, p1.y, p2.y)
        if d == 0:
            q = Point(midx, p.y)
            if self.is_in(t, q) and q != p0 and q != p1 and q != p2:
                self.add_steiner(q)
            elif p0.y < p.y and p1.y > p.y:
                return self.insert_grid_point(p, t.neis[0], 0)
            elif p1.y < p.y and p2.y > p.y:
                return self.insert_grid_point(p, t.neis[1], 0)
            else:
                return self.insert_grid_point(p, t.neis[2], 0)
        elif d == 1:
            q = Point(p.x, midy)
            if self.is_in(t, q) and q != p0 and q != p1 and q != p2:
                self.add_steiner(q)
            elif p0.x > p.x and p1.x < p.x:
                return self.insert_grid_point(p, t.neis[0], 1)
            elif p1.x > p.x and p2.x < p.x:
                return self.insert_grid_point(p, t.neis[1], 1)
            else:
                return self.insert_grid_point(p, t.neis[2], 1)
        elif d == 2:
            q = Point(midx, p.y)
            if self.is_in(t, q) and q != p0 and q != p1 and q != p2:
                self.add_steiner(q)
            elif p0.y > p.y and p1.y < p.y:
                return self.insert_grid_point(p, t.neis[0], 2)
            elif p1.y > p.y and p2.y < p.y:
                return self.insert_grid_point(p, t.neis[1], 2)
            else:
                return self.insert_grid_point(p, t.neis[2], 2)
        else:
            q = Point(p.x, midy)
            if self.is_in(t, q) and q != p0 and q != p1 and q != p2:
                self.add_steiner(q)
            elif p0.x < p.x and p1.x > p.x:
                return self.insert_grid_point(p, t.neis[0], 3)
            elif p1.x < p.x and p2.x > p.x:
                return self.insert_grid_point(p, t.neis[1], 3)
            else:
                return self.insert_grid_point(p, t.neis[2], 3)
        # print(q)

    def insert_point_on(self, e1:int, e2:int, p:Point):
        if not self.is_on(e1, e2, p):
            raise Exception("point is not on the edge")
        self.pts.append(p)
        ind = len(self.pts) - 1
        #print(e1, e2, ind)
        inserted = False
        for i in range(len(self.region_boundary)):
            if (self.region_boundary[i - 1] == e1 and self.region_boundary[i] == e2) or (self.region_boundary[i] == e1 and self.region_boundary[i - 1] == e2):
                inserted = True
                break
        if inserted:
            self.region_boundary.insert(i, ind)
            #print(self.region_boundary)
        else:
            #print(self.region_boundary)
            #print(e1, e2)
            for cons in self.constraints:
                if cons == (e1, e2) or cons == (e2, e1):
                    break
            self.constraints.add((e1, ind))
            self.constraints.add((e2, ind))
            self.constraints.remove(cons)
        t1 = self.find_triangle(e1, e2)
        if t1:
            i = t1.get_ind(e1)
            nt = Triangle(ind, t1.pt(i + 1), t1.pt(i + 2))
            ti1 = t1.nei(i + 1)
            nt.neis[1] = ti1
            if ti1:
                ti1.neis[ti1.get_ind(t1.pt(i + 2))] = nt
            nt.neis[2] = t1
            t1.neis[(i + 1) % 3] = nt
            t1.pts[(i + 1) % 3] = ind
            self.triangles.add(nt)
        t2 = self.find_triangle(e2, e1)
        if t2:
            i = t2.get_ind(e2)
            nt = Triangle(ind, t2.pt(i + 1), t2.pt(i + 2))
            ti2 = t2.nei(i + 1)
            nt.neis[1] = ti2
            if ti2:
                ti2.neis[ti2.get_ind(t2.pt(i + 2))] = nt
            nt.neis[2] = t2
            t2.neis[(i + 1) % 3] = nt
            t2.pts[(i + 1) % 3] = ind
            self.triangles.add(nt)

    def step(self, on_constraint = True):
        #self.make_non_obtuse_boundary()
        obtt = []
        for t in self.triangles:
            if self.is_obtuse(t):
                obtt.append(t)
        if not obtt:
            # print("Done!")
            self.done = True
        else:
            self.done - False
            target = random.choice(obtt)
            # self.print_triangle(target)
            self.make_non_obtuse3(target, self.ban)
            self.delaunay_triangulate()
            obtt = []
            for t in self.triangles:
                if self.is_obtuse(t):
                    obtt.append(t)
            if not obtt:
                # print("Done!")
                self.done = True

    def step_proj(self):
        obtt = []
        for t in self.triangles:
            if self.is_obtuse(t):
                obtt.append(t)
        if not obtt:
            print("Done!")
        else:
            target = random.choice(obtt)
            if (angle(self.pts[target.pts[0]], self.pts[target.pts[1]], self.pts[target.pts[2]]) > 0):
                i = 1
            elif (angle(self.pts[target.pts[1]], self.pts[target.pts[2]], self.pts[target.pts[0]]) > 0):
                i = 2
            else:
                i = 0
            pp = projection(self.pts[target.pts[i]], self.pts[target.pt(i + 1)], self.pts[target.pt(i + 2)])
            self.add_steiner(pp)

    def resolve_dense_pts(self):
        mdist = sqdist(self.pts[self.fp_ind], self.pts[self.fp_ind + 1])
        mp1, mp2 = self.fp_ind, self.fp_ind + 1
        for i in range(len(self.pts)):
            for j in range(max(self.fp_ind, i + 1), len(self.pts)):
                d = sqdist(self.pts[i], self.pts[j])
                if d < mdist:
                    mdist = d
                    mp1, mp2 = i, j
        if mp1 >= self.fp_ind:
            din = mp1
        else:
            din = mp2
        rind = -1
        for i in range(len(self.region_boundary)):
            if self.region_boundary[i] == din:
                rind = i
            if self.region_boundary[i] > din:
                self.region_boundary[i] -= 1
        if rind != -1:
            self.region_boundary.pop(rind)
        dcons = set()
        ncons = set()
        e1, e2 = -1, -1
        for con in self.constraints:
            c1, c2 = con
            if c1 == din or c2 == din:
                if e1 == -1:
                    e1 = c1 + c2 - din
                    if e1 > din:
                        e1 -= 1
                else:
                    e2 = c1 + c2 - din
                    if e2 > din:
                        e2 -= 1
                dcons.add(con)
            elif c1 > din and c2 > din:
                dcons.add(con)
                ncons.add((c1 - 1, c2 - 1))
            elif c1 > din:
                dcons.add(con)
                ncons.add((c1 - 1, c2))
            elif c2 > din:
                dcons.add(con)
                ncons.add((c1, c2 - 1))
        if e1 == -1:
            ncons.add((e1, e2))
        for con in dcons:
            self.constraints.remove(con)
        for con in ncons:
            self.constraints.add(con)
        for t in self.triangles:
            del t
        self.triangles = set()
        self.triangulate()
        self.delaunay_triangulate()

    def print_triangle(self, t:Triangle):
        print("Triangle :", end="")
        print(t)
        print(t.pts[0], ":", self.pts[t.pts[0]])
        print(t.pts[1], ":", self.pts[t.pts[1]])
        print(t.pts[2], ":", self.pts[t.pts[2]])
        print(t.neis[0])
        print(t.neis[1])
        print(t.neis[2])

    def dfs_constraint(self):
        total_bound = []
        checked = dict()
        for t in self.triangles:
            checked[t] = False
        for _ in range(len(self.region_boundary)):
            st = self.find_triangle(self.region_boundary[_-1], self.region_boundary[_])
            if checked[st]:
                continue
            # bd = [self.region_boundary[_]]
            bd = [self.region_boundary[_]]
            stack = [(st, st.get_ind(self.region_boundary[_]))]
            while stack:
                t, ind = stack.pop()
                if t==None:
                    bd.append(ind)
                    continue
                if checked[t]:
                    continue
                checked[t] = True
                # print(t.pts, ind)
                for i in range(1,-1,-1):
                    tt = t.nei(ind+i)
                    if tt==None:
                        stack.append((None, t.pt(ind+i+1)))
                        # bd.append(t.pt(ind+i+1))
                        # print(bd)
                        continue
                    if checked[tt]:
                        continue
                    p_ind = tt.get_ind(t.pt(ind+i))
                    stack.append((tt, p_ind))
            total_bound.append(bd)
        for e in self.constraints:
            st = self.find_triangle(e[0], e[1])
            if checked[st]:
                continue
            bd = [e[1]]
            stack = [(st, st.get_ind(e[1]))]
            while stack:
                t, ind = stack.pop()
                if t==None:
                    bd.append(ind)
                    continue
                if checked[t]:
                    continue
                checked[t] = True
                for i in range(1,-1,-1):
                    tt = t.nei(ind+i)
                    if tt==None:
                        stack.append((None, t.pt(ind+i+1)))
                        continue
                    if checked[tt]:
                        continue
                    p_ind = tt.get_ind(t.pt(ind+i))
                    stack.append((tt, p_ind))
            total_bound.append(bd)
        for e in self.constraints:
            st = self.find_triangle(e[1], e[0])
            if checked[st]:
                continue
            bd = [e[0]]
            stack = [(st, st.get_ind(e[0]))]
            while stack:
                t, ind = stack.pop()
                if t==None:
                    bd.append(ind)
                    continue
                if checked[t]:
                    continue
                checked[t] = True
                for i in range(1,-1,-1):
                    tt = t.nei(ind+i)
                    if tt==None:
                        stack.append((None, t.pt(ind+i+1)))
                        continue
                    if checked[tt]:
                        continue
                    p_ind = tt.get_ind(t.pt(ind+i))
                    stack.append((tt, p_ind))
            total_bound.append(bd)
        return total_bound

    def exterior_mandatory_st(self):
        apt = 0
        next = True
        while next:
            next = False
            obtuse = False
            for t in self.triangles:
                obt = -1
                q1 = self.pts[t.pts[0]]
                q2 = self.pts[t.pts[1]]
                q3 = self.pts[t.pts[2]]
                if (angle(q1,q2,q3) > MyNum(0)): obt = 1
                if (angle(q2,q3,q1) > MyNum(0)): obt = 2
                if (angle(q3,q1,q2) > MyNum(0)): obt = 0
                if obt==-1:
                    obtuse = True
                    continue
                e1 = (t.pt(obt+1),t.pt(obt+2))
                e2 = (t.pt(obt+2),t.pt(obt+1))
                if e1 in self.constraints or e2 in self.constraints:
                    # e11 = (t.pt(obt),t.pt(obt+1))
                    # e12 = (t.pt(obt+1),t.pt(obt))
                    # e21 = (t.pt(obt+2),t.pt(obt))
                    # e22 = (t.pt(obt),t.pt(obt+2))
                    # if e11 in self.constraints or e12 in self.constraints or e21 in self.constraints or e22 in self.constraints:
                    p = projection(self.pts[t.pt(obt)], self.pts[t.pt(obt+1)], self.pts[t.pt(obt+2)])
                    # print(p.x.toString(), p.y.toString())
                    self.add_steiner(p)
                    apt+=1
                    self.DrawResult(f"step_{apt}")
                    next = True
                    break
                    



            if not obtuse:
                return

    def exterior_solver(self):
        print("extracting...")
        bds = self.dfs_constraint()
        bds.sort(key=len, reverse=True)
        lb = bds[0]
        dt = Data(input="", pts = [self.pts[i] for i in lb], constraints = [], bds = list(range(len(lb))), fp_ind=len(lb), triangles=set())
        dt.instance_name = self.instance_name+"_extract"
        dt.DrawPoint()
        dt.triangulate()
        dt.MakeInstance()
        dt.WriteData()
        print(self.instance_name+" Done!")
        pass

    def partial_datas(self):
        bds = self.dfs_constraint()
        bds.sort(key=len, reverse=True)
        bds.pop(0)
        dts = []
        for lb in bds:
            cs = []
            for i in range(len(lb)):
                if (lb[i-1], lb[i]) in self.constraints:
                    cs.append(((len(lb)+i-1)%len(lb), i))
                if (lb[i], lb[i-1]) in self.constraints:
                    cs.append((i,(len(lb)+i-1)%len(lb)))
            dt = Data(input="", pts = [self.pts[i] for i in lb], constraints = set(), bds = list(range(len(lb))), fp_ind=len(lb), triangles=set())
            dt.ban = set(cs)
            dts.append(dt)
            del dt
        return dts

    def dfs(self, merged_e):
        checked = dict()
        for t in self.triangles:
            checked[t] = False
        score = dict()
        for i in range(len(merged_e)):
            for _e1 in merged_e[i]:
                score[(i,_e1)] = (False, (-1,-1),[],set())
        for i in range(len(merged_e)):
            for _e1 in merged_e[i]:
                if score[(i,_e1)][0]:
                    continue
                st:Triangle = self.find_triangle(i, _e1)
                if st==None:
                    score[(i,_e1)] = (True, (float("INF"),float("INF")),[],set())
                    continue
                p_score = 0
                p_obt = 0
                p_stei = set()
                p_tri = set()
                stack = [(st, st.get_ind(i))]
                bound = [(i,_e1)]
                while stack:
                    t, ind = stack.pop()
                    if checked[t]:
                        continue
                    p_score += 1
                    p_tri.add(t)
                    if self.is_obtuse(t):
                        p_obt += 1
                    checked[t] = True
                    for ii in range(3):
                        if t.pt(ii)>=self.fp_ind:
                            p_stei.add(t.pt(ii))
                    if (t.pt(ind+1), t.pt(ind+2)) not in score:
                        tt = self.find_triangle(t.pt(ind+2), t.pt(ind+1))
                        if tt!=None and checked[tt]!=True:
                            stack.append((tt, tt.get_ind(t.pt(ind+2))))
                    else:
                        bound.append((t.pt(ind+1), t.pt(ind+2)))
                    if (t.pt(ind+2), t.pt(ind)) not in score:
                        tt = self.find_triangle(t.pt(ind), t.pt(ind+2))
                        if tt!=None and checked[tt]!=True:
                            stack.append((tt, tt.get_ind(t.pt(ind))))
                    else:
                        bound.append((t.pt(ind+2), t.pt(ind)))
                for b in bound:
                    score[b] = (True, (p_obt, p_score), list(p_stei), p_tri)
        return score

    def delete_random_steiner(self, del_num):
        while del_num>0: # 지울 개수가 늘어나는 만큼 
            # 쿰쿰 ?
            
            bp = False
            dn = random.randint(1,del_num) # 
            del_num -= dn
            ind = 0
            del_pts = set()
            checked = dict()
            qt = None
            for t in self.triangles:
                if self.is_obtuse(t):
                    qt = t
                checked[t] = False
            if qt==None:
                break
            q = collections.deque([qt])
            while q:
                if bp:
                    break
                newt = q.popleft()
                if checked[newt]:
                    continue
                checked[newt] = True
                for p in newt.pts:
                    if p>=self.fp_ind:
                        del_pts.add(p)
                        if len(del_pts)==dn:
                            bp = True
                            break
                if bp:
                    break
                for t in newt.neis:
                    if t!=None and checked[t]==False:
                        q.append(t)
            
            self.delete_steiners(list(del_pts))

    def delete_random_steiner_query(self, _i, dn):
        bp = False
        ind = 0
        del_pts = set()
        checked = dict()
        qt = None
        for t in self.triangles:
            checked[t] = False
        for t in self.triangles:
            if _i in t.pts:
                qt = t
                if self.is_obtuse(t):
                    break
        if qt==None:
            return
        q = collections.deque([qt])
        while q:
            if bp:
                break
            newt = q.popleft()
            if checked[newt]:
                continue
            checked[newt] = True
            for p in newt.pts:
                if p>=self.fp_ind:
                    del_pts.add(p)
                    if len(del_pts)==dn:
                        bp = True
                        break
                        
            if bp:
                break
            for t in newt.neis:
                if t!=None and checked[t]==False:
                    q.append(t)
        # for p in del_pts:
        self.delete_steiners(list(del_pts))

    def merge_result(self, dt):
        e1 = [set() for _ in range(self.fp_ind)]
        e2 = [set() for _ in range(self.fp_ind)]
        for t in self.triangles:
            for i in range(3):
                if t.pts[i]<self.fp_ind and t.pts[i-1]<self.fp_ind:
                    e1[t.pts[i]].add(t.pts[i-1])
                    e1[t.pts[i-1]].add(t.pts[i])
        for t in dt.triangles:
            for i in range(3):
                if t.pts[i]<self.fp_ind and t.pts[i-1]<self.fp_ind:
                    e2[t.pts[i]].add(t.pts[i-1])
                    e2[t.pts[i-1]].add(t.pts[i])
        merged_e = [set() for _ in range(self.fp_ind)]
        for i in range(self.fp_ind):
            merged_e[i] = e1[i].intersection(e2[i])
        score_1 = self.dfs(merged_e)
        score_2 = dt.dfs(merged_e)
        new_ind1 = [-1]*len(self.pts)
        new_ind2 = [-1]*len(dt.pts)
        add_pts = []
        add_e = []
        for key in score_1.keys():
            if score_1[key][1]>score_2[key][1]:
                for t in score_2[key][3]:
                    ind0, ind1, ind2 = t.pts[0], t.pts[1], t.pts[2]
                    if ind0>=self.fp_ind:
                        if new_ind2[ind0]==-1:
                            new_ind2[ind0] = len(add_pts)+self.fp_ind
                            add_pts.append(dt.pts[ind0])
                        ind0 = new_ind2[ind0]
                    if ind1>=self.fp_ind:
                        if new_ind2[ind1]==-1:
                            new_ind2[ind1] = len(add_pts)+self.fp_ind
                            add_pts.append(dt.pts[ind1])
                        ind1 = new_ind2[ind1]
                    if ind2>=self.fp_ind:
                        if new_ind2[ind2]==-1:
                            new_ind2[ind2] = len(add_pts)+self.fp_ind
                            add_pts.append(dt.pts[ind2])
                        ind2 = new_ind2[ind2]
                    add_e.append((ind0,ind1))
                    add_e.append((ind1,ind2))
                    add_e.append((ind2,ind0))
            else:
                for t in score_1[key][3]:
                    ind0, ind1, ind2 = t.pts[0], t.pts[1], t.pts[2]
                    if ind0>=self.fp_ind:
                        if new_ind1[ind0]==-1:
                            new_ind1[ind0] = len(add_pts)+self.fp_ind
                            add_pts.append(self.pts[ind0])
                        ind0 = new_ind1[ind0]
                    if ind1>=self.fp_ind:
                        if new_ind1[ind1]==-1:
                            new_ind1[ind1] = len(add_pts)+self.fp_ind
                            add_pts.append(self.pts[ind1])
                        ind1 = new_ind1[ind1]
                    if ind2>=self.fp_ind:
                        if new_ind1[ind2]==-1:
                            new_ind1[ind2] = len(add_pts)+self.fp_ind
                            add_pts.append(self.pts[ind2])
                        ind2 = new_ind1[ind2]
                    add_e.append((ind0,ind1))
                    add_e.append((ind1,ind2))
                    add_e.append((ind2,ind0))
                    
        print("Find new Sol! merging....")
        
        self.delete_steiners(list(range(self.fp_ind, len(self.pts))))
        for t in self.triangles:
            del t
        self.triangles = set()
        # new_ind = [-1]*len(self.pts)
        # add_pts = []
        # i = 0
        # for key in score_1.keys():
        #     for t in score_1[key][3]:
        #         for _i in range(3):
        #             print(t.pts[_i])
        #             if new_ind[t.pts[_i]]==-1:
        #                 new_ind[t.pts[_i]] = i
        #                 if t.pts[_i]>=self.fp_ind:
        #                     add_pts.append(self.pts(t.pts[_i]))
        #                 i+=1
        # while len(self.pts)>self.fp_ind:
        #     self.delete_steiner(len(self.pts)-1)
        self.triangulate()
        self.DrawResult("step")
        self.add_steiners(add_pts)
        self.DrawResult("step")
        for e in add_e:
            if self.find_triangle(e[0],e[1])==-1 and self.find_triangle(e[1],e[0])!=-1:
                self.resolve_cross(e)
                self.DrawResult("step")

def angle(p1:Point, p2:Point, p3:Point):
    if p1==p2:
        raise Exception("Cannot Calculate Angle")
    if p2==p3:
        raise Exception("Cannot Calculate Angle")
    p12x = p2.x-p1.x
    p12y = p2.y-p1.y
    p23x = p2.x-p3.x
    p23y = p2.y-p3.y
    ab = p12x * p23x + p12y * p23y
    a = p12x * p12x + p12y * p12y
    b = p23x * p23x + p23y * p23y
    if (ab >= MyNum(0)):
        return - ab * ab / a / b
    else:
        return ab * ab / a / b

def turn(p1:Point, p2:Point, p3:Point):
    return (p2.x - p1.x) * (p3.y - p1.y) - (p2.y - p1.y) * (p3.x - p1.x)

def sqdist(p:Point, q:Point):
    xd = p.x - q.x
    yd = p.y - q.y
    return xd * xd + yd * yd

# 어귀
# hwi
def projection(p:Point, q1:Point, q2:Point):
    if q1.x == q2.x:
        return Point(q1.x, p.y)
    if q1.y == q2.y:
        return Point(p.x, q1.y)
    
    s1 = (q2.y - q1.y) / (q2.x - q1.x)
    b1 = q1.y - s1 * q1.x
    s2 = MyNum(-1) / s1
    b2 = p.y - s2 * p.x
    rx = (b2 - b1) / (s1 - s2)
    ry = rx * s1 + b1

    return Point(rx, ry)

def right_angle_point(p1:Point, p2:Point, p3:Point, p4:Point):
    if p3.x == p4.x:
        if p1.y == p2.y:
            return None
        s = (p1.x - p2.x) / (p2.y - p1.y)
        b = p2.y - s * p2.x
        qy = s * p3.x + b
        return Point(p3.x, qy)
    elif p1.y == p2.y:
        s = (p3.y - p4.y) / (p3.x - p4.x)
        b = p3.y - s * p3.x
        qy = s * p2.x + b
        return Point(p2.x, qy)
    else:
        s1 = (p3.y - p4.y) / (p3.x - p4.x)
        s2 = (p1.x - p2.x) / (p2.y - p1.y)
        if s1 == s2:
            return None
        b1 = p3.y - s1 * p3.x
        b2 = p2.y - s2 * p2.x
        qx = (b2 - b1) / (s1 - s2)
        qy = qx * s1 + b1
        return Point(qx, qy)

def midpoint(p:Point, q:Point):
    return Point((p.x + q.x) / 2, (p.y + q.y) / 2)

def intersections_of_orthogonals(p1:Point, p2:Point, p3:Point, p4:Point):
    if (p1.y == p2.y):
        if (p3.y == p4.y):
            return []
        s = (p4.x - p3.x) / (p3.y - p4.y)
        b3 = p3.y - s * p3.x
        b4 = p4.y - s * p4.x
        res = []
        for p in [p1, p2]:
            for b in [b3, b4]:
                res = res + imprecise_points(p.x.toFloat(), s.toFloat() * p.x.toFloat() + b.toFloat())
        return res
    elif p3.y == p4.y:
        return intersections_of_orthogonals(p3, p4, p1, p2)
    else:
        s12 = (p2.x - p1.x) / (p1.y - p2.y)
        s34 = (p4.x - p3.x) / (p3.y - p4.y)
        if s12 == s34:
            return []
        b1 = p1.y - s12 * p1.x
        b2 = p2.y - s12 * p2.x
        b3 = p3.y - s34 * p3.x
        b4 = p4.y - s34 * p4.x
        x13 = (b1 - b3) / (s34 - s12)
        x23 = (b2 - b3) / (s34 - s12)
        x14 = (b1 - b4) / (s34 - s12)
        x24 = (b2 - b4) / (s34 - s12)
        res = []
        for x, b in [[x13, b1], [x23, b2], [x14, b1], [x24, b2]]:
            res = res + imprecise_points(x.toFloat(), s12.toFloat() * x.toFloat() + b.toFloat())
        return res

def intersections_of_disks(p1:Point, r1:MyNum, p2:Point, r2:MyNum):
    if p1.y == p2.y:
        if p1.x == p2.x:
            return []
        qx = (p1.x + p2.x + (r2 - r1) / (p1.x - p2.x)) / 2
        sqrhs = r1 - (qx - p1.x) * (qx - p1.x)
        if sqrhs < 0:
            return []
        frhs = math.sqrt(sqrhs.toFloat())
        return imprecise_points(qx.toFloat(), p1.y.toFloat() + frhs) + imprecise_points(qx.toFloat(), p1.y.toFloat() - frhs)
    s = (p2.x - p1.x) / (p1.y - p2.y)
    bb = (p1.x * p1.x + p1.y * p1.y - p2.x * p2.x - p2.y * p2.y - r1 + r2) / (p1.y - p2.y) / 2
    a = s * s + 1
    b = (-p1.x + s * (bb - p1.y)) * 2
    c = p1.x * p1.x + (bb - p1.y) * (bb - p1.y) - r1
    inroot = b * b - a * c * 4
    if inroot < 0:
        return []
    froot = math.sqrt(inroot.toFloat())
    x1 = (-b.toFloat() + froot) / a.toFloat() / 2
    x2 = (-b.toFloat() - froot) / a.toFloat() / 2
    return imprecise_points(x1, s.toFloat() * x1 + bb.toFloat()) + imprecise_points(x2, s.toFloat() * x2 + bb.toFloat())

def intersections_of_ortho_disk(p1:Point, p2:Point, p3:Point, p4:Point):
    res = []
    for q1, q2, q3, q4 in [(p1, p2, p3, p4), (p3, p4, p1, p2)]:
        m = midpoint(q1, q2)
        r = sqdist(q1, q2) / 4
        if q3.y == q4.y:
            for qq in (q3, q4):
                rhs = r - (m.x - qq.x) * (m.x - qq.x)
                if rhs < 0:
                    continue
                frhs = math.sqrt(rhs.toFloat())
                res = res + imprecise_points(m.x.toFloat() + frhs, qq.y.toFloat()) + imprecise_points(m.x.toFloat() - frhs, qq.y.toFloat())
        else:
            s = (q3.x - q4.x) / (q4.y - q3.y)
            for qq in (q3, q4):
                bb = qq.y - s * qq.x
                a = s * s + 1
                b = (-m.x + s * (bb - m.y)) * 2
                c = m.x * m.x + (bb - m.y) * (bb - m.y) - r
                inroot = b * b - a * c * 4
                if inroot < 0:
                    continue
                froot = math.sqrt(inroot.toFloat())
                x1 = (-b.toFloat() + froot) / a.toFloat() / 2
                x2 = (-b.toFloat() - froot) / a.toFloat() / 2
                res = res + imprecise_points(x1, s.toFloat() * x1 + bb.toFloat()) + imprecise_points(x2, s.toFloat() * x2 + bb.toFloat())
    return res

def imprecise_points(x:float, y:float):
    xi = int(x * IMP)
    yi = int(y * IMP)
    res = []
    for i in range(- (GRID // 2), GRID - (GRID // 2)):
        for j in range(- (GRID // 2), GRID - (GRID // 2)):
            res.append(Point(xi + i, yi + j))
    return res