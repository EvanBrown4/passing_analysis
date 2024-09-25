import pandas as pd
import numpy as np
import os

no_dup_files = set([])
for file in os.listdir(r'clean_files'):
    no_dup_files.add(r'clean_files\\' + file)
files = list(no_dup_files)

def merge(files):
    #explain why you did recursion
    if len(files) == 2:
        file_i = pd.read_json(files[0])
        file_j = pd.read_json(files[1])
        return pd.concat([file_i, file_j], ignore_index=True)
    elif len(files) == 1:
        return pd.read_json(files[0])
    elif len(files) == 0:
        return None
    else:
        merged1 = merge(files[:int(len(files)/2)])
        merged2 = merge(files[int(len(files)/2):])
        return pd.concat([merged1, merged2], ignore_index=True)

merged = merge(files)

merged.to_json(r'training_data.json')