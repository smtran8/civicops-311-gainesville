from fastapi import FastAPI
from datetime import datetime

app = FastAPI(
    title="CivicOps-311 SLA Risk API",
    description="Predict SLA breach risk for Gainesville 311 service requests",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "CivicOps 311 SLA Risk API", "status": "running"}

@app.get("/welcome")
async def welcome():
    return {"message": "Welcome to CivicOps 311 SLA Risk API", "status": "running"}

@app.get("/apicheck")
async def health_check():
    return {
        "status": "working",
        "service": "CivicOps-311 SLA Risk API",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/score_ticket")
async def score_ticket(request: dict):
    """Score a ticket for SLA breach risk"""
    # Simple demo prediction
    backlog = request.get("backlog_at_creation", 0)
    volume = request.get("rolling_7d_volume", 0)
    
    # Calculate probability based on simple rules
    probability = 0.3
    if backlog > 100:
        probability += 0.3
    elif backlog > 50:
        probability += 0.2
    
    if volume > 10:
        probability += 0.2
    elif volume > 5:
        probability += 0.1
    
    probability = min(probability, 0.95)
    
    # Determine risk level
    if probability >= 0.7:
        risk_level = "High"
    elif probability >= 0.4:
        risk_level = "Medium"
    else:
        risk_level = "Low"
    
    return {
        "ticket_id": f"TICKET_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "sla_breach_probability": round(probability, 3),
        "risk_level": risk_level,
        "top_factors": [
            f"Backlog: {backlog} tickets",
            f"Rolling volume: {volume} tickets",
            f"Request type: {request.get('request_type', 'Unknown')}"
        ]
    }