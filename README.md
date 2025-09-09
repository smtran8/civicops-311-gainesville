# CivicOps-311 Gainesville — SLA Risk & Ops Intelligence

## Project Overview
Cities run on tickets. Every day, residents file non‑emergency requests (potholes, code violations, streetlight outages). Ops teams need to know where/when issues surge, what drives slow responses, and which new tickets are at highest risk of missing SLA. This project ingests Gainesville's 311 service requests, models a warehouse in Postgres, engineers features, predicts SLA breach risk at ticket creation, and provides a FastAPI scoring service.

**Primary Source:** [311 Service Requests (myGNV)](https://data.cityofgainesville.org/d/78uv-94ar) on dataGNV (Socrata data portal).

---

## Completed Features
- **ETL Pipeline:** Socrata API → Postgres (Docker) - 5,000+ tickets processed
- **Data Validation:** Pydantic models for data quality
- **Feature Engineering:** Rolling volumes, backlog analysis, request type complexity
- **ML Modeling:** Random Forest model with 70.3% ROC-AUC performance
- **API Service:** FastAPI with SLA breach risk scoring
- **Database:** PostgreSQL with star schema design

---

## All steps taken


### 1. Setup
```bash
# Clone and navigate to project
git clone 
cd civicops-311-gainesville

# Create environment file
cp .env.example .env


# Start Postgres
docker-compose up -d

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Pipeline
```bash
# Extract data from Socrata (5,000 rows)
python3 etl/extract_socrata.py

# Clean and transform data
python3 etl/transform_clean.py

# Load to Postgres
python3 etl/load_postgres.py

# Engineer features
python3 features/rolling_features.py

# Train ML model
python3 modeling/train.py
```

### 3. Launch API Service
```bash
uvicorn api.main:app --reload
```

**API Documentation:** http://localhost:8000/docs

---

## 4. Model Performance

### **Random Forest Model Results:**
- **ROC-AUC Score:** 0.703 (Good performance)
- **Dataset:** 4,714 closed tickets
- **SLA Definition:** 72 hours (3 days)
- **SLA Breach Rate:** 38.76%

### **Key Features:**
1. **Request Type** - Inherent complexity of different service types
2. **Status** - Resolution path (Closed, Archived)
3. **Rolling 7-Day Volume** - Recent demand surge by request type
4. **Backlog at Creation** - System load when ticket was created

---

## API Usage

### **Score a Ticket:**
```bash
curl -X POST "http://localhost:8000/score_ticket" \
  -H "Content-Type: application/json" \
  -d '{
    "request_type": "Road Repair",
    "status": "Closed",
    "rolling_7d_volume": 5,
    "backlog_at_creation": 150
  }'
```

### **Response:**
```json
{
  "ticket_id": "TICKET_20250906_111313",
  "sla_breach_probability": 0.781,
  "risk_level": "High",
  "top_factors": [
    "Backlog: 150 tickets",
    "Rolling volume: 5 tickets", 
    "Request type: Road Repair"
  ]
}
```

---

## Project Structure
```
civicops-311-gainesville/
├── etl/                    # Data extraction and loading
│   ├── extract_socrata.py  # Socrata API extraction
│   ├── transform_clean.py  # Data cleaning
│   └── load_postgres.py    # Database loading
├── features/               # Feature engineering
│   └── rolling_features.py # Rolling windows, backlogs
├── modeling/               # ML model training
│   └── train.py           # Random Forest training
├── api/                    # FastAPI service
│   └── main.py            # API endpoints
├── db/                     # Database schema
│   └── schema.sql         # PostgreSQL DDL
│   └── example_queries.sql # Analytical SQL examples
├── data/                   # Data storage
│   ├── raw/               # Raw JSON from Socrata
│   └── clean/             # Cleaned CSV files
└── docker-compose.yml     # Postgres container
```

---

## PowerBI Dashboard

Temporary dashboard preview :

![City Tickets Project PowerBI Report](https://github.com/user-attachments/assets/afee1032-5927-4693-b6a9-bfa4539b9812)


### FastAPI Documentation

Interactive API documentation available at http://localhost:8000/docs:

![FastAPI Swagger UI](dashboards/screenshots/fastapi_docs_temp.jpg)

---

## Business Value

### **For City Operations Teams:**
- **Prioritize high-risk tickets** before they breach SLA
- **Monitor system capacity** through backlog analysis
- **Identify demand surges** by request type
- **Allocate resources** based on predicted workload

### **Example Use Case:**
A "Road Repair" ticket with 150-ticket backlog and recent volume surge gets 78% breach probability → Operations team prioritizes it for immediate attention.

---

## References
See `reference_links.md` for all resources and documentation.

---

## SQL Examples
Useful, production-ready queries are available in `db/example_queries.sql`:
- SLA attainment overall and by `request_type`
- P90 response time by `request_type`
- Weekly ticket volume (last 1 year)
- Rolling 7‑day volume by `request_type`
- Current backlog overall and by `request_type`

---

## SQL Report (snapshot)
Small excerpts from running the queries locally:

```text
1) SLA attainment by request_type (top sample)
New Infrastructure .................... 100.00%
Flooding & Ditch Maintenance .......... 100.00%
Say Thanks! ........................... 100.00%
Abandoned Vehicle ..................... 100.00%
Trash / Debris (Public Property) ...... 91.67%

2) P90 response hours (top long‑tail sample)
Tree Planting Suggestion .............. 23994.83 h
Blocked Exits .........................  6556.53 h
Traffic/Pedestrian Signal .............  3004.29 h
General Police Enforcement ............  2553.44 h
Parking Enforcement ...................  1753.13 h

3) Weekly ticket volume (last 3 years)
Sample (first weeks with activity):
2022‑09‑05 → 2
2022‑09‑12 → 2
2022‑09‑19 → 2
2022‑09‑26 → 8
2022‑10‑03 → 2
Note: We initially tried a 1‑year window and it returned no rows, likely because the public dataset had a lull/migration; widening to 3 years surfaces recent history.

4) Rolling 7‑day volume by request_type (last 3 years)
Examples of highest recent 7‑day counts:
Road Repair — 2023‑02‑02 — count 3
Noise Complaint — 2023‑07‑01 — count 2
Right‑of‑Way Maintenance — 2023‑04‑27 — count 2

5) Current backlog (now)
Overall backlog ............................... 74
Top types: General Code Issue (11), Other (5), Trash/Debris–Private (5), Road Repair (5)
```

---

## Achievements
- ✅ **Working ML Pipeline** - End-to-end data science workflow
- ✅ **Production-Ready API** - FastAPI service with 70%+ accuracy
- ✅ **Real Data Integration** - Live Socrata API connection
- ✅ **Scalable Architecture** - Docker, PostgreSQL, modular design
