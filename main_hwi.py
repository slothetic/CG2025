import MyNum
from data import *
import os
import sys
import pdb 
import faulthandler; faulthandler.enable()
import shapely

sys.setrecursionlimit(100000)

def computeEdges(dt : Data):

    for t in dt.triangles:
        # 어차피 대칭이므로
        # 한 쪽에 대해서만 생각하면 됨 - (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1) 다 고려할 필요 없이
        # (0, 1), (1, 2), (2, 0)에 대해서만 돌리기
        for i in len(t.pts):
            v1 = t.pts[i]
            v2 = t.pts[i+1 % 3]
        
        isConstrained = [v1.id, v2.id] in dt.constraints or [v2.id, v1.id] in dt.constraints

        v1.incidentPoints.append([v2, isConstrained])
        v2.incidentPoints.append([v1, isConstrained])

def data2Graph():
    pass

# checks if all edges of the given point are non-constrained
def isAllEdgesNonConstrained(p : Point) -> bool:
    for neighbor in p.incidentPoints:
        # if any neighbor is constrained
        if neighbor[1] == True:
            return False

    return True

def findAnyObtuseTriangle(dt : Data):
    for t in dt.triangles:
        if (dt.is_obtuse(t)):
            return t

    return None


def findPathToBoundary(dt : Data):

    t = findAnyObtuseTriangle(dt)

    oT = None # oT stands for opposingTriangle

    len01 = sqdist1(t.pts[0], t.pts[1])
    len12 = sqdist1(t.pts[1], t.pts[2])
    len20 = sqdist1(t.pts[2], t.pts[0])

    aHV = None # aHV stands for antiHypotenuseVertex
    hV1 = None # hypotenuseVertex1
    hV2 = None # hypotenuseVertex2

    if len01 > len12 and len01 > len20:
        # pts[0]pts[1] is the hypotenuse
        aHV = t.pts[2]; hV1 = t.pts[0]; hV2 = t.pts[1]; # oT = nei

    elif len12 > len01 and len12 > len20:
        aHV = t.pts[0]; hV1 = t.pts[1], hV2 = t.pts[2]; # oT =

    elif len20 > len01 and len20 > len12:
        aHV = t.pts[1]; hV1 = t.pts[2], hV2 = t.pts[0]; # oT =

    else:
        raise "In an obtuse triangle, there must exist an edge (hypotenuse) whose length is larger than the two other edges"

    while t is not None:
        # a로부터 b 위에 수선을 내림. 현재 삼각형 t는 t1과 t2로 나누어짐
        proj = projection(aHV, hV1, hV2)
        dt.add_steiner(proj)



        # 맞닿아 있는 삼각형 역시 obtuse면 거기서 멈춤

    # while ()
    # boundary edge인지 아닌지 판단

    return "끝"

def moveSteinerPoint(dt : Data, instanceName : str):
    
    obtuseTriangles = []

    # compute obtuse triangles
    for t in dt.triangles:
        if (dt.is_obtuse(t)):
            obtuseTriangles.append(t)

    # for each obtuse triangle,
    for t in obtuseTriangles:
        # for each vertex
        for v in t.pts:
            # if all its incident edges are non-constrained, we may move the vertex
            if isAllEdgesNonConstrained(v):

                v.x
                v.y

                # again compute the slab


                return 

    # pick 

    # find a good direction
    pass

# 
if __name__=="__main__":

    argument = sys.argv
    if len(argument)>=2:
        inp = argument[1]

    else:
        raise "error"
        # inp = "example_instances/cgshop2025_examples_ortho_10_ff68423e.instance.json"

    print(inp) # instance 이름 출력

    dt = Data(inp) # data 받아 오기

    dt.triangulate()
    
    dt.delaunay_triangulate()

    dt.WriteData() # 어디 저장?
    # Configure Display Langage

    print(inp)

    # ko(한국어)가 있으면 선택해주면 됩니다. ko가 없다면 Install Additional Languages…를 선택합니다.

    # 오른쪽 사이드바에 언어팩 카테고리의 확장 목록이 나타납니다.

    # 한국어를 선택하거나, 리스트가 많아서 한국어가 보이지 않는다면 검색 쿼리에 Korean을 추가합니다. 한국어 언어팩의 Install 버튼을 클릭합니다.

    # 설치가 끝나면 오른쪽 아래에 언어 변경에 대한 팝업이 나타납니다. 방금 설치한 언어(한국어)로 변경하려면 Change Language and Restart 버튼을 클릭합니다.

    # 파일 -> 기본 설정 -> 테마 -> 색 테마

    '''
    print(inp)
    numIterations = 10
    for __ in range(numIterations):
        dt = Data(inp)

        # (1-1) (Delaunay) triangulate the instance
        dt.triangulate()
        
        # (1-2) write data
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

        else:

            none_obtuse_iter(dt)
    '''
            
    # 어쨌든 none_obtuse_iter - make_non_obtuse_boundary가 메인 로직이네

# square dist (L2 제곱) 계산하는 함수
def sqdist1(px, py, qx, qy):
    xd = px-qx
    yd = py-qy
    return xd * xd + yd * yd

# 오케이 dt가 데이터 
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

# 
def none_obtuse_iter(dt:Data, lim=50):
    global best_dt
    global total_num
    global __

    dt.triangles = set()
    dt.triangulate()
    dt.DrawPoint() # solution_point 형식으로 출력.
    dt.delaunay_triangulate()
    dt.WriteData()
    dt.DrawResult()

    cnt = 0

    dt.make_non_obtuse_boundary()
    n_obs = 0 # number of obtuse triangles

    # obtuse triangle
    for t in dt.triangles:
        if dt.is_obtuse(t):
            n_obs += 1
            
    score = dt.score()

    maxcnt = 100

    # $ git stash
    # $ git checkout other-branch
    # $ git stash pop
    # 
    # 

    dt.DrawResult("best")
    dt.WriteData("best")

    while True:  

        if cnt>=maxcnt: # if the maximum number of iterations is exceeded, then finish the procedure
            break

        # dt.fp_ind는 전체 point 개수
        # 결국 좌변이 의미하는 것이 추가한 Steiner point의 개수?
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
        dt.make_non_obtuse_boundary()
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
