#Imports needed for math functions and visualization if needed
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import chi2_contingency
import seaborn as sns

#This chooses which CSV to run the chi square test on, comment out which one your not using
df = pd.read_csv('RMHC_Households.csv')
#df = pd.read_csv('RMHC_Households.csv')

#This replaces all empty entries with a replacement for it
df['Gift Source'] = df['Gift Source'].fillna('Exceed')
df['Reason Code'] = df['Reason Code'].fillna('Blank')

#This chooses which two columns are being compared, make sure only one is active and rest are commmented out
contingency = pd.crosstab(df['Gift Source'], df['Fund'])
#contingency = pd.crosstab(df['Reason Code'], df['Fund'])
#contingency = pd.crosstab(df['Reason Code'], df['Gift Source'])

#The rest of the code below puts together the output of the chi square test
print("Contingency Table:")
print(contingency)

chi2, p, dof, expected = chi2_contingency(contingency)

print("\nChi-squared Statistic:", chi2)
print("Degrees of Freedom:", dof)
print("P-value:", p)
#print(f"P-value: {p:.20f}")   #This can specify to what decimal place the p-value will be
print("\nExpected Frequencies:")
print(expected)