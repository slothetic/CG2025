from MyNum import MyNum
import json
import cv2
import numpy as np
import random
import re
from collections import deque
import pdb
import copy
import math

IMP = 100

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
    def __init__(self, input):
        self.input = input
        self.triangles = set()
        self.ReadData()

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

        inst["edges"] = int_edges 
        print(inst)
        with open("solutions/" + self.instance_name + ".solution.json", "w", encoding="utf-8") as f:
            json.dump(inst, f, indent='\t')


    def DrawResult(self, name=""):
        print("--------------------DrawResult--------------------")
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
            pts = np.array([[minw+int(rad*self.pts[t.pts[0]].x), minh-int(rad*self.pts[t.pts[0]].y)],[minw+int(rad*self.pts[t.pts[1]].x), minh-int(rad*self.pts[t.pts[1]].y)],[minw+int(rad*self.pts[t.pts[2]].x), minh-int(rad*self.pts[t.pts[2]].y)]], dtype=np.int32).reshape(1,-1,2)
            # print(pts)
            cv2.fillPoly(img, pts, color = (random.randint(220,254),random.randint(220,254),random.randint(220,254)))
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
        cv2.imwrite("solutions/"+self.instance_name + ".solution" + name + ".png", img)

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
                y1 = max(q1.y, q2.y)
                y2 = min(q1.y, q2.y)
                return (y1 < p.y) and (p.y < y2)
            else:
                x1 = max(q1.x, q2.x)
                x2 = min(q1.x, q2.x)
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
            t1.neis[2] = t
            t2 = Triangle(p, tt.pt(j + 1), tt.pt(j + 2))
            t2.neis[0] = t
            tj = tt.nei(j + 1)
            if tj:
                tj.neis[tj.get_ind(t2.pts[2])] = t2
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
        self.triangles = set()
        self.triangulate()
        self.minmax_triangulate()

    def add_steiners(self, l:list[Point]):
        for p in l:
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
        self.triangles = set()
        self.triangulate()
        self.minmax_triangulate()
        
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
        


            
    def make_non_obtuse(self, t:Triangle):
        if (angle(self.pts[t.pts[2]], self.pts[t.pts[0]], self.pts[t.pts[1]]) > 0):
            i = 0
        if (angle(self.pts[t.pts[0]], self.pts[t.pts[1]], self.pts[t.pts[2]]) > 0):
            i = 1
        if (angle(self.pts[t.pts[1]], self.pts[t.pts[2]], self.pts[t.pts[0]]) > 0):
            i = 2
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
        while True:
            if not tt:
                break
            stop[0] = False
            j = (tt.get_ind(r_chain[-1]) + 1) % 3
            s = self.pts[tt.pts[j]]
            self.triangles.remove(tt)
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
        print(len(r_chain), len(l_chain))
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
            print(len(farp))
            self.triangulate_polygon(farp)
            if tt:
                ttt = self.find_triangle(r_chain[-1], l_chain[-1])
                ttt.neis[ttt.get_ind(r_chain[-1])] = tt
                tt.neis[j] = ttt
            print('cutting done')
            while len(r_chain) - 1 > ri:
                ttt = self.find_triangle(r_chain[-2], r_chain[-1])
                ttt.neis[ttt.get_ind(r_chain[-2])] = r_neis[-1][0]
                if r_neis[-1][0]:
                    r_neis[-1][0].neis[r_neis[-1][1]] = ttt
                r_chain.pop()
                r_neis.pop()
            print('rchain done')
            while len(l_chain) - 1 > li:
                ttt = self.find_triangle(l_chain[-1], l_chain[-2])
                ttt.neis[ttt.get_ind(l_chain[-1])] = l_neis[-1][0]
                if l_neis[-1][0]:
                    l_neis[-1][0].neis[l_neis[-1][1]] = ttt
                l_chain.pop()
                l_neis.pop()
            print('lchain done')
            tt = self.find_triangle(l_chain[-1], r_chain[-1])
            j = tt.get_ind(l_chain[-1])
        flag = len(l_chain) == 2 and angle(self.pts[t.pts[i]], self.pts[l_chain[1]], self.pts[r_chain[-1]]) < 0
        flag = flag or (len(r_chain) == 2 and angle(self.pts[t.pts[i]], self.pts[r_chain[1]], self.pts[l_chain[-1]]) < 0)
        if flag:
            if not tt:
                cands = []
                pp = projection(self.pts[t.pts[i]], self.pts[l_chain[-1]], self.pts[r_chain[-1]])
                if self.is_on(l_chain[-1], r_chain[-1], pp):
                    cands.append(pp)
                if l_neis[0][0] or len(l_chain) > 2:
                    lp = right_angle_point(self.pts[r_chain[1]], self.pts[t.pts[i]], self.pts[l_chain[-1]], self.pts[r_chain[-1]])
                    if lp and self.is_on(l_chain[-1], r_chain[-1], lp):
                        cands.append(lp)
                if r_neis[0][0] or len(r_chain) > 2:
                    rp = right_angle_point(self.pts[l_chain[1]], self.pts[t.pts[i]], self.pts[l_chain[-1]], self.pts[r_chain[-1]])
                    if rp and self.is_on(l_chain[-1], r_chain[-1], rp):
                        cands.append(rp)
                if not cands:
                    nt = Triangle(t.pts[i], r_chain[-1], l_chain[-1])
                    self.triangles.add(nt)
                    if len(l_chain) == 2:
                        nt.neis[2] = l_neis[-1][0]
                        if nt.neis[2]:
                            nt.neis[2].neis[l_neis[-1][1]] = nt
                        l_neis.pop()
                        k = 0
                        l_chain.pop()
                    else:
                        nt.neis[0] = r_neis[-1][0]
                        if nt.neis[0]:
                            nt.neis[0].neis[r_neis[-1][1]] = nt
                        r_neis.pop()
                        k = 2
                        r_chain.pop()
                    remaining = deque(r_chain + l_chain[-1:0:-1])
                    self.triangulate_polygon(remaining)
                    for i in range(len(r_chain) - 1):
                        tttt = self.find_triangle(r_chain[i], r_chain[i + 1])
                        l = tttt.get_ind(r_chain[i])
                        tttt.neis[l] = r_neis[i][0]
                        if r_neis[i][0]:
                            r_neis[i][0].neis[r_neis[i][1]] = tttt
                    for i in range(len(l_chain) - 1):
                        tttt = self.find_triangle(l_chain[i + 1], r_chain[i])
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
                    for i in range(len(r_chain) - 1):
                        tttt = self.find_triangle(r_chain[i], r_chain[i + 1])
                        l = tttt.get_ind(r_chain[i])
                        tttt.neis[l] = r_neis[i][0]
                        if r_neis[i][0]:
                            r_neis[i][0].neis[r_neis[i][1]] = tttt
                    for i in range(len(l_chain) - 1):
                        tttt = self.find_triangle(l_chain[i + 1], r_chain[i])
                        l = tttt.get_ind(l_chain[i + 1])
                        tttt.neis[l] = l_neis[i][0]
                        if l_neis[i][0]:
                            l_neis[i][0].neis[l_neis[i][1]] = tttt
                return
            elif angle(self.pts[tt.pt(j + 1)], self.pts[tt.pts[j]], self.pts[tt.pt(j + 2)]) > 0 or angle(self.pts[tt.pts[j]], self.pts[tt.pt(j + 1)], self.pts[tt.pt(j + 2)]) > 0:
                self.triangulate_polygon(remaining)
                for i in range(len(r_chain) - 1):
                    tttt = self.find_triangle(r_chain[i], r_chain[i + 1])
                    l = tttt.get_ind(r_chain[i])
                    tttt.neis[l] = r_neis[i][0]
                    if r_neis[i][0]:
                        r_neis[i][0].neis[r_neis[i][1]] = tttt
                for i in range(len(l_chain) - 1):
                    tttt = self.find_triangle(l_chain[i + 1], r_chain[i])
                    l = tttt.get_ind(l_chain[i + 1])
                    tttt.neis[l] = l_neis[i][0]
                    if l_neis[i][0]:
                        l_neis[i][0].neis[l_neis[i][1]] = tttt
                self.make_non_obtuse(tt)
                return
        cands = []
        r_neis.append((tt, j))
        neis = r_neis + l_neis[::-1]
        chain = r_chain + l_chain[:0:-1]
        for i in range(-1, len(chain) - 1):
            cands.append(projection(self.pts[chain[i]], self.pts[chain[i - 1]], self.pts[chain[i + 1]]))
            for pp in intersections_of_orthogonals(self.pts[chain[i]], self.pts[chain[i - 1]], self.pts[chain[i]], self.pts[chain[i + 1]]):
                check = True
                for ii in range(len(chain)):
                    if turn(self.pts[chain[ii - 1]], self.pts[chain[ii]], pp) <= 0:
                        check = False
                        break
                if check:
                    cands.append(pp)
        for i in range(len(chain)):
            for ii in range(i + 2, len(chain)):
                if i == 0 and ii == len(chain) - 1:
                    continue
                for pp in intersections_of_orthogonals(self.pts[chain[i - 1]], self.pts[chain[i]], self.pts[chain[ii - 1]], self.pts[chain[ii]]):
                    check = True
                    for iii in range(len(chain)):
                        if turn(self.pts[chain[iii - 1]], self.pts[chain[iii]], pp) <= 0:
                            check = False
                            break
                    if check:
                        cands.append(pp)
                for pp in intersections_of_disks(midpoint(self.pts[chain[i - 1]], self.pts[chain[i]]), sqdist(self.pts[chain[i - 1]], self.pts[chain[i]]) / 4, midpoint(self.pts[chain[ii - 1]], self.pts[chain[ii]]), sqdist(self.pts[chain[ii - 1]], self.pts[chain[ii]]) / 4):
                    check = True
                    for iii in range(len(chain)):
                        if turn(self.pts[chain[iii - 1]], self.pts[chain[iii]], pp) <= 0:
                            check = False
                            break
                    if check:
                        cands.append(pp)
        bcands = []
        bscore = 0
        for pp in cands:
            score = 0
            for i in range(len(chain)):
                if angle(self.pts[i], self.pts[i - 1], pp) <= 0 and angle(self.pts[i - 1], self.pts[i], pp) <= 0 and angle(self.pts[i], pp, self.pts[i - 1]) <= 0:
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

    def insert_point_on(self, e1:int, e2:int, p:Point):
        if not self.is_on(e1, e2, p):
            raise Exception("point is not on the edge")
        self.pts.append(p)
        ind = len(self.pts) - 1
        inserted = False
        for i in range(len(self.region_boundary)):
            if (self.region_boundary[i - 1] == e1 and self.region_boundary[i] == e2) or (self.region_boundary[i] == e1 and self.region_boundary[i - 1] == e2):
                inserted = True
                break
        if inserted:
            self.region_boundary.insert(i, ind)
        else:
            for cons in self.constraints:
                if cons == (e1, e2) or cons == (e2, e1):
                    break
            self.constraints.add((cons[0], ind))
            self.constraints.add((cons[1], ind))
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

    def step(self):
        obtt = []
        for t in self.triangles:
            if self.is_obtuse(t):
                obtt.append(t)
        if not obtt:
            print("Done!")
        else:
            target = random.choice(obtt)
            self.print_triangle(target)
            self.make_non_obtuse(target)
            self.minmax_triangulate()

    def print_triangle(self, t:Triangle):
        print("Triangle :", end="")
        print(t)
        print(self.pts[t.pts[0]])
        print(self.pts[t.pts[1]])
        print(self.pts[t.pts[2]])
        print(t.neis[0])
        print(t.neis[1])
        print(t.neis[2])


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
        return [Point(p1.x, s * p1.x + b3), Point(p1.x, s * p1.x + b4), Point(p2.x, s * p2.x + b3), Point(p2.x, s * p2.x + b4)]
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
        return [Point(x13, s12 * x13 + b1), Point(x23, s12 * x23 + b2), Point(x14, s12 * x14 + b1), Point(x24, s12 * x24 + b2)]

