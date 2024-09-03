import MyNum
from data import *
import os
import argparse
import sys

parser = argparse.ArgumentParser()

parser.add_argument("--data", "-d", required=False, default="")
args = parser.parse_args()
if __name__=="__main__":
    if args.data:
        input = args.data
    else:
        # input = "example_instances/cgshop2025_examples_ortho_10_ff68423e.instance.json"
        input = "example_instances/cgshop2025_examples_simple-polygon-exterior-20_250_329290ff.instance.json"
    print(input)
    dt = Data(input)
    dt.triangulate()
    print("triangulate done")
    # dt.minmax_triangulate()
    # dt.DrawResult("MinMax")
    dt.additional_triangulate()
    dt.DrawPoint()
    # dt.partial_minmax_triangulate()
    # dt.add_steiner(Point(4000,4000))
    # dt.add_steiner(Point(8032,MyNum(8855,2)))
    # dt.delete_steiner(len(dt.pts)-1)
    
    dt.WriteData()
    dt.DrawResult("add_st")
