import datetime as dt
import urllib.parse

keyword = ["네이버"]
url1 = "https://twitter.com/search?f=tweets&vertical=default&q="
url2 = urllib.parse.quote_plus(", ".join(keyword))

s_date = dt.date(year=2018, month=11, day=15)
e_date = dt.date(year=2018, month=11, day=16)
