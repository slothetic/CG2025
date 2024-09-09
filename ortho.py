import MyNum
from data import *
import os
import sys
import pdb 
import faulthandler; faulthandler.enable()

sys.setrecursionlimit(100000)
# parser = argparse.ArgumentParser()

# parser.add_argument("--data", "-d", required=False, default="")
# args = parser.parse_args()
if __name__=="__main__":
    argument = sys.argv
    if len(argument)>=2:
        inp = argument[1]
    else:
        inp = "example_instances/cgshop2025_examples_ortho_10_ff68423e.instance.json"
    dt = Data(inp)
    print(f"{dt.instance_name} Start!!!!")
    if "example_instances" in inp:
        dt.triangulate()
        dt.DrawPoint()
        dt.delaunay_triangulate()
        dt.make_non_obtuse_ortho()
        dt.WriteData()
        dt.DrawResult()
        print("score:", dt.score())