import MyNum
from data import *
import os
import sys
import pdb 
import faulthandler; faulthandler.enable()
import shapely
import macro

from pathlib import Path

from cgshop2025_pyutils import (
    DelaunayBasedSolver,
    InstanceDatabase,
    ZipSolutionIterator,
    ZipWriter,
    verify, Cgshop2025Solution,
)

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

def getAnyObtuseTriangle(dt : Data):

    for t in dt.triangles:
        if t.used == True:
            if dt.is_obtuse(t):
                return t
    '''
    for n, t in enumerate(dt.triangles):
        if t.used == True:
            if dt.is_obtuse(t):
                return n, t
    '''

    print('There is no obtuse triangle in the triangulation.')
    return None

'''
# 3개의 vertex id가 주어졌을 때, 해당하는 triangle의 리스트 dt.triangles 상에서의 index 찾기
def getTriangleID(dt : Data, v_id1 : int, v_id2 : int, v_id3 : int): # vID stands for vertexID

    # for n, i in enumerate(dt.triangles):

    for n, t in enumerate(dt.triangles):
        if v_id1 in t.pts:
            if v_id2 in t.pts:
                if v_id3 in t.pts:
                    return n

    print('No matching triangle found.')
    return None
'''

'''
# triangle.pts 인덱스 (0, 1 혹은 2) 가 주어졌을 때,
# 해당 point의 맞은편 edge를 기준으로 맞닿아있는 nei의 인덱스를 반환
def getOppositeNeiID(ptID):
    return (ptID + 1) % 3
'''

# square dist (L2 제곱) 계산하는 함수
def sqdist1(px, py, qx, qy):
    xd = px-qx
    yd = py-qy
    return xd * xd + yd * yd

# 실제 각도를 반환
def printObtuse(p: Point, q: Point, r: Point):
    # print('printObtuse start')

    print(float(angle(p, q, r)))
    print(float(angle(q, r, p)))
    print(float(angle(r, p, q)))

    # print('printObtuse end')

# printObtuse와 마찬가지로, 세 점이 입력임.
def isObtuse(p: Point, q: Point, r: Point):

    if angle(p, q, r) > MyNum(0): return True
    if angle(q, r, p) > MyNum(0): return True
    if angle(r, p, q) > MyNum(0): return True

    return False

def printCurrentTriangles(dt : Data):
    print('--current triangles--')

    for t in dt.triangles:
        print(sorted(t.pts), end = ' ')

def removeTriangle(dt : Data, t : Triangle):

    # printCurrentTriangles(dt)
    try:
        dt.triangles.remove(t)

    except:
        print('remove triangle with points', sorted(t.pts))

        print('do we have it?')
        for temp_t in dt.triangles:
            if sorted(temp_t.pts) == sorted(t.pts):
                print('Yes')

                print('do we have the right neis?')

                temp_t.printNeis(dt.pts, 'temp_t.neis')
                t.printNeis(dt.pts, 't.neis')

            else:
                print('No')

        # print('neis of ')

    # print('current number of triangles:', len(dt.triangles))

def isAllNeisValid(dt : Data):

    # nei 관계에 있는 모든 triangle pair에 대해
    for t1 in dt.triangles:
        for t2 in dt.triangles:
            
            if t2 in t1.neis:
                # 한 변, 즉 두 꼭짓점을 공유하는지 확인
                if not len(set(t1.pts).intersection(set(t2.pts))) == 2:
                    print('t1.pts:',sorted(t1.pts))
                    print('t2.pts:', sorted(t2.pts))
                    raise "error occurred during isAllNeisValid, size of intersection is not 2"

    print("All Neis Valid!")


def addTriangle(dt : Data, t : Triangle):
    dt.triangles.add(t)
    # print('added triangle with points', t.pts)

    # print('neis:', end = ' ')
    # t.printNeis(dt.pts)

    # print('isObtuse:', dt.is_obtuse(t))

    # print('and with neis:', t.printNeis(dt.pts))
    '''
    , 'and neis (represented by points)')
    for nei in t.neis:
        if nei == None:
            print('None', sep=' ')
        else:
            print(sorted(nei.pts), sep=' ')
    '''
    # printCurrentTriangles(dt)
    # print('current number of triangles:', len(dt.triangles))


