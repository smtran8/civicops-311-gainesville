# Power BI Dashboard Setup Guide

## Prerequisites
- Power BI Desktop installed on Windows
- PostgreSQL database running (Docker container)
- Data loaded in `fact_requests` table

---

## Step 1: Connect to PostgreSQL Database

### **In Power BI Desktop:**
1. **Open Power BI Desktop**
2. **Get Data** → **Database** → **PostgreSQL database**
3. **Enter Connection Details:**
   - **Server:** `localhost`
   - **Database:** `civicops_311`
   - **Data Connectivity mode:** Import
4. **Authentication:**
   - **Username:** `civicops`
   - **Password:** `civicops_pass`
5. **Click Connect**

### **Select Tables:**
1. **Check `fact_requests` table**
2. **Click Load** (not Transform Data)

---

## Step 2: Data Preparation

### **Create Calculated Columns:**
1. **Go to Data view** (table icon on left)
2. **Right-click `fact_requests` table** → **New Column**

**Column 1: SLA_Breach_Flag**
```dax
SLA_Breach_Flag = IF(fact_requests[response_hours] > 72, 1, 0)
```

**Column 2: Days_Open**
```dax
Days_Open = DATEDIFF(fact_requests[created], TODAY(), DAY)
```

**Column 3: Risk_Level**
```dax
Risk_Level = 
SWITCH(
    TRUE(),
    fact_requests[breach_probability] >= 0.7, "High",
    fact_requests[breach_probability] >= 0.4, "Medium", 
    "Low"
)
```

**Column 4: Created_Date (Date only)**
```dax
Created_Date = DATE(YEAR(fact_requests[created]), MONTH(fact_requests[created]), DAY(fact_requests[created]))
```

---

## Step 3: Create Measures

### **Go to Model view** → **Right-click `fact_requests`** → **New Measure**

**Measure 1: SLA_Attainment**
```dax
SLA_Attainment = 
DIVIDE(
    CALCULATE(COUNTROWS(fact_requests), fact_requests[SLA_Breach_Flag] = 0),
    CALCULATE(COUNTROWS(fact_requests), fact_requests[status] = "Closed")
)
```

**Measure 2: Avg_Response_Time**
```dax
Avg_Response_Time = 
CALCULATE(
    AVERAGE(fact_requests[response_hours]),
    fact_requests[status] = "Closed"
)
```

**Measure 3: P90_Response_Time**
```dax
P90_Response_Time = 
PERCENTILEX.INC(
    FILTER(fact_requests, fact_requests[status] = "Closed"),
    fact_requests[response_hours],
    0.9
)
```

**Measure 4: Current_Backlog**
```dax
Current_Backlog = 
CALCULATE(
    COUNTROWS(fact_requests),
    fact_requests[status] IN {"Open", "In Process", "Submitted"}
)
```

**Measure 5: Total_Tickets**
```dax
Total_Tickets = COUNTROWS(fact_requests)
```

---

## Step 4: Build Dashboard Pages

### **Page 1: Operations Overview**

#### **KPI Cards (Top Row):**
1. **Total Tickets Card:**
   - **Fields:** Total_Tickets measure
   - **Format:** Number, 0 decimal places

2. **SLA Attainment Card:**
   - **Fields:** SLA_Attainment measure
   - **Format:** Percentage, 1 decimal place

3. **Avg Response Time Card:**
   - **Fields:** Avg_Response_Time measure
   - **Format:** Number, 1 decimal place, suffix "hours"

4. **Current Backlog Card:**
   - **Fields:** Current_Backlog measure
   - **Format:** Number, 0 decimal places

#### **Charts (Main Area):**
1. **Ticket Volume Trend (Line Chart):**
   - **X-axis:** Created_Date
   - **Y-axis:** Total_Tickets measure
   - **Title:** "Daily Ticket Volume"

2. **Request Type Distribution (Pie Chart):**
   - **Legend:** request_type
   - **Values:** Total_Tickets measure
   - **Title:** "Tickets by Request Type"

3. **SLA Performance by Type (Bar Chart):**
   - **X-axis:** request_type
   - **Y-axis:** SLA_Attainment measure
   - **Title:** "SLA Attainment by Request Type"

4. **Response Time Distribution (Histogram):**
   - **X-axis:** response_hours
   - **Y-axis:** Total_Tickets measure
   - **Title:** "Response Time Distribution"

#### **Filters (Right Panel):**
1. **Date Range Filter:**
   - **Field:** Created_Date
   - **Type:** Between

2. **Request Type Filter:**
   - **Field:** request_type
   - **Type:** List

3. **Status Filter:**
   - **Field:** status
   - **Type:** List

---

## Step 5: Formatting and Styling

### **Color Scheme:**
- **Primary:** #1f77b4 (Blue)
- **Success:** #2ca02c (Green)
- **Warning:** #ff7f0e (Orange)
- **Danger:** #d62728 (Red)

### **Apply Colors:**
1. **Select each chart**
2. **Format** → **Data colors**
3. **Apply color scheme based on data type**

### **Chart Titles:**
1. **Select chart**
2. **Format** → **Title**
3. **Enable title and customize**

---

## Step 6: Save and Export

### **Save Dashboard:**
1. **File** → **Save As**
2. **Name:** `CivicOps-311-Dashboard.pbix`
3. **Save to:** `dashboards/` folder

### **Export Screenshots:**
1. **File** → **Export** → **PowerPoint**
2. **Select pages to export**
3. **Save as:** `CivicOps-311-Screenshots.pptx`

---

## Step 7: Test Dashboard

### **Test Interactions:**
1. **Click on pie chart slices** → Verify other charts filter
2. **Use date range filter** → Verify all charts update
3. **Select request types** → Verify filtering works
4. **Hover over charts** → Verify tooltips show

### **Verify Calculations:**
1. **Check KPI cards** match expected values
2. **Verify SLA calculations** are correct
3. **Test measures** with different filters

---

## Troubleshooting

### **Connection Issues:**
- Ensure Docker container is running
- Check PostgreSQL credentials
- Verify port 5432 is accessible

### **Data Issues:**
- Refresh data if changes made
- Check calculated column formulas
- Verify measure syntax

### **Performance Issues:**
- Use Import mode (not DirectQuery)
- Limit data to last 2 years if needed
- Optimize DAX formulas
