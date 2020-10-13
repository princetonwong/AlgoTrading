import pandas as pd
import backtrader as bt
from .BTScreenerBase import *
        
class MyScreener(DataNameCloseScreener, SMAScreener, RSIScreener, MACDScreener):
    pass