import pandas as pd

# Read in the 2 data sets and combines them
df = pd.read_csv("RMHC_2018-2023.csv")
df2 = pd.read_csv("RMHC_2024-2025.csv")
df = pd.concat([df, df2], ignore_index=True)

print(df.head()) 

# remove the ", " from the name column
df["Name"] = df["Name"].str.replace(", ", "")

# remove the null values from the name column
df = df.dropna(subset=["Name"])

# remove the $ and , from the gift value column
df['Gift Value'] = df['Gift Value'].str.replace('$', '').str.replace(',', '').astype(float)

# remove the null values from the gift value column and entity 
df = df.dropna(subset=["Gift Value"])
df = df.dropna(subset=["Entity #"])

# cleans the address column to get the zip code alone
df["Address"] = df["Address"]

df.to_csv('clean_RMHC.csv', index=False)
print(df.head()) 