def intersections_of_disks(p1:Point, r1:MyNum, p2:Point, r2:MyNum):
    if p1.y == p2.y:
        if p1.x == p2.x:
            return []
        qx = (p1.x + p2.x + (r2 - r1) / (p1.x - p2.x)) / 2
        sqrhs = r1 - (qx - p1.x) * (qx - p1.x)
        if sqrhs < 0:
            return []
        frhs = math.sqrt(sqrhs.toFloat())
        rhs1 = MyNum(int(frhs * IMP), IMP)
        rhs2 = MyNum(int(frhs * IMP) + 1, TMP)
        return [Point(qx, p1.y + rhs1), Point(qx, p1.y + rhs2), Point(qx, p1.y - rhs1), Point(qx, p1.y - rhs2)]
    s = (p2.x - p1.x) / (p1.y - p2.y)
    bb = (p1.x * p1.x + p1.y * p1.y - p2.x * p2.x - p2.y * p2.y - r1 + r2) / (p1.y - p2.y) / 2
    a = s * s + 1
    b = 2 * (-p1.x + s * (bb - p1.y))
    c = p1.x * p1.x + (bb - p1.y) * (bb - p1.y) - r1
    inroot = b * b - a * c * 4
    if inroot < 0:
        return []
    db24ac = math.sqrt(inroot.toFloat())
    root1 = MyNum(int(db24ac * IMP), IMP)
    root2 = MyNum(int(db24ac * IMP) + 1, IMP)
    x1 = (-b + root1) / a / 2
    x2 = (-b + root2) / a / 2
    x3 = (-b - root1) / a / 2
    x4 = (-b - root2) / a / 2
    return [Point(x, s * x + bb) for x in [x1, x2, x3, x4]]