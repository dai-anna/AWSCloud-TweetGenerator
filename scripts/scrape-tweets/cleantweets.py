#%%

import pandas as pd
# from gethashtags import trends_ls

df = pd.read_csv("twint_out_1.csv", sep = ",")
df["tweet"].to_list()
df.columns
df[df["language"] == "en"]
# %%
