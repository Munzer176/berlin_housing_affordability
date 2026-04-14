"""
Berlin Housing Affordability Analysis
======================================
Project: Who Can Still Afford Berlin? Housing Pressure Across Berlin Districts
Tools: Python (Pandas, Matplotlib, Seaborn) + Tableau
Date: April 2026

Description:
    This script analyzes housing affordability across Berlin's 12 districts
    by combining rental listing data with income statistics and social indicators.
    It produces publication-ready visualizations and Tableau-ready CSV exports.

Datasets Required:
    data/raw/
        - berlin_income_by_district.csv

    data/processed/
        - berlin_core_clean.csv
        - social_atlas_clean.csv
        - housing_bezirk_summary.csv
        - housing_social_summary.csv
        - neighborhood_rent_summary.csv
        - district_part_rent_summary.csv
        - affordability_ranking.csv
        - berlin_affordability_master.csv
        - berlin_housing_detailed_tableau.csv

How to Run:
    1. Install dependencies:
       pip install pandas matplotlib seaborn

    2. Make sure the project structure is organized as:
       data/raw/
       data/processed/
       figures/
       reports/

    3. Run:
       python scripts/berlin_affordability_analysis.py

    4. Outputs will be saved to:
       - figures/
       - data/processed/

Author: Munzer
"""

# ============================================================
# 1. IMPORTS & SETUP
# ============================================================
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", font_scale=1.1)

# Path configuration
project_root = Path(__file__).resolve().parent.parent
raw_path = project_root / "data" / "raw"
processed_path = project_root / "data" / "processed"
figures_path = project_root / "figures"
reports_path = project_root / "reports"

print("=" * 60)
print("  BERLIN HOUSING AFFORDABILITY ANALYSIS")
print("  Who Can Still Afford Berlin?")
print("=" * 60)

# ============================================================
# 2. DATA LOADING
# ============================================================
print("\n[1/7] Loading datasets...")

housing = pd.read_csv(processed_path / "berlin_core_clean.csv")
social = pd.read_csv(processed_path / "social_atlas_clean.csv")
income = pd.read_csv(raw_path / "berlin_income_by_district.csv")

print(f"  Housing listings: {housing.shape[0]:,} rows x {housing.shape[1]} columns")
print(f"  Social atlas:     {social.shape[0]} districts")
print(f"  Income data:      {income.shape[0]} districts")

# ============================================================
# 3. DATA CLEANING
# ============================================================
print("\n[2/7] Cleaning data...")

# Fix boolean columns (may be strings or already boolean)
bool_cols = ["lift", "balcony", "hasKitchen", "cellar", "garden", "newlyConst"]
for col in bool_cols:
    if col in housing.columns and housing[col].dtype == object:
        housing[col] = housing[col].map({"True": True, "False": False})

# Convert numeric columns
numeric_cols = [
    "baseRent", "totalRent", "livingSpace", "noRooms", "floor",
    "numberOfFloors", "yearConstructed", "serviceCharge", "rent_per_sqm"
]
for col in numeric_cols:
    if col in housing.columns:
        housing[col] = pd.to_numeric(housing[col], errors="coerce")

# Remove outliers (rent_per_sqm outside 5-40 EUR range)
before = len(housing)
housing = housing[(housing["rent_per_sqm"] >= 5) & (housing["rent_per_sqm"] <= 40)].copy()
print(f"  Removed {before - len(housing)} outlier rows")
print(f"  Clean dataset: {len(housing):,} rows")

# Standardize date format
date_map = {
    "Sep18": "2018-09",
    "May19": "2019-05",
    "Oct19": "2019-10",
    "Feb20": "2020-02"
}
if "date" in housing.columns:
    housing["date_clean"] = housing["date"].map(date_map)

# Report missing values
print("\n  Missing values (>5%):")
missing = (housing.isnull().sum() / len(housing) * 100).round(1)
for col, pct in missing[missing > 5].sort_values(ascending=False).items():
    print(f"    {col}: {pct}%")

# ============================================================
# 4. DATA MERGING & AFFORDABILITY CALCULATION
# ============================================================
print("\n[3/7] Merging data and calculating affordability...")

# Aggregate housing by district
district_housing = housing.groupby("bezirk").agg(
    avg_rent_sqm=("rent_per_sqm", "mean"),
    median_rent_sqm=("rent_per_sqm", "median"),
    avg_base_rent=("baseRent", "mean"),
    avg_living_space=("livingSpace", "mean"),
    listing_count=("rent_per_sqm", "count"),
    avg_total_rent=("totalRent", "mean")
).reset_index()

# Merge housing + income + social data
master = district_housing.merge(income, left_on="bezirk", right_on="district_name", how="left")
master = master.merge(social, on="district_name", how="left")

