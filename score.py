import MyNum
from data import *
import os
import sys
import pdb 
import faulthandler; faulthandler.enable()
import random

if __name__=="__main__":
    argument = sys.argv
    inp = argument[1]
    dt = Data(inp)
    
    obt, spt = dt.score_imp()
    score = dt.score()
    print(f"------------------{dt.instance_name} Information------------------")
    print(f"- number of obtuse triangle: {obt}")
    print(f"- number of steiner points: {spt}")
    print(f"- total score: {score}")
   