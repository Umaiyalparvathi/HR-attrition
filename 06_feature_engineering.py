import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score
 
df = pd.read_csv("cleaned_hr_data.csv")
print(f"Loaded {len(df)} employees")
 
# ---- 1. Correlation check (quick sanity check before modeling) ----
df["AttritionFlag"] = (df["Attrition"] == "Yes").astype(int)
df["OverTimeFlag"] = (df["OverTime"] == "Yes").astype(int)
 
numeric_cols = ["Age", "TenureYears", "MonthlyIncome", "DistanceFromHome_km",
                 "JobSatisfaction", "WorkLifeBalance", "OverTimeFlag",
                 "NumCompaniesWorked", "YearsSinceLastPromotion",
                 "TrainingTimesLastYear", "PerformanceRating", "PercentSalaryHike"]
 
correlations = df[numeric_cols + ["AttritionFlag"]].corr()["AttritionFlag"].drop("AttritionFlag")
correlations = correlations.sort_values(key=abs, ascending=False)
print("\nCorrelation with Attrition (sorted by strength):")
print(correlations.round(3))
 
# ---- 2. Logistic regression ----
X = df[numeric_cols]
y = df["AttritionFlag"]
 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
 
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
 
model = LogisticRegression(max_iter=1000)
model.fit(X_train_scaled, y_train)
 
y_pred = model.predict(X_test_scaled)
y_proba = model.predict_proba(X_test_scaled)[:, 1]
 
print("\nModel performance on test set:")
print(classification_report(y_test, y_pred, target_names=["Stayed", "Left"]))
print(f"ROC-AUC: {roc_auc_score(y_test, y_proba):.3f}")
 
# ---- 3. Feature importance (standardized coefficients -> comparable magnitude) ----
importance = pd.DataFrame({
    "Feature": numeric_cols,
    "Coefficient": model.coef_[0]
})
importance["AbsCoefficient"] = importance["Coefficient"].abs()
importance = importance.sort_values("AbsCoefficient", ascending=False)
importance["Direction"] = importance["Coefficient"].apply(lambda x: "Increases Attrition Risk" if x > 0 else "Decreases Attrition Risk")
 
print("\nTop attrition drivers (logistic regression coefficients):")
print(importance[["Feature", "Coefficient", "Direction"]].to_string(index=False))
 
importance.to_csv("feature_importance.csv", index=False)
 
# ---- 4. Attrition risk score for every current employee (not just test set) ----
X_all_scaled = scaler.transform(df[numeric_cols])
df["AttritionRiskScore"] = model.predict_proba(X_all_scaled)[:, 1].round(3)
 
def risk_band(score):
    if score >= 0.7:
        return "High Risk"
    elif score >= 0.4:
        return "Medium Risk"
    else:
        return "Low Risk"
 
df["RiskBand"] = df["AttritionRiskScore"].apply(risk_band)
 
# ---- Export for Power BI ----
df.to_csv("powerbi_hr_dataset.csv", index=False)
 
print("\nExported:")
print("  powerbi_hr_dataset.csv   -> main table with per-employee AttritionRiskScore + RiskBand")
print("  feature_importance.csv   -> top drivers, for a horizontal bar chart in Power BI")
 
print("\nCurrent employees (Attrition=No) flagged High Risk:")
high_risk_current = df[(df["Attrition"] == "No") & (df["RiskBand"] == "High Risk")]
print(f"{len(high_risk_current)} employees -> these are your proactive retention targets")
print(high_risk_current[["EmployeeID", "EmployeeName", "Department", "AttritionRiskScore"]].head(10).to_string(index=False))
 