# Calculate rent burden (% of income spent on rent)
master["avg_monthly_rent"] = master["avg_base_rent"]
master["rent_burden_pct"] = (master["avg_monthly_rent"] / master["avg_monthly_income_eur"]) * 100

# Rent burden for a typical 60 sqm apartment using median values
master["median_rent_burden_pct"] = (
    master["median_rent_sqm"] * 60 / master["median_monthly_income_eur"]
) * 100

# Classify affordability
def classify_affordability(burden):
    """Classify district affordability based on international thresholds."""
    if burden < 25:
        return "Affordable"
    elif burden < 35:
        return "Moderate"
    elif burden < 50:
        return "Stressed"
    else:
        return "Severely Burdened"

master["affordability_class"] = master["rent_burden_pct"].apply(classify_affordability)

# Print results
print("\n  AFFORDABILITY RESULTS:")
print("  " + "-" * 75)
result = master[
    ["district_name", "avg_rent_sqm", "avg_monthly_income_eur",
     "avg_monthly_rent", "rent_burden_pct", "affordability_class"]
].sort_values("rent_burden_pct", ascending=False)

for _, row in result.iterrows():
    print(
        f"  {row['district_name']:<30} "
        f"Rent Burden: {row['rent_burden_pct']:5.1f}%  "
        f"[{row['affordability_class']}]"
    )

# ============================================================
# 5. VISUALIZATIONS
# ============================================================
print("\n[4/7] Creating visualizations...")

# --- Figure 1: Rent Burden by District ---
fig, ax = plt.subplots(figsize=(12, 7))
sorted_master = master.sort_values("rent_burden_pct", ascending=True)

bar_colors = [
    "#2ecc71" if x < 25 else "#f39c12" if x < 35 else "#e74c3c" if x < 50 else "#8e44ad"
    for x in sorted_master["rent_burden_pct"]
]

bars = ax.barh(
    sorted_master["district_name"],
    sorted_master["rent_burden_pct"],
    color=bar_colors,
    edgecolor="white"
)

ax.axvline(x=30, color="red", linestyle="--", alpha=0.7, label="30% Threshold (Housing Stress)")
ax.set_xlabel("Rent Burden (% of Income)", fontsize=13)
ax.set_title("Who Can Still Afford Berlin?\nRent Burden by District", fontsize=16, fontweight="bold")
ax.legend(fontsize=11)

for bar, val in zip(bars, sorted_master["rent_burden_pct"]):
    ax.text(
        bar.get_width() + 0.5,
        bar.get_y() + bar.get_height() / 2,
        f"{val:.1f}%",
        va="center",
        fontsize=10,
        fontweight="bold"
    )

plt.tight_layout()
plt.savefig(figures_path / "fig1_rent_burden.png", dpi=300, bbox_inches="tight")
plt.close()
print("  Saved: fig1_rent_burden.png")

# --- Figure 2: Rent Distribution Box Plot ---
fig, ax = plt.subplots(figsize=(14, 7))
order = housing.groupby("bezirk")["rent_per_sqm"].median().sort_values(ascending=False).index

sns.boxplot(
    data=housing,
    x="bezirk",
    y="rent_per_sqm",
    order=order,
    palette="RdYlGn_r",
    ax=ax
)

ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
ax.set_ylabel("Rent per sqm (EUR)", fontsize=13)
ax.set_xlabel("")
ax.set_title("Rent Distribution Across Berlin Districts", fontsize=16, fontweight="bold")

plt.tight_layout()
plt.savefig(figures_path / "fig2_rent_distribution.png", dpi=300, bbox_inches="tight")
plt.close()
print("  Saved: fig2_rent_distribution.png")

# --- Figure 3: Social Status vs Rent Scatter ---
fig, ax = plt.subplots(figsize=(10, 8))

size_col = "population" if "population" in master.columns else None
bubble_sizes = master[size_col] / 1500 if size_col else 200

scatter = ax.scatter(
    master["GESIx_2022"],
    master["avg_rent_sqm"],
    s=bubble_sizes,
    c=master["rent_burden_pct"],
    cmap="RdYlGn_r",
    edgecolors="black",
    alpha=0.8,
    linewidth=1.5
)

for _, row in master.iterrows():
    ax.annotate(
        row["district_name"],
        (row["GESIx_2022"], row["avg_rent_sqm"]),
        fontsize=8,
        ha="center",
        va="bottom",
        fontweight="bold"
    )

plt.colorbar(scatter, label="Rent Burden (%)", ax=ax)
ax.set_xlabel("Social Status Index (GESIx 2022)\n<-- Lower Status | Higher Status -->", fontsize=12)
ax.set_ylabel("Average Rent per sqm (EUR)", fontsize=12)
ax.set_title(
    "Social Status vs Rent: The Affordability Paradox\n(Bubble size = Population)",
    fontsize=14,
    fontweight="bold"
)

