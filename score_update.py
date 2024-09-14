import pandas as pd
import json
import openpyxl
import datetime as dt
import os
import glob
from data import *
import matplotlib.pyplot as plt
df1 = pd.read_excel("score.xlsx", index_col=0, engine = "openpyxl")

# plt.plot()
x = dt.datetime.now()
print(x)
Lee_folder = "/home/jagunlee/CG2025/*/*.solutio*.json"
# Lee_folder = "/home/jagunlee/CG2025/opt_solutions/cgshop2025_examples_ortho_80_f9b89ad1.solution.json"
Ahn_folder = "/home/sloth/CGSHOP2025/*/*.solutio*.json"
# Ahn_folder = "/home/sloth/CGSHOP2025/opt_sloth/cgshop2025_examples_ortho_150_a39ede60.solution.json"
score_dict = df1.iloc[-1].to_dict()
# for key in score_dict.keys():
#     score_dict[key] = [score_dict[key]]
# pdb.set_trace()
# for d in os.listdir("/home/jagunlee/CG2025/example_instances/"):
#     if "json" in d:
#         with open("/home/jagunlee/CG2025/example_instances/"+d, "r", encoding="utf-8") as f:
#             root = json.load(f)
#             score_dict[root["instance_uid"]] = [0]
#             pdb.set_trace()
for k in score_dict.keys():
    score_dict[k] = [0]
for d in glob.glob(Lee_folder):
    print(d)
    try:
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
                        check = True
                    del dt1
            if check:
                with open(d, "w", encoding="utf-8") as f:
                    root["score"]=score
                    json.dump(root, f, indent='\t')
    except:
        continue
for d in glob.glob(Ahn_folder):
    print(d)
    try:
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
                        check = True
                    del dt1
            if check:
                with open(d, "w", encoding="utf-8") as f:
                    root["score"]=score
                    # pdb.set_trace()
                    json.dump(root, f, indent='\t')
    except:
        continue

# pdb.set_trace()
df = pd.DataFrame(score_dict, index = [x.strftime("%Y-%m-%d")])
df1 = pd.concat([df1, df])
# pdb.set_trace()
df1.to_excel("score.xlsx")
date_list = []
names = ["ortho", "point-set", "simple-polygon_", "simple-polygon-exterior_", "simple-polygon-exterior-20"]
l = []
for n in names:
    dd = df1.filter(regex=n).mean(1)
    l.append(dd)
df2 = pd.concat(l, axis=1)
df2.columns = names
df2.plot()
plt.savefig("score.png")

