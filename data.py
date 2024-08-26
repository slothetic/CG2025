from MyNum import MyNum
import json
import cv2
import numpy as np
import random
import re

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, p):
        if self.x==p.x and self.y==p.y:
            return True
        return False
    
    def __str__(self):
        return "("+str(self.x)+", "+str(self.y)+")"
    
    def __ne__(self, p):
        if self.x==p.x and self.y==p.y:
            return False
        return True
class Triangle:
    def __init__(self, p1, p2, p3):
        self.p = [p1, p2, p3]
    
class Data:
    def __init__(self, input):
        self.input = input
        self.triangles = []
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
            self.region_boundary = root["region_boundary"]
            self.num_constraints =  root["num_constraints"]
            self.constraints = root["additional_constraints"]
        self.triangles.append(Triangle(0,1,2))

    def WriteData(self):
        print("--------------------WriteData--------------------")
        inst = dict()
        inst["content_type"]="CG_SHOP_2025_Solution"
        inst["instance_uid"]=self.instance_name
        inst["steiner_points_x"] =  list(p.x for p in self.pts[self.fp_ind:])
        inst["steiner_points_y"] =  list(p.y for p in self.pts[self.fp_ind:])
        const_edges = []
        for e in self.constraints:
            const_edges.append(sorted(e))
        for i in range(1,len(self.region_boundary)):
            const_edges.append(sorted([self.region_boundary[i-1],self.region_boundary[i]]))
        const_edges.append(sorted([self.region_boundary[-1],self.region_boundary[0]]))
        int_edges = []
        for t in self.triangles:
            e1 = sorted([t.p[0],t.p[1]])
            e2 = sorted([t.p[0],t.p[2]])
            e3 = sorted([t.p[1],t.p[2]])
            if e1 not in const_edges and e1 not in int_edges:
                int_edges.append(e1)
            if e2 not in const_edges and e2 not in int_edges:
                int_edges.append(e2)
            if e3 not in const_edges and e3 not in int_edges:
                int_edges.append(e3)

        inst["edges"] = int_edges 
        def jsonIndentLimit(jsonString, indent, limit):
            regexPattern = re.compile(f'\n({indent}){{{limit}}}(({indent})+|(?=(}}|])))')
            return regexPattern.sub('', jsonString)
        with open("solutions/" + self.instance_name + ".solution.json", "w", encoding="utf-8") as f:
            json.dump(inst, f, indent='\t')


    def DrawResult(self):
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
        for t in self.triangles:
            pts = np.array([[minw+int(rad*self.pts[t.p[0]].x), minh-int(rad*self.pts[t.p[0]].y)],[minw+int(rad*self.pts[t.p[1]].x), minh-int(rad*self.pts[t.p[1]].y)],[minw+int(rad*self.pts[t.p[2]].x), minh-int(rad*self.pts[t.p[2]].y)]], dtype=np.int32).reshape(1,-1,2)
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
            e1 = sorted([t.p[0],t.p[1]])
            e2 = sorted([t.p[0],t.p[2]])
            e3 = sorted([t.p[1],t.p[2]])
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
        cv2.imwrite("solutions/"+self.instance_name+".solution_check.png", img)

def angle(p1:Point, p2:Point, p3:Point):
    if p1==p2:
        raise Exception("Cannot Calculate Angle")
    if p2==p3:
        raise Exception("Cannot Calculate Angle")
    p12x = MyNum(p2.x-p1.x)
    p12y = MyNum(p2.y-p1.y)
    p23x = MyNum(p2.x-p3.x)
    p23y = MyNum(p2.y-p3.y)
    ab = p12x * p23x + p12y * p23y
    a = p12x * p12x + p12y * p12y
    b = p23x * p23x + p23y * p23y

def turn(p1:Point, p2:Point, p3:Point):
    return (p2.x - p1.x) * (p3.y - p1.y) - (p2.y - p1.y) * (p3.x - p1.x)

