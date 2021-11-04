import twint

c = twint.Config()

c.Search = "#great"  # your search here
c.Since = "2021-10-31 00:00:00"
c.Until = "2021-11-01 00:00:00"

c.to_csv = True
c.Output = "data/twint_out.csv"

twint.run.Search(c)