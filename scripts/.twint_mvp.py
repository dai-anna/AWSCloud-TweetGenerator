import twint

c = twint.Config()

c.Search = "#brazilgp"  # your search here
c.Since = "2021-11-11 00:00:00"
c.Until = "2021-11-12 00:00:00"

c.to_csv = True
c.Output = "data/twint_out.csv"

twint.run.Search(c)
