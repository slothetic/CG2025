from data import *

if __name__=="__main__":
    # inputName = "example_instances/cgshop2025_examples_ortho_10_ff68423e.instance.json"
    inputName = "challenge_instances_cgshop25/ortho_10_d2723dcc.instance.json"

    print(inputName)  # instance 이름 출력

    dt = Data(inputName)  # data 받아 오기

    dt.triangulate()

    print(len(dt.triangles))

    L = list(dt.triangles)
    fT = L[0] # fT stands for firstTriangle

    fT.printPoints(dt.pts)
    fT.printNeis(dt.pts)

