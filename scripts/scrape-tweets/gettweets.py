import twint
import datetime
from gethashtags import trends_ls

print(trends_ls)

for idx, trend in enumerate(trends_ls):
    trend = trend.strip("#")
    c = twint.Config()
    c.Search = "#"+trend  # your search here
    c.Lang = "en"
    c.Since = (datetime.datetime.now() - datetime.timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
    c.Until = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    c.Store_csv = True
    c.Output = f"../../data/twint_out_{idx}.csv"
    twint.run.Search(c)
