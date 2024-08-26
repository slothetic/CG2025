from MyNum import MyNum
import json

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
    
class Data:
    def __init__(self, input):
        self.input = input
        self.ReadData()
    def ReadData(self):
        print("--------------------ReadData--------------------")
        with open(self.input, "r", encoding="utf-8") as f:
            root = json.load(f)
            # print(root)
            print(root["instance_uid"])
        pass



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

