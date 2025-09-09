from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
from typing import List, Optional
import os
from datetime import datetime

app = FastAPI(
    title="CivicOps 311 SLA Risk API",
    description="API for predicting SLA breach risk for 311 service requests",
    version="1.0.0"
)

# Load the trained model and encoders
try:
    model = joblib.load('modeling/sla_breach_model.pkl')
    le_request_type = joblib.load('modeling/le_request_type.pkl')
    le_status = joblib.load('modeling/le_status.pkl')
    print("Model and encoders loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

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

@app.get("/welcome", summary="API Welcome", tags=["General"])
async def root():
    return {"message": "CivicOps 311 SLA Risk API", "status": "running"}

@app.post("/score_ticket", response_model=TicketResponse, tags=["Predictions"])
async def score_ticket(ticket: TicketRequest):
    """Score a ticket for SLA breach risk"""
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Prepare features for prediction
        features = pd.DataFrame([{
            'rolling_7d_volume': ticket.rolling_7d_volume,
            'backlog_at_creation': ticket.backlog_at_creation,
            'request_type_encoded': le_request_type.transform([ticket.request_type])[0],
            'status_encoded': le_status.transform([ticket.status])[0]
        }])
        
        # Make prediction
        probability = model.predict_proba(features)[0][1]
        
        # Determine risk level
        if probability >= 0.7:
            risk_level = "High"
        elif probability >= 0.4:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        # Generate top factors (simplified)
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
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")

@app.get("/apicheck", summary="API Status Check", tags=["General"])
async def health_check():
    """API Status Check - Verify service and model are working"""
    return {
        "status": "working",
        "model_loaded": model is not None,
        "service": "CivicOps-311 SLA Risk API",
        "timestamp": datetime.now().isoformat()
    }
