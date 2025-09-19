from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from src.db.session import get_session
from src.schemas.deals import DealCreate, DealOut, DealUpdate
from src.services.deals import deal_service

router = APIRouter()


@router.get("/", response_model=List[DealOut], summary="List deals")
# PUBLIC_INTERFACE
def list_deals(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
    """
    List deals with pagination.
    """
    db = get_session()
    skip = (page - 1) * size
    return deal_service.list(db, skip=skip, limit=size)


@router.post("/", response_model=DealOut, status_code=201, summary="Create deal")
# PUBLIC_INTERFACE
def create_deal(payload: DealCreate):
    """
    Create a new deal.
    """
    db = get_session()
    return deal_service.create(db, payload)


@router.get("/{deal_id}", response_model=DealOut, summary="Get deal")
# PUBLIC_INTERFACE
def get_deal(deal_id: int):
    """
    Get deal by ID.
    """
    db = get_session()
    obj = deal_service.get(db, deal_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Deal not found")
    return obj


@router.put("/{deal_id}", response_model=DealOut, summary="Update deal")
# PUBLIC_INTERFACE
def update_deal(deal_id: int, payload: DealUpdate):
    """
    Update deal fields.
    """
    db = get_session()
    obj = deal_service.get(db, deal_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal_service.update(db, obj, payload)


@router.delete("/{deal_id}", status_code=204, summary="Delete deal")
# PUBLIC_INTERFACE
def delete_deal(deal_id: int):
    """
    Delete deal by ID.
    """
    db = get_session()
    obj = deal_service.get(db, deal_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Deal not found")
    deal_service.delete(db, obj)
    return None


@router.get("/_forecast", summary="Forecast (weighted revenue)", response_model=dict)
# PUBLIC_INTERFACE
def forecast(pipeline_id: Optional[int] = Query(None, description="Filter by pipeline ID")):
    """
    Return simple weighted forecast using stage probabilities.
    """
    db = get_session()
    value = deal_service.amount_forecast(db, pipeline_id=pipeline_id)
    return {"weighted_amount": value}
