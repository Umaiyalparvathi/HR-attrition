-- Normalized into 2 tables: DEPARTMENTS, EMPLOYEES
 
DROP DATABASE IF EXISTS hr_attrition;
CREATE DATABASE hr_attrition;
USE hr_attrition;
 
CREATE TABLE DEPARTMENTS (
    DepartmentID   INT AUTO_INCREMENT PRIMARY KEY,
    DepartmentName VARCHAR(50) NOT NULL UNIQUE
);
 
CREATE TABLE EMPLOYEES (
    EmployeeID              VARCHAR(10) PRIMARY KEY,
    EmployeeName             VARCHAR(100) NOT NULL,
    DepartmentID             INT NOT NULL,
    JobRole                  VARCHAR(50),
    Age                      INT,
    Gender                   VARCHAR(10),
    MaritalStatus            VARCHAR(15),
    Education                VARCHAR(20),
    TenureYears               DECIMAL(4,1),
    MonthlyIncome            INT,
    DistanceFromHome_km      INT,
    JobSatisfaction          TINYINT,     -- 1-4
    WorkLifeBalance          TINYINT,     -- 1-4
    OverTime                 VARCHAR(3),  -- Yes/No
    NumCompaniesWorked       INT,
    YearsSinceLastPromotion  DECIMAL(4,1),
    TrainingTimesLastYear    INT,
    PerformanceRating        TINYINT,     -- 1-4
    PercentSalaryHike        INT,
    Attrition                VARCHAR(3),  -- Yes/No
    FOREIGN KEY (DepartmentID) REFERENCES DEPARTMENTS(DepartmentID)
);
 
CREATE INDEX idx_emp_dept ON EMPLOYEES(DepartmentID);
CREATE INDEX idx_emp_attrition ON EMPLOYEES(Attrition);
CREATE INDEX idx_emp_tenure ON EMPLOYEES(TenureYears);
