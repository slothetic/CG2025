import pandas as pd
import os
import json
import openpyxl
import glob
import pdb
import sys
import datetime as dt
import faulthandler; faulthandler.enable()
from data import Data

x = dt.datetime.now()
print(x)
Lee_folder = "/home/jagunlee/CG2025/*/*.solution.json"
# Lee_folder = "/home/jagunlee/CG2025/solutions/cgshop2025_examples_simple-polygon-exterior-20_250_329290ff.solution.json"
Ahn_folder = "/home/sloth/CGSHOP2025/*/*.solution.json"
score_dict = {}
for d in os.listdir("/home/jagunlee/CG2025/example_instances/"):
    if "json" in d:
        with open("/home/jagunlee/CG2025/example_instances/"+d, "r", encoding="utf-8") as f:
            root = json.load(f)
            score_dict[root["instance_uid"]] = [0]
for d in glob.glob(Lee_folder):
    print(d)
    if "solution.json" in d:
        check = False
        with open(d, "r", encoding="utf-8") as f:
            root = json.load(f)
            if "score" in root:
                score = root["score"]
                if score>score_dict[root["instance_uid"]][0]:
                    score_dict[root["instance_uid"]] = [score]
            else:
                dt1 = Data(d)
                score = dt1.score()
                if score>score_dict[root["instance_uid"]][0]:
                    score_dict[root["instance_uid"]] = [score]
        if check:
            with open(d, "w", encoding="utf-8") as f:
                root = json.load(f)
                root["score"]=score

# pdb.set_trace()
df = pd.DataFrame(score_dict, index = [x.strftime("%Y-%m-%d")])
df.to_excel("score.xlsx")
            # score_dict[root["instance_uid"]] = (0,""