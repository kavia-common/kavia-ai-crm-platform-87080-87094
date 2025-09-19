from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from src.core.config import get_settings
from src.db.session import get_session
from src.services.ai import ai_service
from src.services.contacts import contact_service
from src.services.deals import deal_service

router = APIRouter()


@router.post("/lead-score/{contact_id}", summary="Compute lead score", response_model=dict)
# PUBLIC_INTERFACE
def lead_score(contact_id: int):
    """
    Compute a heuristic lead score for a contact and persist it to the contact record.

    Path parameters:
        contact_id (int): Contact ID
    Returns:
        dict: { "lead_score": float }
    """
    settings = get_settings()
    if not settings.AI_LEAD_SCORING_ENABLED:
        raise HTTPException(status_code=503, detail="Lead scoring is disabled")

    db = get_session()
    contact = contact_service.get(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    score = ai_service.score_lead(db, contact_id)
    contact.lead_score = score
    db.add(contact)
    db.commit()
    return {"lead_score": score}


@router.get("/probability/{deal_id}", summary="Estimate win probability", response_model=dict)
# PUBLIC_INTERFACE
def probability(deal_id: int):
    """
    Estimate the win probability for a given deal.

    Path parameters:
        deal_id (int): Deal ID
    Returns:
        dict: { "probability": float } where probability is between 0 and 1.
    """
    settings = get_settings()
    if not settings.AI_PROBABILITY_ENABLED:
        raise HTTPException(status_code=503, detail="Probability analysis is disabled")

    db = get_session()
    if not deal_service.get(db, deal_id):
        raise HTTPException(status_code=404, detail="Deal not found")

    p = ai_service.win_probability(db, deal_id)
    return {"probability": p}


@router.get("/forecast", summary="Forecast summary", response_model=dict)
# PUBLIC_INTERFACE
def forecast(pipeline_id: Optional[int] = Query(None, description="Filter by pipeline")):
    """
    Provide a forecast summary including weighted revenue, counts, and totals.

    Query parameters:
        pipeline_id (int, optional): Filter forecast to a specific pipeline.
    Returns:
        dict: { weighted_amount, total_open, total_amount_open }
    """
    settings = get_settings()
    if not settings.AI_FORECASTING_ENABLED:
        raise HTTPException(status_code=503, detail="Forecasting is disabled")

    db = get_session()
    return ai_service.forecast(db, pipeline_id=pipeline_id)