plt.tight_layout()
plt.savefig(figures_path / "fig3_social_vs_rent.png", dpi=300, bbox_inches="tight")
plt.close()
print("  Saved: fig3_social_vs_rent.png")

# --- Figure 4: Income vs Rent Comparison ---
fig, ax = plt.subplots(figsize=(12, 7))
sorted_m = master.sort_values("avg_monthly_income_eur")
x = range(len(sorted_m))
width = 0.35

ax.bar(
    [i - width / 2 for i in x],
    sorted_m["avg_monthly_income_eur"],
    width,
    label="Avg Monthly Income",
    color="#3498db"
)

ax.bar(
    [i + width / 2 for i in x],
    sorted_m["avg_monthly_rent"],
    width,
    label="Avg Monthly Rent",
    color="#e74c3c"
)

ax.set_xticks(list(x))
ax.set_xticklabels(sorted_m["district_name"], rotation=45, ha="right")
ax.set_ylabel("EUR per Month", fontsize=13)
ax.set_title("Income vs Rent by District\nThe Affordability Gap", fontsize=16, fontweight="bold")
ax.legend(fontsize=12)

plt.tight_layout()
plt.savefig(figures_path / "fig4_income_vs_rent.png", dpi=300, bbox_inches="tight")
plt.close()
print("  Saved: fig4_income_vs_rent.png")

# --- Figure 5: Correlation Heatmap ---
fig, ax = plt.subplots(figsize=(10, 8))

corr_cols = [
    "avg_rent_sqm",
    "avg_monthly_income_eur",
    "unemployment_rate_pct",
    "GESIx_2022",
    "rent_burden_pct",
    "transfer_income_share_pct",
    "population"
]

corr_labels = [
    "Avg Rent/sqm",
    "Avg Income",
    "Unemployment %",
    "Social Index",
    "Rent Burden %",
    "Transfer Income %",
    "Population"
]

corr = master[corr_cols].corr()
corr.index = corr_labels
corr.columns = corr_labels

sns.heatmap(
    corr,
    annot=True,
    fmt=".2f",
    cmap="RdBu_r",
    center=0,
    ax=ax,
    square=True,
    linewidths=0.5
)

ax.set_title("Correlation Matrix: Housing & Social Indicators", fontsize=14, fontweight="bold")

plt.tight_layout()
plt.savefig(figures_path / "fig5_correlation.png", dpi=300, bbox_inches="tight")
plt.close()
print("  Saved: fig5_correlation.png")

# ============================================================
# 6. EXPORT FOR TABLEAU
# ============================================================
print("\n[5/7] Exporting Tableau-ready datasets...")

# Master summary (district level)
master.to_csv(processed_path / "berlin_affordability_master.csv", index=False)
print(f"  Saved: berlin_affordability_master.csv ({len(master)} rows)")

# Detailed housing with income (listing level)
housing_detailed = housing.merge(income, left_on="bezirk", right_on="district_name", how="left")
housing_detailed["rent_burden_pct"] = (
    housing_detailed["baseRent"] / housing_detailed["avg_monthly_income_eur"]
) * 100

housing_detailed.to_csv(processed_path / "berlin_housing_detailed_tableau.csv", index=False)
print(f"  Saved: berlin_housing_detailed_tableau.csv ({len(housing_detailed):,} rows)")

# ============================================================
# 7. SUMMARY
# ============================================================
print("\n[6/7] Key Findings:")
print("  1. Rent burden appears high across all Berlin districts in this district-level comparison")
print(f"  2. Highest estimated burden: Mitte ({master.loc[master['district_name'] == 'Mitte', 'rent_burden_pct'].values[0]:.1f}%)")
print(f"  3. Lowest estimated burden: Marzahn-Hellersdorf ({master.loc[master['district_name'] == 'Marzahn-Hellersdorf', 'rent_burden_pct'].values[0]:.1f}%)")
print("  4. District-level social indicators alone do not fully explain rent differences")
print("  5. Housing pressure appears to be shaped by both location and property characteristics")

print("\n[7/7] All done!")
print("=" * 60)
print("  OUTPUT FILES:")
print("  - figures/fig1_rent_burden.png")
print("  - figures/fig2_rent_distribution.png")
print("  - figures/fig3_social_vs_rent.png")
print("  - figures/fig4_income_vs_rent.png")
print("  - figures/fig5_correlation.png")
print("  - data/processed/berlin_affordability_master.csv")
print("  - data/processed/berlin_housing_detailed_tableau.csv")
print("=" * 60)