# Power BI Dashboard Design - CivicOps 311 Gainesville

## Data Overview
- **Total Tickets:** 5,000
- **Closed Tickets:** 4,926 (98.5%)
- **Open Tickets:** 74 (1.5%)
- **Request Types:** 68 different types
- **Top Request Types:** Trash/Debris, Road Repair, General Code Issue, Streetlight/Lamp

---

## Dashboard Pages

### 1. **Operations Overview** (Main Dashboard)
**Purpose:** High-level KPIs and trends for operations managers

**Visualizations:**
- **KPI Cards:**
  - Total Tickets (5,000)
  - SLA Attainment % (tickets closed within 72 hours)
  - Average Response Time (hours)
  - Current Backlog (open tickets)

- **Charts:**
  - **Ticket Volume Trend** (Line chart: Created date vs Count)
  - **Request Type Distribution** (Pie chart: Top 10 request types)
  - **SLA Performance by Type** (Bar chart: Request type vs SLA attainment %)
  - **Response Time Distribution** (Histogram: Hours to close)

- **Filters:**
  - Date Range (Created date)
  - Request Type (Multi-select)
  - Status

### 2. **Risk Monitoring** (SLA Risk Analysis)
**Purpose:** Identify high-risk tickets and breach patterns

**Visualizations:**
- **KPI Cards:**
  - High Risk Tickets (predicted breach probability > 70%)
  - Breach Rate % (actual breaches in last 30 days)
  - Average Backlog Size
  - Peak Volume Day

- **Charts:**
  - **Risk Score Distribution** (Histogram: Breach probability)
  - **Breach Rate by Request Type** (Bar chart: Type vs Breach %)
  - **Backlog Trend** (Line chart: Date vs Backlog count)
  - **Volume vs Breach Correlation** (Scatter plot: Rolling volume vs Breach rate)

- **Tables:**
  - **High Risk Tickets** (Top 20 tickets with highest breach probability)
  - **Request Type Risk Ranking** (Type, Volume, Breach Rate, Avg Response Time)

### 3. **Analytics Deep Dive** (Detailed Analysis)
**Purpose:** Detailed analysis for data analysts and city planners

**Visualizations:**
- **Charts:**
  - **Response Time by Request Type** (Box plot: Type vs Hours to close)
  - **Seasonal Patterns** (Line chart: Month vs Ticket volume)
  - **Time of Day Analysis** (Bar chart: Hour vs Ticket count)
  - **Backlog Aging** (Stacked bar: Days open vs Count)

- **Tables:**
  - **Request Type Performance** (Type, Count, Avg Response, SLA %, Backlog)
  - **Recent Tickets** (Last 100 tickets with details)

---

## Data Model Design

### **Primary Table: fact_requests**
- All 5,000 tickets with features
- Key columns: id, request_type, status, created, closed, response_hours, sla_breach

### **Calculated Columns:**
```dax
SLA_Breach_Flag = IF(fact_requests[response_hours] > 72, 1, 0)
Days_Open = DATEDIFF(fact_requests[created], TODAY(), DAY)
Risk_Level = 
SWITCH(
    TRUE(),
    fact_requests[breach_probability] >= 0.7, "High",
    fact_requests[breach_probability] >= 0.4, "Medium", 
    "Low"
)
```

### **Measures:**
```dax
SLA_Attainment = 
DIVIDE(
    CALCULATE(COUNTROWS(fact_requests), fact_requests[SLA_Breach_Flag] = 0),
    CALCULATE(COUNTROWS(fact_requests), fact_requests[status] = "Closed")
)

Avg_Response_Time = 
CALCULATE(
    AVERAGE(fact_requests[response_hours]),
    fact_requests[status] = "Closed"
)

P90_Response_Time = 
PERCENTILEX.INC(
    FILTER(fact_requests, fact_requests[status] = "Closed"),
    fact_requests[response_hours],
    0.9
)

Current_Backlog = 
CALCULATE(
    COUNTROWS(fact_requests),
    fact_requests[status] IN {"Open", "In Process", "Submitted"}
)
```

---

## Connection Setup

### **PostgreSQL Connection:**
- **Server:** localhost:5432
- **Database:** civicops_311
- **Username:** civicops
- **Password:** civicops_pass
- **Table:** fact_requests

### **Data Refresh:**
- Manual refresh for development
- Automatic refresh every 4 hours in production

---

## Color Scheme
- **Primary:** #1f77b4 (Blue)
- **Success:** #2ca02c (Green) - SLA met
- **Warning:** #ff7f0e (Orange) - Medium risk
- **Danger:** #d62728 (Red) - High risk/SLA breach
- **Neutral:** #7f7f7f (Gray) - Background

---

## Interactive Features
- **Drill-through:** From summary → request type → individual tickets
- **Cross-filtering:** All charts filter each other
- **Tooltips:** Detailed information on hover
- **Bookmarks:** Save specific filter states
- **Mobile responsive:** Optimized for tablet viewing

---

## Export Options
- **PDF:** Executive summary reports
- **Excel:** Detailed data exports
- **PowerPoint:** Presentation slides
- **Web:** Embedded dashboard for city website