def findPathToBoundary(dt : Data):

    '''
    L = list(dt.triangles)
    print(len(L))

    for i in range(len(L)):
        print(sorted(L[i].pts))

    for i in range(len(L)):
        for j in range(i+1, len(L)):
            if sorted(L[i].pts) == sorted(L[j].pts):
                raise "duplicated vertices!!"
    '''

    # indicates the current iteration number
    # 하나의 Steiner chain이 boundary에 도달해서, 새로운 obtuse triangle을 잡는 경우뿐만 아니라
    # Steiner chain 매 step 끝날 때도 iterNum을 1씩 증가시킴 (WriteData 시 삼각형 위에 iterNum을 표시하기 위해)
    iterNum = 0
    # maxIter =

    while True:

        t = getAnyObtuseTriangle(dt)
        if t is None:
            print('No triangle selected, end with iterNum', iterNum)
            return
        else:
            # print('triangle #', _, 'selected')
            print('triangle selected, pts:', t.pts)

        while True:

            isAllNeisValid(dt)

            if iterNum > macro.maxIter:
                print('iterNum exceeded', macro.maxIter, ', we stop here.')

                numObtuseTriangles = 0
                for t in dt.triangles:
                    if dt.is_obtuse(t):
                        numObtuseTriangles += 1
                print('Number of obtuse triangles:', numObtuseTriangles)

                return

            # initialize SteinerChainMark
            dt.emptySteinerChainMark()

            '''
            numTrianglesTasNei = 0
            for temp_t in dt.triangles:

                if t in temp_t.neis:
                    print(temp_t.pts, t.pts)
                    numTrianglesTasNei += 1
            print('numTrianglesTasNei:', numTrianglesTasNei)
            '''

            oT = None # oT stands for opposingTriangle

            # len01 = sqdist1(t.pts[0].x, t.pts[0].y, t.pts[1].x, t.pts[1].y)
            # len12 = sqdist1(t.pts[1].x, t.pts[1].y, t.pts[2].x, t.pts[2].y)
            # len20 = sqdist1(t.pts[2].x, t.pts[2].y, t.pts[0].x, t.pts[0].y)

            len01 = sqdist(dt.pts[t.pts[0]], dt.pts[t.pts[1]]); # print('len01 dist: ', len01)
            len12 = sqdist(dt.pts[t.pts[1]], dt.pts[t.pts[2]]); # print('len12 dist: ', len12)
            len20 = sqdist(dt.pts[t.pts[2]], dt.pts[t.pts[0]]); # print('len20 dist: ', len20)

            aHV = None; aHVtID = None # aHV stands for antiHypotenuseVertex
            hV1 = None; hV1tID = None # hypotenuseVertex1
            hV2 = None; hV2tID = None # hypotenuseVertex2

            # oT may be None

            # aHVid, hV1id, hV2id라고 표현했지만,
            # 사실 aHV, hV1, hV2 역시 모두 index임

            # dt.pts[hV1]dt.pts[hV2] is the hypotenuse
            if len01 > len12 and len01 > len20:
                aHV = t.pts[2]; hV1 = t.pts[0]; hV2 = t.pts[1]; oT = t.neis[0]
                aHVtID = 2; hV1tID = 0; hV2tID = 1

            # dt.pts[hV1]dt.pts[hV2] is the hypotenuse
            elif len12 > len01 and len12 > len20:
                aHV = t.pts[0]; hV1 = t.pts[1]; hV2 = t.pts[2]; oT = t.neis[1]
                aHVtID = 0; hV1tID = 1; hV2tID = 2

            # dt.pts[hV1]dt.pts[hV2] is the hypotenuse
            elif len20 > len01 and len20 > len12:
                aHV = t.pts[1]; hV1 = t.pts[2]; hV2 = t.pts[0]; oT = t.neis[2]
                aHVtID = 1; hV1tID = 2; hV2tID = 0

            else:
                raise "In an obtuse triangle, there must exist an edge (hypotenuse) whose length is larger than the two other edges."

            proj = projection(dt.pts[aHV], dt.pts[hV1], dt.pts[hV2])
            projID = dt.addSteinerNoTriangulation(proj)

            # print('hV1:', hV1, 'hV2:', hV2)

            # 새로 추가한 Steiner point가 boundary 위에 있다면,
            # (1) 기존 triangle (t) 을 지우고,
            # (2) 새로운 두 triangle (newT1, newT2) 을 더하고, pts 및 neis 정보를 업데이트한 뒤 함수 종료
            if oT is None:

                print('oT is None, iterNum:', iterNum)

                # triangle 정보 복사

                newT1 = t.copy()
                newT2 = t.copy()

                # newT1 = copy.deepcopy(t)
                # newT2 = copy.deepcopy(t)

                # pts 정보 수정

                newT1.pts[hV2tID] = projID
                newT2.pts[hV1tID] = projID

                # neis 정보 수정 (neis의 각 원소는 triangle index (int형) 가 아니라 triangle 객체임)

                # newT1.printNeis(dt.pts, 'newT1, before change')
                newT1.neis[newT1.getOppositeNeiID(hV1tID)] = newT2
                # newT1.printNeis(dt.pts, 'newT1, after change')

                # newT2.printNeis(dt.pts, 'newT2, before change')
                newT2.neis[newT2.getOppositeNeiID(hV2tID)] = newT1
                # newT2.printNeis(dt.pts, 'newT2, after change')

                aHV_hV1_t = t.neis[t.getOppositeNeiID(hV2tID)] # aHV와 hV1를 잇는 직선을 t와 공유 (했던) triangle
                if aHV_hV1_t is not None:
                    for k in range(len(aHV_hV1_t.neis)):
                        if aHV_hV1_t.neis[k] == t:
                            # print('nei of aHV_hV1_t changed from t:', t.pts, 'to newT1', newT1.pts)
                            aHV_hV1_t.neis[k] = newT1

                aHV_hV2_t = t.neis[t.getOppositeNeiID(hV1tID)] # aHV와 hV2를 잇는 직선을 t와 공유 (했던) triangle
                if aHV_hV2_t is not None:
                    for k in range(len(aHV_hV2_t.neis)):
                        if aHV_hV2_t.neis[k] == t:
                            # print('nei of aHV_hV2_t changed from t:', t.pts, 'to newT2', newT2.pts)
                            aHV_hV2_t.neis[k] = newT2

                '''
                aHV_hV1_t = t.neis[t.getOppositeNeiID(hV2tID)] # aHV와 hV1를 잇는 직선을 t와 공유 (했던) triangle
                for k in range(len(aHV_hV1_t.neis)):
                    if aHV_hV1_t.neis[k] == t:
                        print('nei of aHV_hV1_t changed from t:', t.pts, 'to newT1', newT1.pts)
                        aHV_hV1_t.neis[k] = newT1

                aHV_hV2_t = t.neis[t.getOppositeNeiID(hV1tID)] # aHV와 hV2를 잇는 직선을 t와 공유 (했던) triangle
                for k in range(len(aHV_hV2_t.neis)):
                    if aHV_hV2_t.neis[k] == t:
                        print('nei of aHV_hV2_t changed from t:', t.pts, 'to newT2', newT2.pts)
                        aHV_hV2_t.neis[k] = newT2
                '''

                # 최종적으로, triangles 삽입 및 삭제

                '''
                numTrianglesTasNei = 0
                for temp_t in dt.triangles:
                    if t in temp_t.neis:
                        print(temp_t.pts, t.pts)
                        numTrianglesTasNei += 1
                print('numTrianglesTasNei:', numTrianglesTasNei)
                '''

                removeTriangle(dt, t)

                addTriangle(dt, newT1)
                addTriangle(dt, newT2)

                dt.addSteinerChainMark(newT1, 'T1')
                dt.addSteinerChainMark(newT2, 'T2')

                # iterNum 올리고 결과 출력
                iterNum += 1
                dt.DrawResult('step' + str(iterNum), macro.folder + '/' + nick)

                '''
                print('printObtuse hV1-projID-aHV'); printObtuse(dt.pts[hV1], dt.pts[projID], dt.pts[aHV])
                print('is_obtuse hV1-projID-aHV', isObtuse(dt.pts[hV1], dt.pts[projID], dt.pts[aHV]))
                print(newT1.pts, hV1, projID, aHV)
                print()

                print('printObtuse hV2-projID-aHV'); printObtuse(dt.pts[hV2], dt.pts[projID], dt.pts[aHV])
                print('is_obtuse hV2-projID-aHV', isObtuse(dt.pts[hV2], dt.pts[projID], dt.pts[aHV]))
                print(newT2.pts, hV2, projID, aHV)
                print()
                '''

                break

            else:
                '''
                print('t.pts:', t.pts)
                print('oT.pts:', oT.pts)
                print('t == oT ?', t == oT)
                '''

                print('oT is not None, iterNum:', iterNum)

                # triangle 정보 복사

                newT1 = t.copy()
                newT2 = t.copy()

                newOT1 = oT.copy()
                newOT2 = oT.copy()

                # newT1 = copy.deepcopy(t)
                # newT2 = copy.deepcopy(t)

                # newOT1 = copy.deepcopy(oT)
                # newOT2 = copy.deepcopy(oT)

                # pts 정보 수정

                newT1.pts[hV2tID] = projID # 이러면서 t까지, oT까지 바뀐다고?
                newT2.pts[hV1tID] = projID

                hV1otID = oT.get_ind(hV1)
                hV2otID = oT.get_ind(hV2)

                    # newOT1.pts = [hV1, thirdVid, projID]
                newOT1.pts[hV2otID] = projID
                    # newOT2.pts = [hV2, thirdVid, projID]
                newOT2.pts[hV1otID] = projID

                # neis 정보 수정 (neis의 각 원소는 triangle index (int형) 가 아니라 triangle 객체임)

                # triangle(neis)

                # print('newT1.pts:', newT1.pts)
                # newT1.printNeis(dt.pts, 'newT1, before change')
                newT1.neis[newT1.getOppositeNeiID(hV1tID)] = newT2
                # newT1.printNeis(dt.pts, 'newT1, after change')

                # print('newT2.pts:', newT2.pts)
                # newT2.printNeis(dt.pts, 'newT2, before change')
                newT2.neis[newT2.getOppositeNeiID(hV2tID)] = newT1
                # newT2.printNeis(dt.pts, 'newT2, after change')

                # print('newOT1.pts:', newOT1.pts)
                # newOT1.printNeis(dt.pts, 'newOT1, before change')
                newOT1.neis[newOT1.getOppositeNeiID(hV1otID)] = newOT2
                # newOT1.printNeis(dt.pts, 'newOT1, after change')

                # print('newOT2.pts:', newOT2.pts)
                # newOT2.printNeis(dt.pts, 'newOT2, before change')
                newOT2.neis[newOT2.getOppositeNeiID(hV2otID)] = newOT1
                # newOT2.printNeis(dt.pts, 'newOT2, after change')

                # newOT1.neis[Triangle.getOppositeNeiID(hV1otID)] = newOT2
                # newOT2.neis[Triangle.getOppositeNeiID(hV2otID)] = newOT1

                aHV_hV1_t = t.neis[t.getOppositeNeiID(hV2tID)] # aHV와 hV1를 잇는 직선을 t와 공유 (했던) triangle
                if aHV_hV1_t is not None:
                    for k in range(len(aHV_hV1_t.neis)):
                        if aHV_hV1_t.neis[k] == t:
                            # print('nei of aHV_hV1_t changed from t:', t.pts, 'to newT1', newT1.pts)
                            aHV_hV1_t.neis[k] = newT1

                aHV_hV2_t = t.neis[t.getOppositeNeiID(hV1tID)] # aHV와 hV2를 잇는 직선을 t와 공유 (했던) triangle
                if aHV_hV2_t is not None:
                    for k in range(len(aHV_hV2_t.neis)):
                        if aHV_hV2_t.neis[k] == t:
                            # print('nei of aHV_hV2_t changed from t:', t.pts, 'to newT2', newT2.pts)
                            aHV_hV2_t.neis[k] = newT2

                # print('newT1.pts:', newT1.pts)
                # newT1.printNeis(dt.pts, 'newT1, before change')
                newT1.neis[newT1.getNeiID(hV1, projID)] = newOT1
                # newT1.printNeis(dt.pts, 'newT1, after change')

                # print('newOT1.pts:', newOT1.pts)
                # newOT1.printNeis(dt.pts, 'newOT1, before change')
                newOT1.neis[newOT1.getNeiID(hV1, projID)] = newT1
                # newOT1.printNeis(dt.pts, 'newOT1, after change')

                # print('newT2.pts:', newT2.pts)
                # newT2.printNeis(dt.pts, 'newT2, before change')
                newT2.neis[newT2.getNeiID(hV2, projID)] = newOT2
                # newT2.printNeis(dt.pts, 'newT2, after change')

                # print('newOT2.pts:', newOT2.pts)
                # newOT2.printNeis(dt.pts, 'newOT2, before change')
                newOT2.neis[newOT2.getNeiID(hV2, projID)] = newT2
                # newOT2.printNeis(dt.pts, 'newOT2, after change')

                # newT1.neis[newT1.getNeiID(dt.pts[hV1], dt.pts[projID])] = newOT1
                # newOT1.neis[newOT1.getNeiID(dt.pts[hV1], dt.pts[projID])] = newT1
                # newT2.neis[newT2.getNeiID(dt.pts[hV2], dt.pts[projID])] = newOT2
                # newOT2.neis[newOT2.getNeiID(dt.pts[hV2], dt.pts[projID])] = newT2

                hV1_third_oT = oT.neis[oT.getOppositeNeiID(hV2otID)]
                if hV1_third_oT is not None:
                    for k in range(len(hV1_third_oT.neis)):
                        if hV1_third_oT.neis[k] == oT:
                            # print('nei of hV1_third_oT changed from oT:', oT.pts, 'to newOT1', newOT1.pts)
                            # print('nei of hV1_third_oT changed from oT to newOT1')
                            hV1_third_oT.neis[k] = newOT1

                hV2_third_oT = oT.neis[oT.getOppositeNeiID(hV1otID)]
                if hV2_third_oT is not None:
                    for k in range(len(hV2_third_oT.neis)):
                        if hV2_third_oT.neis[k] == oT:
                            # print('nei of hV2_third_oT changed from oT:', oT.pts, 'to newOT2', newOT2.pts)
                            # print('nei of hV2_third_oT changed from oT to newOT2')
                            hV2_third_oT.neis[k] = newOT2

                # 최종적으로, triangles 삽입 및 삭제

                #print('t.pts:', t.pts)
                #print('oT.pts:', oT.pts)
                #print('t == oT ?', t == oT)

                if t == oT:
                    raise "t cannot be same as oT"

                '''
                numTrianglesTasNei = 0
                for temp_t in dt.triangles:
                    if t in temp_t.neis:
                        print(temp_t.pts, t.pts)
                        numTrianglesTasNei += 1
                print('numTrianglesTasNei:', numTrianglesTasNei)
                '''

                removeTriangle(dt, t)

                addTriangle(dt, newT1)
                addTriangle(dt, newT2)

                removeTriangle(dt, oT)

                addTriangle(dt, newOT1)
                addTriangle(dt, newOT2)

                # triangle 업데이트 (반복문 다음 step을 위해)

                thirdVid = oT.getThirdVertexID(hV1, hV2)

                # print('angle hV1-projID-aHV', angle(dt.pts[hV1], dt.pts[projID], dt.pts[aHV]))
                # print('angle hV2-projID-aHV', angle(dt.pts[hV2], dt.pts[projID], dt.pts[aHV]))

                '''
                print('printObtuse hV1-projID-aHV'); printObtuse(dt.pts[hV1], dt.pts[projID], dt.pts[aHV])
                print('is_obtuse hV1-projID-aHV', isObtuse(dt.pts[hV1], dt.pts[projID], dt.pts[aHV]))
                print(newT1.pts, hV1, projID, aHV)
                print()

                print('printObtuse hV2-projID-aHV'); printObtuse(dt.pts[hV2], dt.pts[projID], dt.pts[aHV])
                print('is_obtuse hV2-projID-aHV', isObtuse(dt.pts[hV2], dt.pts[projID], dt.pts[aHV]))
                print(newT2.pts, hV2, projID, aHV)
                print()

                print('printObtuse hV1-projID-thirdVid'); printObtuse(dt.pts[hV1], dt.pts[projID], dt.pts[thirdVid])
                print('is_obtuse hV1-projID-thirdVid', isObtuse(dt.pts[hV1], dt.pts[projID], dt.pts[thirdVid]))
                print(newOT1.pts, hV1, projID, thirdVid)
                print()

                print('printObtuse hV2-projID-thirdVid'); printObtuse(dt.pts[hV2], dt.pts[projID], dt.pts[thirdVid])
                print('is_obtuse hV2-projID-thirdVid', isObtuse(dt.pts[hV2], dt.pts[projID], dt.pts[thirdVid]))
                print(newOT2.pts, hV2, projID, thirdVid)
                print()
                '''

                if angle(dt.pts[thirdVid], dt.pts[projID], dt.pts[hV1]) > MyNum(0):
                    t = newOT1

                    dt.addSteinerChainMark(newT1, 'T1')
                    dt.addSteinerChainMark(newT2, 'T2')

                    dt.addSteinerChainMark(newOT1, 'OT1N')
                    dt.addSteinerChainMark(newOT2, 'OT2')

                elif angle(dt.pts[thirdVid], dt.pts[projID], dt.pts[hV2]) > MyNum(0):
                    t = newOT2

                    dt.addSteinerChainMark(newT1, 'T1')
                    dt.addSteinerChainMark(newT2, 'T2')

                    dt.addSteinerChainMark(newOT1, 'OT1')
                    dt.addSteinerChainMark(newOT2, 'OT2N')
                # very unlikely, but when both newOT1 and newOT2 are non-obtuse, quit the program.
                else:
                    # print()
                    # We are done.
                    # they are right triangles
                    raise 'error occurred. Both newOT1 and newOT2 are non-obtuse.'

                # iterNum 올리고 결과 출력
                iterNum += 1
                dt.DrawResult('step' + str(iterNum), macro.folder + '/' + nick)

                '''
                if dt.is_obtuse(newOT1):
                    t = newOT1
                elif dt.is_obtuse(newOT2):
                    t = newOT2
                # very unlikely, but when both newOT1 and newOT2 are non-obtuse, quit the program.
                else:
                    print('Both newOT1 and newOT2 are non-obtuse (they are right triangles). We are done.')
                    break
                '''

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

