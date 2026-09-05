import pandas as pd
import numpy as np
import random
 
random.seed(11)
np.random.seed(11)
 
n = 600
 
employee_names = [
    "Arun Kumar", "Priya Sharma", "Divya Raj", "Karthik R", "Sneha Iyer",
    "Vignesh M", "Lakshmi Narayan", "Rahul Verma", "Anitha S", "Suresh Babu",
    "Meena Krishnan", "Deepak Nair", "Kavya Reddy", "Manoj Pillai", "Swathi P",
    "Ganesh V", "Nithya S", "Ashok Kumar", "Revathi B", "Prakash Chandran",
    "Bhavya Menon", "Senthil Kumar", "Pooja Agarwal", "Ramesh Gupta", "Sowmya T",
    "Vijay Anand", "Kalaivani R", "Harish Chandra", "Aishwarya K", "Mohan Das",
    "Vikram Singh", "Anjali Nambiar", "Ravi Shankar", "Divya Bharathi", "Naveen Raj"
]
 
departments = ["Sales", "Engineering", "HR", "Finance", "Operations", "Customer Support"]
job_roles = {
    "Sales": ["Sales Executive", "Sales Manager"],
    "Engineering": ["Software Engineer", "Senior Engineer", "Tech Lead"],
    "HR": ["HR Executive", "HR Manager"],
    "Finance": ["Financial Analyst", "Accountant"],
    "Operations": ["Ops Executive", "Ops Manager"],
    "Customer Support": ["Support Executive", "Support Lead"]
}
education = ["Bachelor's", "Master's", "Diploma", "PhD"]
marital_status = ["Single", "Married", "Divorced"]
 
records = []
for i in range(n):
    name = random.choice(employee_names)
    dept = random.choice(departments)
    role = random.choice(job_roles[dept])
    age = random.randint(22, 58)
    tenure_years = round(random.uniform(0.2, 20), 1)
    monthly_income = random.randint(18000, 150000)
    distance_from_home = random.randint(1, 40)
    job_satisfaction = random.randint(1, 4)          # 1=Low, 4=Very High
    work_life_balance = random.randint(1, 4)
    overtime = random.choice(["Yes", "No"])
    num_companies_worked = random.randint(0, 8)
    years_since_promotion = round(min(tenure_years, random.uniform(0, 8)), 1)
    training_times_last_year = random.randint(0, 6)
    performance_rating = random.randint(1, 4)
    percent_salary_hike = random.randint(10, 25)
 
    # attrition probability driven by realistic factors (so the model has real signal)
    risk_score = (
        (4 - job_satisfaction) * 0.20 +
        (4 - work_life_balance) * 0.18 +
        (1 if overtime == "Yes" else 0) * 0.25 +
        (distance_from_home / 40) * 0.12 +
        (years_since_promotion / 8) * 0.10 +
        (1 - min(tenure_years, 10) / 10) * 0.15
    )
    attrition = "Yes" if random.random() < (0.10 + risk_score * 0.55) else "No"
 
    records.append({
        "EmployeeID": f"EMP{2000+i}",
        "EmployeeName": name,
        "Department": dept,
        "JobRole": role,
        "Age": age,
        "Gender": random.choice(["Male", "Female"]),
        "MaritalStatus": random.choice(marital_status),
        "Education": random.choice(education),
        "TenureYears": tenure_years,
        "MonthlyIncome": monthly_income,
        "DistanceFromHome_km": distance_from_home,
        "JobSatisfaction": job_satisfaction,
        "WorkLifeBalance": work_life_balance,
        "OverTime": overtime,
        "NumCompaniesWorked": num_companies_worked,
        "YearsSinceLastPromotion": years_since_promotion,
        "TrainingTimesLastYear": training_times_last_year,
        "PerformanceRating": performance_rating,
        "PercentSalaryHike": percent_salary_hike,
        "Attrition": attrition
    })
 
df = pd.DataFrame(records)
 
# ---- inject data quality issues ------------------------------------------
 
# 1. Inconsistent categorical casing/labels
for idx in np.random.choice(df.index, 40, replace=False):
    field = random.choice(["Department", "OverTime", "Attrition"])
    if field == "Department":
        df.loc[idx, "Department"] = df.loc[idx, "Department"].upper()
    elif field == "OverTime":
        df.loc[idx, "OverTime"] = df.loc[idx, "OverTime"].lower()
    else:
        df.loc[idx, "Attrition"] = df.loc[idx, "Attrition"].lower()
 
# 2. Missing values
for col in ["MonthlyIncome", "JobSatisfaction", "WorkLifeBalance", "Department", "PerformanceRating"]:
    idxs = np.random.choice(df.index, random.randint(15, 25), replace=False)
    df.loc[idxs, col] = np.nan
 
# 3. Impossible/outlier values (data entry errors)
err_idx = np.random.choice(df.index, 6, replace=False)
df.loc[err_idx, "Age"] = df.loc[err_idx, "Age"] * -1   # negative age typo
 
err_idx2 = np.random.choice(df.index, 5, replace=False)
df.loc[err_idx2, "TenureYears"] = 99.9  # obviously wrong sentinel value
 
# 4. Duplicate employee records (common HRMS export bug)
dupes = df.sample(12, random_state=4).copy()
df = pd.concat([df, dupes], ignore_index=True)
 
# 5. Stray whitespace
for idx in np.random.choice(df.index, 20, replace=False):
    df.loc[idx, "JobRole"] = "  " + df.loc[idx, "JobRole"]
 
df = df.sample(frac=1, random_state=8).reset_index(drop=True)
 
df.to_csv("raw_hr_data.csv", index=False)
print(f"Generated raw_hr_data.csv with {len(df)} rows")
print(df.head(8).to_string())
print("\nMissing values:")
print(df.isna().sum())
print("\nAttrition value counts (before cleaning):")
print(df["Attrition"].value_counts())
