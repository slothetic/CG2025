import MyNum
from data import *
import os
import sys
import pdb 
import glob
import faulthandler; faulthandler.enable()

if __name__=="__main__":
    Lee_folder = "/home/jagunlee/CG2025/challenge_instances_cgshop25/*exterior_*.json"
    argument = sys.argv
    if len(argument)>=2:
        inp = argument[1]
        #for inp in glob.glob(Lee_folder):
        print(inp)
        dt = Data(inp)
        dt.triangulate()
        dt.delaunay_triangulate()
        dt.DrawResult()
        dt.exterior_mandatory_st()
        dt.DrawResult()

        dt.exterior_solver()
