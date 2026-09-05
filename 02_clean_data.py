import pandas as pd
import numpy as np
 
df = pd.read_csv("raw_hr_data.csv")
print(f"Raw rows: {len(df)}")
 
# ---- 1. Trim whitespace + standardize casing on text fields ----
df["JobRole"] = df["JobRole"].str.strip()
df["Department"] = df["Department"].str.strip().str.title()
df["OverTime"] = df["OverTime"].str.strip().str.title()
df["Attrition"] = df["Attrition"].str.strip().str.title()
 
# "Customer Support" needs special handling since .title() -> "Customer Support" is already correct
# but confirm no stray variants remain
df["Department"] = df["Department"].replace({"Hr": "HR"})
 
# ---- 2. Fix impossible values ----
df["Age"] = df["Age"].abs()                              # negative age -> positive
df.loc[df["TenureYears"] == 99.9, "TenureYears"] = np.nan  # sentinel error value -> null, then impute
 
# ---- 3. Remove duplicate employee records ----
before = len(df)
df = df.drop_duplicates(subset=["EmployeeID"])
print(f"Duplicate employee rows removed: {before - len(df)}")
 
# ---- 4. Impute missing values ----
# Department: fill with "Unknown" rather than guess
df["Department"] = df["Department"].fillna("Unknown")
 
# Numeric ratings/income: impute using department-level median (more accurate than global median)
for col in ["MonthlyIncome", "JobSatisfaction", "WorkLifeBalance", "PerformanceRating", "TenureYears"]:
    df[col] = df.groupby("Department")[col].transform(lambda x: x.fillna(x.median()))
    df[col] = df[col].fillna(df[col].median())  # fallback for "Unknown" dept groups with no data
 
# ---- 5. Round/cast types ----
df["JobSatisfaction"] = df["JobSatisfaction"].round().astype(int)
df["WorkLifeBalance"] = df["WorkLifeBalance"].round().astype(int)
df["PerformanceRating"] = df["PerformanceRating"].round().astype(int)
df["MonthlyIncome"] = df["MonthlyIncome"].round(0).astype(int)
 
# ---- 6. Final sanity checks ----
assert df["Age"].between(18, 65).all(), "Age out of realistic range after cleaning"
assert set(df["Attrition"].unique()) == {"Yes", "No"}, "Attrition has unexpected values"
 
df = df.reset_index(drop=True)
df.to_csv("cleaned_hr_data.csv", index=False)
 
print(f"\nFinal cleaned rows: {len(df)}")
print(df.head(8).to_string())
print("\nRemaining nulls:")
print(df.isna().sum().sum(), "total nulls")
print("\nAttrition distribution:")
print(df["Attrition"].value_counts(normalize=True).round(3) * 100)