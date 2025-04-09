import pandas as pd
import json
import openpyxl
import datetime as dt
import os
import glob
from data import *
import matplotlib.pyplot as plt
f1 = open("score.txt", 'w')
Lee_folder = "/home/jagunlee/CG2025/best_zip/*.solution.json"
for d in glob.glob(Lee_folder):
    # print(d)
    with open(d, "r", encoding="utf-8") as f:
        root = json.load(f)
        uid = root["instance_uid"]
        st_x = len(root["steiner_points_x"])
        data = uid+"\t%d"%st_x+"\n"
        print(data)
        f1.write(data)
f1.close()