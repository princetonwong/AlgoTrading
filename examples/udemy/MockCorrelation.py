import pandas
import numpy
from pandas.plotting import scatter_matrix
import matplotlib.pyplot as plt

data2 = pandas.read_excel("Q_Correlation.xlsx", sheet_name="Marks")

scatter_matrix(data2, figsize=(10, 10))
# plt.tight_layout()
plt.show()


