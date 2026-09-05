# HR Attrition Analysis (Excel → SQL → Python → Power BI)

## Business Problem
A company has 600 employee records and HR wants to know:
1. What is our overall attrition rate, and which departments are worst affected?
2. Are we losing people early (under 1 year) or after they've settled in?
3. What actually predicts attrition - satisfaction, overtime, pay, tenure?
4. Which *currently employed* people are at high risk of leaving, so HR can act before they resign?

## Pipeline Overview
| Stage | Tool | File | What it does |
|---|---|---|---|
| 1. Generate raw data | Python | `01_generate_data.py` | Simulates a messy 600-row HRMS export with realistic attrition drivers baked in |
| 2. Clean data | Python (mirrors Excel steps) | `02_clean_data.py` | Fixes casing, negative-age typos, sentinel error values, dedupes, imputes by department |
| 3. Schema design | MySQL | `03_schema.sql` | Normalizes into DEPARTMENTS / EMPLOYEES with FK + indexes |
| 4. Load data | Python + MySQL | `04_load_to_mysql.py` | Loads cleaned CSV into MySQL |
| 5. SQL analysis | MySQL | `05_analysis_queries.sql` | Attrition rate by dept/tenure bucket/overtime, HAVING filters, RANK window function, rule-based risk flagging - 8 business-question queries |
| 6. Modeling | pandas + scikit-learn | `06_attrition_model.py` | Correlation analysis + logistic regression to rank what actually drives attrition, scores every current employee's risk |
| 7. Dashboard | Power BI | *(build separately)* | Visualize `powerbi_hr_dataset.csv` and `feature_importance.csv` |

## How to Run
```bash
pip install pandas numpy scikit-learn mysql-connector-python

python 01_generate_data.py       # -> raw_hr_data.csv
python 02_clean_data.py          # -> cleaned_hr_data.csv

# Optional MySQL step (update credentials in 04_load_to_mysql.py first):
mysql -u root -p < 03_schema.sql
python 04_load_to_mysql.py
# then run 05_analysis_queries.sql in MySQL Workbench / CLI

python 06_attrition_model.py     # -> powerbi_hr_dataset.csv, feature_importance.csv
```

## Why Logistic Regression (and not something fancier)
For a fresher-level project, a logistic regression is the right choice, not a limitation:
- Coefficients are directly interpretable ("Work-Life Balance going up by 1 point reduces attrition odds") -
  which is exactly what HR needs to act on, unlike a black-box model.
- It's honest about your current skill level (basic Python) while still showing you understand
  train/test splits, scaling, and evaluation metrics (precision/recall/ROC-AUC) - not just `.fit()`.
- Interviewers ask "why this model?" more than "why not XGBoost?" - having a clear answer matters more
  than model complexity at entry level.

## Power BI Dashboard (build using the 2 exported CSVs)
Import `powerbi_hr_dataset.csv` and `feature_importance.csv` and build:
1. **KPI cards**: Total Employees, Attrition Rate %, High-Risk Current Employees count
2. **Attrition by department** (bar chart) - `Department` + `Attrition`
3. **Attrition by tenure bucket** (bar chart) - bucket `TenureYears` in Power Query, same logic as SQL Q3
4. **Top attrition drivers** (horizontal bar chart) - from `feature_importance.csv`, sorted by `AbsCoefficient`
5. **Risk band distribution** (donut chart) - `RiskBand` for currently employed staff only (filter `Attrition = No`)
6. **High-risk employee table** - filterable table of `Attrition = No` AND `RiskBand = High Risk`, for HR to act on directly

## Key Findings
- Overall attrition rate is **54.5%** in this simulated dataset (skewed high on purpose to give the model clear signal to learn from — note in your writeup that real-world attrition is usually 10-20%, so this dataset was intentionally designed to demonstrate the analysis method, not to reflect realistic attrition levels)
- **HR has the highest departmental attrition rate at 62.1%**, followed by Operations (60.6%) — these two departments should be leadership's first priority for retention efforts
- **Work-Life Balance** and **Job Satisfaction** are the strongest protective factors; **Overtime** is the strongest risk factor (confirmed by both the correlation analysis and logistic regression coefficients)
- **28 currently employed staff** are flagged "High Risk" (≥70% predicted attrition probability) — recommend HR prioritize 1:1 check-ins with this group before they resign

## Skills Demonstrated
- **Excel-equivalent cleaning logic**: fixing data entry errors, casing standardization, department-level imputation
- **SQL**: schema normalization, CASE WHEN bucketing, HAVING, window functions (RANK), rule-based filtering
- **Python/pandas**: correlation analysis
- **scikit-learn**: train/test split, feature scaling, logistic regression, classification metrics (precision, recall, ROC-AUC)
- **Power BI**: dashboard combining descriptive stats (attrition rates) with predictive output (risk scores)
- **Business framing**: model output translated into an actionable HR shortlist, not just accuracy numbers

## Talking Points for Interviews
> "I built an attrition prediction pipeline - cleaned a messy HRMS export, analyzed attrition
> patterns by department and tenure in SQL, then used a logistic regression in Python to identify
> that work-life balance and overtime were the strongest predictors. The HR department itself had
> the highest attrition rate at 62%, which was a notable finding for leadership. I scored every
> current employee's attrition risk and flagged 28 people as high-risk for HR to proactively
> engage - turning a descriptive dashboard into something HR could actually act on."

**If asked "why logistic regression and not a more advanced model":** be honest that at this stage
interpretability and getting the fundamentals right (train/test split, avoiding data leakage, evaluation
metrics) mattered more to you than squeezing out extra accuracy with a black-box model.
