USE hr_attrition;
 
-- ============================================================
-- Q1. Overall attrition rate
-- Business question: what % of the workforce is leaving?
-- ============================================================
SELECT
    COUNT(*) AS TotalEmployees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS AttritionCount,
    ROUND(SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS AttritionRate_Pct
FROM EMPLOYEES;
 
-- ============================================================
-- Q2. Attrition rate by department
-- Business question: which department has the biggest retention problem?
-- ============================================================
SELECT
    d.DepartmentName,
    COUNT(*) AS TotalEmployees,
    SUM(CASE WHEN e.Attrition = 'Yes' THEN 1 ELSE 0 END) AS AttritionCount,
    ROUND(SUM(CASE WHEN e.Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS AttritionRate_Pct
FROM EMPLOYEES e
JOIN DEPARTMENTS d ON e.DepartmentID = d.DepartmentID
GROUP BY d.DepartmentName
ORDER BY AttritionRate_Pct DESC;
 
-- ============================================================
-- Q3. Attrition rate by tenure bucket (cohort-style grouping)
-- Business question: are we losing people early (<1yr) or after they've settled in?
-- ============================================================
SELECT
    CASE
        WHEN TenureYears < 1 THEN '0-1 yr'
        WHEN TenureYears < 3 THEN '1-3 yrs'
        WHEN TenureYears < 5 THEN '3-5 yrs'
        WHEN TenureYears < 10 THEN '5-10 yrs'
        ELSE '10+ yrs'
    END AS TenureBucket,
    COUNT(*) AS TotalEmployees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS AttritionCount,
    ROUND(SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS AttritionRate_Pct
FROM EMPLOYEES
GROUP BY TenureBucket
ORDER BY MIN(TenureYears);
 
-- ============================================================
-- Q4. Overtime vs attrition (HAVING to surface only meaningful groups)
-- Business question: does overtime correlate with people leaving?
-- ============================================================
SELECT
    OverTime,
    COUNT(*) AS TotalEmployees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) AS AttritionCount,
    ROUND(SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS AttritionRate_Pct
FROM EMPLOYEES
GROUP BY OverTime
HAVING COUNT(*) > 5
ORDER BY AttritionRate_Pct DESC;
 
-- ============================================================
-- Q5. Job satisfaction & work-life balance vs attrition
-- Business question: which satisfaction levels correlate most with leaving?
-- ============================================================
SELECT
    JobSatisfaction,
    WorkLifeBalance,
    COUNT(*) AS TotalEmployees,
    ROUND(SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS AttritionRate_Pct
FROM EMPLOYEES
GROUP BY JobSatisfaction, WorkLifeBalance
ORDER BY AttritionRate_Pct DESC;
 
-- ============================================================
-- Q6. Department attrition ranked (window function)
-- Business question: rank departments by attrition severity for leadership review
-- ============================================================
WITH dept_attrition AS (
    SELECT
        d.DepartmentName,
        COUNT(*) AS TotalEmployees,
        ROUND(SUM(CASE WHEN e.Attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*) * 100, 2) AS AttritionRate_Pct
    FROM EMPLOYEES e
    JOIN DEPARTMENTS d ON e.DepartmentID = d.DepartmentID
    GROUP BY d.DepartmentName
)
SELECT
    DepartmentName,
    TotalEmployees,
    AttritionRate_Pct,
    RANK() OVER (ORDER BY AttritionRate_Pct DESC) AS RiskRank
FROM dept_attrition;
 
-- ============================================================
-- Q7. Salary vs attrition - avg income of leavers vs stayers, by department
-- Business question: is pay a factor, and where specifically?
-- ============================================================
SELECT
    d.DepartmentName,
    ROUND(AVG(CASE WHEN e.Attrition = 'Yes' THEN e.MonthlyIncome END), 0) AS AvgIncome_Left,
    ROUND(AVG(CASE WHEN e.Attrition = 'No' THEN e.MonthlyIncome END), 0) AS AvgIncome_Stayed
FROM EMPLOYEES e
JOIN DEPARTMENTS d ON e.DepartmentID = d.DepartmentID
GROUP BY d.DepartmentName
ORDER BY d.DepartmentName;
 
-- ============================================================
-- Q8. Employees at highest attrition risk (simple rule-based flag for HR to act on)
-- Business question: who should HR proactively check in with this month?
-- ============================================================
SELECT
    EmployeeID, EmployeeName, JobRole,
    JobSatisfaction, WorkLifeBalance, OverTime, YearsSinceLastPromotion
FROM EMPLOYEES
WHERE Attrition = 'No'                 -- still employed
  AND JobSatisfaction <= 2
  AND WorkLifeBalance <= 2
  AND OverTime = 'Yes'
  AND YearsSinceLastPromotion > 2
ORDER BY YearsSinceLastPromotion DESC;

