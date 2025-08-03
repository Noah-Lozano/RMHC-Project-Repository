import pandas as pd
from scipy.stats import kruskal
import scikit_posthocs as sp
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib

matplotlib.use("Agg")  # For non-interactive environments

# Load the dataset
df = pd.read_csv("RMHC_Households (1).csv")
df.columns = df.columns.str.strip()

# Drop missing values
df = df.dropna(subset=["Donor Name", "Campaign", "Gift Value"])
df["Gift Value"] = df["Gift Value"].astype(float)

# Remove SDKT22 and Uvalde campaigns
df = df[~df["Campaign"].str.upper().isin(["SDKT22", "UVALDE"])]

# One donation per donor per campaign
df_unique = df.drop_duplicates(subset=["Donor Name", "Campaign"], keep="first")

# Get top 5 campaigns by total gift value
top5_campaigns = (
    df_unique.groupby("Campaign")["Gift Value"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

# Filter to top 5 only
df_top5 = df_unique[df_unique["Campaign"].isin(top5_campaigns)]

# Group for Kruskal-Wallis
groups = df_top5.groupby("Campaign")["Gift Value"].apply(list)

# Kruskal-Wallis test
kruskal_result = kruskal(*groups)
print("Kruskal-Wallis H-statistic:", kruskal_result.statistic)
print("p-value:", kruskal_result.pvalue)

# Post-hoc Dunn's test with Bonferroni correction
dunn_results = sp.posthoc_dunn(
    df_top5, 
    val_col="Gift Value", 
    group_col="Campaign", 
    p_adjust="bonferroni"
)

# Print Dunn results
print("\nDunn’s Post-Hoc Test Results (Bonferroni-adjusted p-values):")
print(dunn_results.round(4))

# Plot boxplot in gold with log scale for visibility
plt.figure(figsize=(12, 6))
sns.boxplot(data=df_top5, x="Campaign", y="Gift Value", color="#FFD700")
plt.yscale("log")  # Helps reveal boxes with high outliers
plt.title("Top 5 Household Campaigns (Excluding SDKT22 & Uvalde)")
plt.xlabel("Campaign")
plt.ylabel("Gift Value ($, Log Scale)")
plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig("top5_household_campaigns_boxplot_no_sdk_no_uvalde.png")
print("Saved plot as 'top5_household_campaigns_boxplot_no_sdk_no_uvalde.png'")



