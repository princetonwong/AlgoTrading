import numpy as np
import pandas
import matplotlib.pyplot as plt
import statsmodels.api as sm

df = sm.datasets.macrodata.load_pandas().data

index = pandas.Index(sm.tsa.datetools.dates_from_range("1959Q1","2009Q3"))

df.index = index

print(df.head())

gdp_cycle, gdp_trend = sm.tsa.filters.hpfilter(df["realgdp"])
df["trend"] = gdp_trend
df["cycle"] = gdp_cycle.ewm(span=12).mean()
df[["cycle", "realgdp"]]["2000-03-31":].plot()
plt.show()