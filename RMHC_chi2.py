import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import chi2_contingency
import seaborn as sns

df = pd.read_csv('RMHC_Households.csv')

df['Gift Source'] = df['Gift Source'].fillna('Blank')

contingency = pd.crosstab(df['Gift Source'], df['Fund'])

print("Contingency Table:")
print(contingency)

chi2, p, dof, expected = chi2_contingency(contingency)

print("\nChi-squared Statistic:", chi2)
print("Degrees of Freedom:", dof)
print("P-value:", p)
print(f"P-value: {p:.20f}")
print("\nExpected Frequencies:")
print(expected)