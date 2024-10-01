import pandas as pd
import json
import openpyxl
import datetime as dt
import os
import glob
from data import *
import matplotlib.pyplot as plt
df1 = pd.read_excel("/home/jagunlee/CG2025/score.xlsx", index_col=0, engine = "openpyxl")
# plt.plot()
x = dt.datetime.now()
print(x)
Lee_folder = "/home/jagunlee/CG2025/*/*.solutio*.json"
# Lee_folder = "/home/jagunlee/CG2025/opt_solutions/cgshop2025_examples_ortho_80_f9b89ad1.solution.json"
Ahn_folder = "/home/sloth/CGSHOP2025/*/*.solutio*.json"
# Ahn_folder = "/home/sloth/CGSHOP2025/opt_sloth/cgshop2025_examples_ortho_150_a39ede60.solution.json"
score_dict = df1.iloc[-1].to_dict()
best_dict = {}
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
    # print(d)
    try:
        if "example_instances" not in d:
            check = False
            with open(d, "r", encoding="utf-8") as f:
                root = json.load(f)
                if "score" in root:
                    score = root["score"]
                    if score>score_dict[root["instance_uid"]][0]:
                        score_dict[root["instance_uid"]] = [score]
                        best_dict[root["instance_uid"]] = d
                else:
                    dt1 = Data(d)
                    score = dt1.score()
                    if score>score_dict[root["instance_uid"]][0]:
                        score_dict[root["instance_uid"]] = [score]
                        best_dict[root["instance_uid"]] = d
                        check = True
                    del dt1
            if check:
                with open(d, "w", encoding="utf-8") as f:
                    root["score"]=score
                    json.dump(root, f, indent='\t')
    except:
        continue
for d in glob.glob(Ahn_folder):
    # print(d)
    try:
        if "example_instances" not in d:
            check = False
            with open(d, "r", encoding="utf-8") as f:
                root = json.load(f)
                if "score" in root:
                    score = root["score"]
                    if score>score_dict[root["instance_uid"]][0]:
                        score_dict[root["instance_uid"]] = [score]
                        best_dict[root["instance_uid"]] = d
                else:
                    dt1 = Data(d)
                    score = dt1.score()
                    if score>score_dict[root["instance_uid"]][0]:
                        score_dict[root["instance_uid"]] = [score]
                        best_dict[root["instance_uid"]] = d
                        check = True
                    del dt1
            if check:
                with open(d, "w", encoding="utf-8") as f:
                    root["score"]=score
                    # pdb.set_trace()
                    json.dump(root, f, indent='\t')
    except:
        continue

df = pd.DataFrame(score_dict, index = [x.strftime("%m-%d")])
df1 = pd.concat([df1, df])
df1 = df1.reindex(sorted(df1.columns), axis=1)
df1.to_excel("/home/jagunlee/CG2025/score.xlsx")
date_list = []
names = ["ortho", "point-set", "simple-polygon_", "simple-polygon-exterior_", "simple-polygon-exterior-20"]
l = []
for n in names:
    dd = df1.filter(regex=n).mean(1)
    l.append(dd)
df2 = pd.concat(l, axis=1)
df2.columns = names
df2.plot()
plt.xticks(rotation=90)
plt.savefig("/home/jagunlee/CG2025/score.png")
print(best_dict)
opt_list = os.listdir("./best_zip")
for sol in opt_list:
    os.remove("./best_zip/"+sol)
for k in best_dict.keys():
    shutil.copyfile(best_dict[k], "./best_zip/" + k + ".solution.json")
