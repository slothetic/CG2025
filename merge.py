import MyNum
from data import *
import os
import sys
import pdb 
import faulthandler; faulthandler.enable()


def merge(dt:Data, dt1:Data):
    if dt.instance_name != dt1.instance_name:
        pdb.set_trace()
        return
    print(f"Base sol: {dt.score(True)}")
    print(f"Adding sol: {dt1.score(True)}")
    dt.merge_result(dt1)
    print(f"Result sol: {dt.score(True)}")
    dt.WriteData()


if __name__=="__main__":
    argument = sys.argv
    if len(argument)>=2:
        inp = argument[1]
        new_inp = argument[2]
    else:
        inp = "opt_solutions/cgshop2025_examples_ortho_150_a39ede60.solution.json"
        new_inp = "solutions/cgshop2025_examples_ortho_150_a39ede60.solution_best.json"
    if inp!=new_inp:
        with open(inp, "r", encoding="utf-8") as f:
            root = json.load(f)
            # print(root)
            inst1 = root["instance_uid"]
        with open(new_inp, "r", encoding="utf-8") as f:
            root = json.load(f)
            # print(root)
            inst2 = root["instance_uid"]
        if inst1==inst2:
            print(f"Data 1: {inp}")
            print(f"Data 2: {new_inp}")
            dt = Data(inp)
            dt1 = Data("solutions/cgshop2025_examples_ortho_150_a39ede60.solution_best.json")
            merge(dt, dt1)
