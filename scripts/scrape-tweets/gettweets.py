import twint
import datetime
from gethashtags import tweet_data

c = twint.Config()

c.Search = "#brazilgp"  # your search here
c.Lang = "en"
c.Since = (datetime.datetime.now() - datetime.timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
c.Until = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# c.to_csv = True
# c.Output = "../../data/twint_out.csv"

twint.run.Search(c)