# filePath ex) test_dir/ortho_10_d2723dcc.solution.json
def sol2verifySol(filePath):
    # json.load()
    # print(filePath)

    dt = Data(filePath)

    # 원래 점이 7개고, Steiner point가 3개 있으면,
    # Steiner point들의 index는 7, 8, 9

    # Steiner point, x coordinates
    xs = []
    # Steiner point, y coordinates
    ys = []

    for i in range(dt.fp_ind, len(dt.pts)):
        p = dt.pts[i]
        xs.append(p.x)
        ys.append(p.y)

    with open(filePath, "r", encoding="utf-8") as f:
        root = json.load(f)
        _edges = root["edges"]

    return Cgshop2025Solution(
        instance_uid=instance.instance_uid,

        steiner_points_x=root["steiner_points_x"],
        steiner_points_y=root["steiner_points_y"],
        edges=root["edges"],
        # steiner_points_x=xs,
        # steiner_points_y=ys,
        # edges=_edges,
    )

#
if __name__=="__main__":

    '''
    # Load the instances from the example_instances folder. Instead of referring to the folder,
    # you can also give a path to a zip file.

    # idb = InstanceDatabase("example_instances/")
    # idb = InstanceDatabase("challenge_instances_cgshop25/")
    # idb = InstanceDatabase("challenge_instances_cgshop25_hwi_temp/")
    idb = InstanceDatabase("test_dir/")

    # If the solution zip file already exists, delete it
    if Path("example_solutions.zip").exists():
        Path("example_solutions.zip").unlink()

    numIters = 0
    # Compute solutions for all instances using the provided (naive) solver
    solutions = []
    for instance in idb:
        # numIters += 1
        # print(numIters, instance.instance_uid)

        solutionPath = macro.folder + '/' + instance.instance_uid + '/' + instance.instance_uid + '.solution.json'
        print(solutionPath)

        verifySol = sol2verifySol(solutionPath)

        # 실제 json 형식이랑 같은지 아닌지 확인하자.
        # solver = DelaunayBasedSolver(instance)
        # solution = solver.solve()
        solutions.append(verifySol)

    # Write the solutions to a new zip file
    with ZipWriter("example_solutions.zip") as zw:
        for solution in solutions:
            zw.add_solution(solution)

    # Verify the solutions
    for solution in ZipSolutionIterator("example_solutions.zip"):
        instance = idb[solution.instance_uid]
        result = verify(instance, solution)
        print(f"{solution.instance_uid}: {result}")
        assert not result.errors, "Expect no errors."

    exit()
    '''

    '''
    B = bool(input('give me a bool:'))
    print(B)
    B = bool(input('give me a bool:'))
    print(B)
    exit()
    '''

    '''
    L = 'abc.solution.json'
    print(L[len(L)-13:])
    print(L[:len(L)-13])
    exit()
    '''

    argument = sys.argv

    if len(argument) == 3:

        # ex) ortho_10_d2723dcc, ortho_20_5a9e8244
        nick = argument[1]

        if argument[2] == 'T':
            startFromSolution = True
        else:
            startFromSolution = False

        # ex) hwi_instances/ortho_10_d2723dcc
        realFolder = macro.folder + '/' + nick

        # ex) hwi_instances/ortho_10_d2723dcc/ortho_10_d2723dcc.instance.json
        instanceJson = realFolder + '/' + nick + '.instance.json'
        solutionJson = realFolder + '/' + nick + '.solution.json'
        solution = realFolder + '/' + nick + '.solution'

        '''
        # json으로 끝나면 그대로 두기
        if nick[:9] == 'challenge':
            pass
        else:
            inp = macro.folder + nick

        if inp[len(inp)-13:] == 'instance.json':
            inpInstanceJson = nick
        elif inp[len(inp)-13:] == 'solution.json':
            inpSolutionJson = nick
            inp = inp[:len(inp)-13]
            startFromSolution = True
        else:
            # ex) ends with 'd2723dcc'
            inpInstanceJson = nick + ".instance.json"
        '''

    else:
        # nick = "hwi_instances/ortho_10_d2723dcc"
        # inpInstanceJson = "hwi_instances/ortho_10_d2723dcc.instance.json"

        raise "error, instance nickname is invalid."

    # print(inp) # instance 이름 출력

    if startFromSolution:
        dt = Data(solutionJson)
    else:
        dt = Data(instanceJson, RDflag = True) # data 받아 오기

    # findPathToBoundary로 생성된 step 파일 모두 지우기
    for i in range(1, macro.maxIter):
        #
        filePath = solution + '_step' + str(i) + '.png'
        if os.path.exists(filePath):
            os.remove(filePath)

    if not startFromSolution:
        dt.triangulate()
        dt.delaunay_triangulate()

    findPathToBoundary(dt)

    dt.WriteData()

    dt.DrawResult()

    '''
    dt.triangulate()
    
    dt.delaunay_triangulate()

    dt.WriteData() # 어디 저장?
    # Configure Display Langage

    print(inp)
    '''

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
