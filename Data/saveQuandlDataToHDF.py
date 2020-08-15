import pandas as pd
from pathlib import Path

DATA_STORE = Path.cwd() / "assets.h5"
df = (pd.read_csv('wiki_prices.csv',
                 parse_dates=['date'],
                 index_col=['date', 'ticker'],
                 infer_datetime_format=True)
     .sort_index())

print(df.info(null_counts=True))
with pd.HDFStore(DATA_STORE) as store:
    store.put('quandl/wiki/prices', df)

'''
date(parsed), ticker as index
open           15388776 non-null float64
high           15389259 non-null float64
low            15389259 non-null float64
close          15389313 non-null float64
volume         15389314 non-null float64
ex-dividend    15389314 non-null float64
split_ratio    15389313 non-null float64
adj_open       15388776 non-null float64
adj_high       15389259 non-null float64
adj_low        15389259 non-null float64
adj_close      15389313 non-null float64
adj_volume     15389314 non-null float64
dtypes: float64(12)
memory usage: 1.4+ GB
None

'''