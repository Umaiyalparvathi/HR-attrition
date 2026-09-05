import pandas as pd
import mysql.connector
from mysql.connector import Error
 
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Uma#02",   # <-- update this
    "database": "hr_attrition"
}
 
def load_data():
    df = pd.read_csv("cleaned_hr_data.csv")
 
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("Connected to MySQL.")
 
        # ---- 1. Load DEPARTMENTS ----
        departments = df["Department"].unique().tolist()
        dept_sql = "INSERT IGNORE INTO DEPARTMENTS (DepartmentName) VALUES (%s)"
        cursor.executemany(dept_sql, [(d,) for d in departments])
        conn.commit()
        print(f"Inserted {len(departments)} departments.")
 
        cursor.execute("SELECT DepartmentID, DepartmentName FROM DEPARTMENTS")
        dept_lookup = {name: did for did, name in cursor.fetchall()}
 
        # ---- 2. Load EMPLOYEES ----
        emp_sql = """
            INSERT INTO EMPLOYEES
                (EmployeeID, EmployeeName, DepartmentID, JobRole, Age, Gender, MaritalStatus,
                 Education, TenureYears, MonthlyIncome, DistanceFromHome_km, JobSatisfaction,
                 WorkLifeBalance, OverTime, NumCompaniesWorked, YearsSinceLastPromotion,
                 TrainingTimesLastYear, PerformanceRating, PercentSalaryHike, Attrition)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE MonthlyIncome = VALUES(MonthlyIncome)
        """
        rows = []
        for _, r in df.iterrows():
            rows.append((
                r["EmployeeID"], r["EmployeeName"], dept_lookup[r["Department"]], r["JobRole"],
                int(r["Age"]), r["Gender"], r["MaritalStatus"], r["Education"], float(r["TenureYears"]),
                int(r["MonthlyIncome"]), int(r["DistanceFromHome_km"]), int(r["JobSatisfaction"]),
                int(r["WorkLifeBalance"]), r["OverTime"], int(r["NumCompaniesWorked"]),
                float(r["YearsSinceLastPromotion"]), int(r["TrainingTimesLastYear"]),
                int(r["PerformanceRating"]), int(r["PercentSalaryHike"]), r["Attrition"]
            ))
        cursor.executemany(emp_sql, rows)
        conn.commit()
        print(f"Inserted {len(rows)} employees.")
 
        cursor.close()
        conn.close()
        print("Done. Data loaded into hr_attrition database.")
 
    except Error as e:
        print(f"MySQL error: {e}")
 
if __name__ == "__main__":
    load_data()
 
