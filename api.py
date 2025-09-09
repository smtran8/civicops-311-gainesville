from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime

app = FastAPI(
    title="CivicOps-311 SLA Risk API",
    description="Predict SLA breach risk for Gainesville 311 service requests",
    version="1.0.0"
)

class TicketRequest(BaseModel):
    request_type: str
    status: str
    rolling_7d_volume: int
    backlog_at_creation: int

class TicketResponse(BaseModel):
    ticket_id: str
    sla_breach_probability: float
    risk_level: str
    top_factors: List[str]

@app.get("/")
async def root():
    return {"message": "CivicOps 311 SLA Risk API", "status": "running"}

@app.get("/welcome", summary="API Welcome", tags=["General"])
async def welcome():
    return {"message": "Welcome to CivicOps 311 SLA Risk API", "status": "running"}

@app.post("/score_ticket", response_model=TicketResponse, tags=["Predictions"])
async def score_ticket(ticket: TicketRequest):
    """Score a ticket for SLA breach risk"""
    # Demo mode - return mock prediction based on input
    probability = 0.3  # Base probability
    
    # Adjust based on backlog
    if ticket.backlog_at_creation > 100:
        probability += 0.3
    elif ticket.backlog_at_creation > 50:
        probability += 0.2
    
    # Adjust based on volume
    if ticket.rolling_7d_volume > 10:
        probability += 0.2
    elif ticket.rolling_7d_volume > 5:
        probability += 0.1
    
    # Adjust based on request type
    if ticket.request_type in ["Road Repair", "Emergency", "Water"]:
        probability += 0.1
    
    # Cap at 0.95
    probability = min(probability, 0.95)
    
    # Determine risk level
    if probability >= 0.7:
        risk_level = "High"
    elif probability >= 0.4:
        risk_level = "Medium"
    else:
        risk_level = "Low"
    
    # Generate top factors
    top_factors = [
        f"Backlog: {ticket.backlog_at_creation} tickets",
        f"Rolling volume: {ticket.rolling_7d_volume} tickets",
        f"Request type: {ticket.request_type}"
    ]
    
    return TicketResponse(
        ticket_id=f"TICKET_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        sla_breach_probability=round(probability, 3),
        risk_level=risk_level,
        top_factors=top_factors
    )

@app.get("/apicheck", summary="API Status Check", tags=["General"])
async def health_check():
    """API Status Check - Verify service is working"""
    return {
        "status": "working",
        "service": "CivicOps-311 SLA Risk API",
        "timestamp": datetime.now().isoformat()
    }
