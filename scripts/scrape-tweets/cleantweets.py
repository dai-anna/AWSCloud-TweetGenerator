import pandas as pd
from gethashtags import trends_ls

df = pd.read_csv("../../data/twint_out_0.csv", sep = ",")
print(df)
print(df.columns)