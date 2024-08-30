from MyNum import MyNum
import json
import cv2
import numpy as np
import random
from collections import deque
import pdb
import copy
from typing import List

class Point:
    def __init__(self, x, y):
        self.x = MyNum(x)
        self.y = MyNum(y)

    def __eq__(self, p):
        return self.x==p.x and self.y==p.y
        
    def __str__(self):
        return "("+str(self.x)+", "+str(self.y)+")"
    
    def __ne__(self, p):
        return self.x != p.x or self.y != p.y

class Triangle:
    def __init__(self, p:int, q:int, r:int):
        self.pts = [p, q, r]
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

    
class Data:
    def __init__(self, input, pts=None, constraints=None, bds=None, fp_ind=None):
        if input:
            self.input = input
            self.triangles = set()
            self.ReadData()
        else:
            self.input = ""
            self.instance_name = ""
            self.fp_ind = fp_ind
            self.pts = pts
            self.region_boundary = bds
            self.num_constraints = constraints
        

    def ReadData(self):
        print("--------------------ReadData--------------------")
        with open(self.input, "r", encoding="utf-8") as f:
            root = json.load(f)
            # print(root)
            self.instance_name = root["instance_uid"]
            self.fp_ind = int(root["num_points"])
            pts_x = root["points_x"]
            pts_y = root["points_y"]
            self.pts = []
            for i in range(len(pts_y)):
                self.pts.append(Point(pts_x[i], pts_y[i]))
            self.region_boundary = deque(root["region_boundary"])
            self.num_constraints =  root["num_constraints"]
            self.constraints = set()
            for con in root["additional_constraints"]:
                self.constraints.add((con[0], con[1]))
        

    def WriteData(self):
        print("--------------------WriteData--------------------")
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
            if e1 not in const_edges and e1 not in int_edges:
                int_edges.append(e1)
            if e2 not in const_edges and e2 not in int_edges:
                int_edges.append(e2)
            if e3 not in const_edges and e3 not in int_edges:
                int_edges.append(e3)
        obt = 0
        for t in self.triangles:
            if self.is_obtuse(t):
                obt+=1
        inst["edges"] = int_edges
        print("indstance id: ", self.instance_name)
        print("Steiner point: ", len(self.pts)-self.fp_ind)
        print("Total Triangle: ", len(self.triangles))
        print("Obtuse Triangle: ", obt)

        # print(inst)
        with open("solutions/" + self.instance_name + ".solution.json", "w", encoding="utf-8") as f:
            json.dump(inst, f, indent='\t')


    def DrawResult(self, add = ""):
        print("--------------------DrawResult--------------------")
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
        if add=="":
            cv2.imwrite("solutions/"+self.instance_name+".solution.png", img)
        else:
            cv2.imwrite("solutions/"+self.instance_name+".solution_"+add+".png", img)

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

    def max_angle(self, t:Triangle):
        q1 = self.pts[t.pts[0]]
        q2 = self.pts[t.pts[1]]
        q3 = self.pts[t.pts[2]]
        return max(angle(q1,q2,q3),angle(q2,q3,q1),angle(q3,q1,q2))

    def where_is_obtuse(self, t:Triangle):
        q1 = self.pts[t.pts[0]]
        q2 = self.pts[t.pts[1]]
        q3 = self.pts[t.pts[2]]
        if (angle(q1,q2,q3) > MyNum(0)): return 1
        if (angle(q2,q3,q1) > MyNum(0)): return 2
        if (angle(q3,q1,q2) > MyNum(0)): return 0
        return -1
    
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

    def triangulate(self):
        check = [False] * len(self.pts)
        self.triangulate_polygon(deque(self.region_boundary))
        for d in self.region_boundary:
            check[d] = True
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
        i = -1
        if self.is_on(t.pts[0], t.pts[1], q):
            i = 0
            tt = t.neis[0]
        elif self.is_on(t.pts[1], t.pts[2], q):
            i = 1
            tt = t.neis[1]
        elif self.is_on(t.pts[2], t.pts[0], q):
            i = 2
            tt = t.neis[2]
        if i!=-1 and tt==None:
            t1 = Triangle(p, t.pt(i + 1), t.pt(i + 2))
            t1.neis[0] = tt
            ti = t.nei(i + 1)
            if ti:
                ti.neis[ti.get_ind(t1.pts[2])] = t1
            t1.neis[1] = ti
            t1.neis[2] = t
            t.pts[(i + 1) % 3] = p
            t.neis[i] = tt
            t.neis[(i + 1) % 3] = t1
            self.triangles.add(t1)
            # pdb.set_trace()
        elif tt:
            j = tt.get_ind(t.pt(i + 1))
            t1 = Triangle(p, t.pt(i + 1), t.pt(i + 2))
            t1.neis[0] = tt
            ti = t.nei(i + 1)
            if ti:
                ti.neis[ti.get_ind(t1.pts[2])] = t1
            t1.neis[1] = ti # Check!!!ADDED BY JAEGUN
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

    def flip(self, t:Triangle, i:int):
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
                self.flip(ttt, (k + 2) % 3)
            else:
                self.flip(tt, (j + 2) % 3)
            return self.flip(t, i)
        else:
            ttt = tt.nei(j + 1)
            k = (ttt.get_ind(tt.pt(j + 2)) + 2) % 3
            pk = ttt.pts[k]
            if turn(self.pts[pi], self.pts[t.pts[i]], self.pts[pk]) <= 0:
                self.flip(ttt, k)
            else:
                self.flip(tt, (j + 1) % 3)
            return self.flip(t, i)

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
    def dfs(self, qt, key_func=is_obtuse):
        check = {}
        return_t = []
        bd = []
        outer_t_list = []
        for t in self.triangles:
            check[t] = False
        stack = [qt]
        while stack:
            v = stack.pop()
            if check[v]==True:
                continue
            check[v] = True
            return_t.append(v)
            for num, i in enumerate(v.neis):
                if i!=None:
                    if key_func(i) and check[i]==False:
                        stack.append(i)
                    if not key_func(i):
                        bd.append((v.pt(num),v.pt(num+1)))
                        outer_t_list.append(i)
                else:
                    bd.append((v.pt(num),v.pt(num+1)))
                    outer_t_list.append(i)

        return return_t, bd, outer_t_list

    def partial_minmax_triangulate(self, iter = 1000):
        for _ in range(iter):
            print(f"Iteration [{_:>4d}/{iter:>4d}]")
            obt = 0
            for t in self.triangles:
                if self.is_obtuse(t):
                    obt+=1
            print("Total Triangle: ", len(self.triangles))
            print("Obtuse Triangle: ", obt)
            for __ in range(100):
                self.partition_boundary_obtuse()
                find = False
                t = random.sample(self.triangles,1)[0]
                if self.is_obtuse(t):
                    MA = self.max_angle(t)
                    # print(MA)
                    find = True
                    # t_list, bd, outer_t_list = self.dfs(t, key_func=lambda x:self.max_angle(x)<=MA)
                    # sorted_bd = [bd[0][0], bd[0][1]]
                    # sorted_outer_t_list = [outer_t_list[0]]
                    # while True:
                    #     bp = False
                    #     for i, b in enumerate(bd):
                    #         if b[0]==sorted_bd[-1]:
                    #             sorted_outer_t_list.append(outer_t_list[i])
                    #             if sorted_bd[0]==b[1]:
                    #                 bp = True
                    #             else:
                    #                 sorted_bd.append(b[1])
                    #             break
                    #     if bp:break
                    # sorted_bd.reverse()
                    # sorted_outer_t_list.reverse()
                    self.partial_ear_cut(t,self.where_is_obtuse(t))
                    self.DrawPoint()
                    for t in self.triangles:
                        for i in range(1,4):
                            tt = self.find_triangle(t.pt(i), t.pt(i-1))
                            if t.nei(i-1)!=tt:
                                pdb.set_trace()
                            
                    # pts = set()
                    # for t in t_list:
                    #     for p in t.pts:
                    #         pts.add(self.pts[p])
                    # pts = list(pts)
                    # small_region = []
                    # small_triangles = set()
                    # con = []
                    # for t in sorted_bd:
                    #     for i,p in enumerate(pts):
                    #         if self.pts[t]==p:
                    #             small_region.append(i)
                    #             break
                    # for t in t_list:
                    #     p1, p2, p3 = t.pts
                    #     for i,p in enumerate(pts):
                    #         if self.pts[p1]==p:
                    #             newp1=i
                    #         if self.pts[p2]==p:
                    #             newp2=i
                    #         if self.pts[p3]==p:
                    #             newp3=i
                    #     small_triangles

                    
                    # for t in t_list:
                    # Data(None, pts, constraints=con, bds=small_region, fp_ind=len(pts),triangulate = small_triangles)
                    # pdb.set_trace()
                    break
            print("")
            if not find:
                print("Cannot find obtuse triangle.....Stop")
                break
        # while True:
        #     for t in self.triangles:

        #     maxang = MyNum(0)
        #     mt = None
        #     for t in self.triangles:
        #         ang = angle(self.pts[t.pts[2]], self.pts[t.pts[0]], self.pts[t.pts[1]])
        #         if ang > maxang:
        #             mt = t
        #             maxang = ang
        #             i = 0
        #         ang = angle(self.pts[t.pts[0]], self.pts[t.pts[1]], self.pts[t.pts[2]])
        #         if ang > maxang:
        #             mt = t
        #             maxang = ang
        #             i = 1
        #         ang = angle(self.pts[t.pts[1]], self.pts[t.pts[2]], self.pts[t.pts[0]])
        #         if ang > maxang:
        #             mt = t
        #             maxang = ang
        #             i = 2
        #     if (not mt) or (not self.ear_cut(mt, i)):
        #         break
    
    def partial_ear_cut(self, t:Triangle, i:int):
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
            if self.max_angle(t.neis[i])<=ang:
                r_neis.append((t.neis[i], t.neis[i].get_ind(t.pt(i + 1)), True))
            else:
                r_neis.append((t.neis[i], t.neis[i].get_ind(t.pt(i + 1)), False))
        else:
            r_neis.append((None, 0, False))
        if t.nei(i + 2):
            if self.max_angle(t.nei(i+2))<=ang:
                l_neis.append((t.nei(i + 2), t.nei(i + 2).get_ind(t.pts[i]), True))
            else:
                l_neis.append((t.nei(i + 2), t.nei(i + 2).get_ind(t.pts[i]), False))
        else:
            l_neis.append((None, 0, False))
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
        tt_check = True
        while True:
            if not tt_check:
                abort()
                return False
            stop[0] = False
            try:
                j = (tt.get_ind(r_chain[-1]) + 1) % 3
            except:
                pdb.set_trace()
            s = self.pts[tt.pts[j]]
            removed.add(tt)
            ttt = tt.neis[j]
            if ttt:
                if self.max_angle(ttt)<=ang:
                    l_neis.append((ttt, ttt.get_ind(tt.pt(j + 1)), True))
                else:
                    l_neis.append((ttt, ttt.get_ind(tt.pts[j]), False))
            else:
                l_neis.append((None, 0, False))
            ttt = tt.nei(j + 2)
            if ttt:
                if self.max_angle(ttt)<=ang:
                    r_neis.append((ttt, ttt.get_ind(tt.pts[j]), True))
                else:
                    r_neis.append((ttt, ttt.get_ind(tt.pts[j]), False))
            else:
                r_neis.append((None, 0, False))
            if turn(q, r, s) <= 0:
                while not stop[0]:
                    cutright()
                r_chain.append(tt.pts[j])
                tt = l_neis[-1][0]
                tt_check = l_neis[-1][-1]
                l_neis.pop()
            elif turn(q, l, s) >= 0:
                while not stop[0]:
                    cutleft()
                l_chain.append(tt.pts[j])
                tt = r_neis[-1][0]
                tt_check = r_neis[-1][-1]
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
                    tt_check = r_neis[-1][-1]
                    r_neis.pop()
                elif not lsgn:
                    r = s
                    r_chain.append(tt.pts[j])
                    tt = l_neis[-1][0]
                    tt_check = l_neis[-1][-1]
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

    def find_triangle(self, q1:int, q2:int):
        for t in self.triangles:
            if t.pts[0] == q1 and t.pts[1] == q2:
                return t
            if t.pts[1] == q1 and t.pts[2] == q2:
                return t
            if t.pts[2] == q1 and t.pts[0] == q2:
                return t
        return None
    def add_steiner(self, p:Point):
        self.pts.append(p)
        for i in range(len(self.region_boundary)-1):
            if self.is_on(self.region_boundary[i], self.region_boundary[i+1], p):
                self.region_boundary.insert(i+1, len(self.pts)-1)
                break
        for e in self.constraints:
            if self.is_on(e[0], e[1], p):
                self.constraints.add([e[0],len(self.pts)-1])
                self.constraints.add([e[1],len(self.pts)-1])
                self.constraints.remove(e)
        self.insert_point(len(self.pts)-1)
        # self.triangles = set()
        # self.triangulate()
        # self.minmax_triangulate()

    def add_steiners(self, l:List[Point]):
        for p in l:
            self.pts.append(p)
            for i in range(len(self.region_boundary)-1):
                if self.is_on(self.region_boundary[i], self.region_boundary[i+1], p):
                    # pdb.set_trace()
                    self.region_boundary.insert(i+1, len(self.pts)-1)
                    break
            for e in self.constraints:
                if self.is_on(e[0], e[1], p):
                    self.constraints.add([e[0],len(self.pts)-1])
                    self.constraints.add([e[1],len(self.pts)-1])
                    self.constraints.remove(e)
        for i in range(len(l)):
            self.insert_point(len(self.pts)-1-i)
        # pdb.set_trace()
        # self.DrawResult("check")
        # self.triangles = set()
        # self.triangulate()
        # self.minmax_triangulate()
        
    def delete_steiner(self, i:int):
        if i>len(self.pts):
            raise Exception("There is no such point to delete")
        if i<self.fp_ind:
            pass
            # raise Exception("Cannot delete given point")
        # if i in self.region_boundary:
        #     pass
        for t in self.triangles:
            if i in t.pts:
                break
        t_list = [t]
        small_boundary = [t.pt(t.get_ind(i)+2)]
        outer_t_list = [t.nei(t.get_ind(i)+1)]
        while True:  
            t_ind = t_list[-1].get_ind(i)+2
            new_t = t_list[-1].nei(t_ind)
            if new_t!=t_list[0] and new_t!=None:
                t_list.append(new_t)
                outer_t_list.append(t_list[-1].nei(t_list[-1].get_ind(i)+1))  
                small_boundary.append(t_list[-1].pt(t_list[-1].get_ind(i)+2))
            else:
                if new_t==None:
                    outer_t_list.append(None)
                    small_boundary.append(t.pt(t.get_ind(i)+1))
                break
        for t in t_list:
            self.triangles.remove(t)
                
        self.triangulate_polygon(deque(small_boundary))
        small_boundary.append(small_boundary[0])
        for t in self.triangles:
            for j in range(len(small_boundary)-1):
                if t.get_ind(small_boundary[j])!=-1 and t.get_ind(small_boundary[j+1])==(t.get_ind(small_boundary[j])+1)%3:
                    t.neis[t.get_ind(small_boundary[j])] = outer_t_list[j]
                    if outer_t_list[j]!=None:
                        outer_t_list[j].neis[outer_t_list[j].get_ind(small_boundary[j])] = t
        if i in self.region_boundary:
            self.region_boundary.remove(i)
        i_connect = []
        for e in self.constraints:
            if e[0]==i:
                i_connect.append(e[1])
            if e[1]==i:
                i_connect.append(e[0])
        con = []
        if len(i_connect)>=2:
            for j in range(len(i_connect)-1):
                for k in range(j+1, len(i_connect)):
                    if self.is_on(j,k,self.pts[i]):
                        self.constraints.append([j,k])
                        con = [j,k]
        e_list = []
        for e in self.constraints:
            if i in e:
                e_list.append(e)
        for e in e_list:
            self.constraints.remove(e)
        if i!=len(self.pts)-1:
            self.pts[i] = self.pts[-1]
            for t in self.triangles:
                if t.get_ind(len(self.pts)-1)!=-1:
                    t.pts[t.get_ind(len(self.pts)-1)] = i
        self.pts.pop()
        if con:
            self.resolve_cross(con)
    def find_perp(self, t:Triangle):
        obtuse_ind = self.where_is_obtuse(t)
        if obtuse_ind==-1:
            return
        p3 = self.pts[t.pt(obtuse_ind)]
        p1 = self.pts[t.pt(obtuse_ind+1)]
        p2 = self.pts[t.pt(obtuse_ind+2)]
        if p1.x==p2.x:
            x = p1.x
            y = p3.y
        if p1.y==p2.y:
            x = p3.x
            y = p1.y
        else:
            x = ((p2.y-p1.y)*p1.x/(p2.x-p1.x)+(p2.x-p1.x)*p3.x/(p2.y-p1.y)+p3.y-p1.y)/((p2.y-p1.y)/(p2.x-p1.x)+(p2.x-p1.x)/(p2.y-p1.y))
            y = (p2.y-p1.y)*(x-p1.x)/(p2.x-p1.x)+p1.y
        # pdb.set_trace()
        return Point(x,y)
        
    def additional_triangulate(self):
        xs = sorted([p.x for p in self.pts])
        ys = sorted([p.y for p in self.pts])
        # mindist = xs[1]-xs[0]
        # for i in range(len(xs)-1):
        #     if mindist>xs[i+1]-xs[i]:
        #         mindist = xs[i+1]-xs[i]
        # for i in range(len(ys)-1):
        #     if mindist>ys[i+1]-ys[i]:
        #         mindist = ys[i+1]-ys[i]
        # addx = []
        # for i in range(len(xs)-1):
        #     if mindist<xs[i+1]-xs[i]:
        #         ds = int((xs[i+1]-xs[i]+mindist-1)/mindist)
        #         for d in range(ds):
        #             addx.append(xs[i]+int(MyNum(d+1)*(xs[i+1]-xs[i])/ds))
        # addy = []
        # for i in range(len(ys)-1):
        #     if mindist<ys[i+1]-ys[i]:
        #         ds = int((ys[i+1]-ys[i]+mindist-1)/mindist)
        #         for d in range(ds):
        #             addy.append(ys[i]+int(MyNum(d+1)*(ys[i+1]-ys[i])/ds))
        # pdb.set_trace()
        # xs+=addx
        # ys+=addy

        
        steiners = []
        for x in xs:
            for y in ys:
                p = Point(x,y)
                new = True
                for pt in self.pts:
                    if pt==p:
                        new = False
                        break
                if not new: continue
                add = False
                for t in self.triangles:
                    if self.is_in(t,p):
                        steiners.append(p)
                        add = True
                        break
                    if add: break
        for i in range(len(self.region_boundary)-1):
            p1, p2 = self.pts[self.region_boundary[i]],self.pts[self.region_boundary[i+1]]
            for x in xs:
                if min(p1.x,p2.x)<x and x<max(p1.x,p2.x):
                    steiners.append(Point(x,p1.y+(p2.y-p1.y)*(x-p1.x)/(p2.x-p1.x)))
            for y in ys:
                if min(p1.y,p2.y)<y and y<max(p1.y,p2.y):
                    steiners.append(Point(p1.x+(p2.x-p1.x)*(y-p1.y)/(p2.y-p1.y),y))
        p1, p2 = self.pts[self.region_boundary[-1]],self.pts[self.region_boundary[0]]
        for x in xs:
            if min(p1.x,p2.x)<x and x<max(p1.x,p2.x):
                steiners.append(Point(x,p1.y+(p2.y-p1.y)*(x-p1.x)/(p2.x-p1.x)))
        for y in ys:
            if min(p1.y,p2.y)<y and y<max(p1.y,p2.y):
                steiners.append(Point(p1.x+(p2.x-p1.x)*(y-p1.y)/(p2.y-p1.y),y))
        for e in self.constraints:
            p1, p2 = self.pts[e[0]],self.pts[e[1]]
            for x in xs:
                if min(p1.x,p2.x)<x and x<max(p1.x,p2.x):
                    steiners.append(Point(x,p1.y+(p2.y-p1.y)*(x-p1.x)/(p2.x-p1.x)))
            for y in ys:
                if min(p1.y,p2.y)<y and y<max(p1.y,p2.y):
                    steiners.append(Point(p1.x+(p2.x-p1.x)*(y-p1.y)/(p2.y-p1.y),y))
        self.add_steiners(steiners)
        self.DrawPoint()
        self.minmax_triangulate()
    def partition_boundary_obtuse(self):
        steiners = []
        for t in self.triangles:
            if self.is_obtuse(t):
                obtuse_ind = self.where_is_obtuse(t)
                if not t.nei(obtuse_ind+1):
                    steiners.append(self.find_perp(t))
        self.add_steiners(steiners)
        self.minmax_triangulate()


        

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

