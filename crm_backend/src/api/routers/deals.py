from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.core.database import get_db
from src.models.crm_models import Deal, DealStatusEnum
from src.schemas.crm import Deal as DealSchema, DealCreate, DealUpdate

router = APIRouter(prefix="/deals", tags=["deals"])


def _get_or_404(db: Session, deal_id: int) -> Deal:
    inst = db.get(Deal, deal_id)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")
    return inst


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[DealSchema],
    summary="List deals",
    description="Retrieve deals filtered by account, stage, status, and search.",
)
def list_deals(
    db: Session = Depends(get_db),
    account_id: Optional[int] = Query(default=None),
    stage_id: Optional[int] = Query(default=None),
    status: Optional[str] = Query(default=None, description="open|won|lost|on_hold"),
    q: Optional[str] = Query(default=None, description="Search by deal name"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    stmt = select(Deal)
    if account_id is not None:
        stmt = stmt.filter(Deal.account_id == account_id)
    if stage_id is not None:
        stmt = stmt.filter(Deal.stage_id == stage_id)
    if status is not None:
        stmt = stmt.filter(Deal.status == status)
    if q:
        stmt = stmt.filter(Deal.name.ilike(f"%{q}%"))
    stmt = stmt.order_by(Deal.created_at.desc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=DealSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create deal",
    description="Create a new deal.",
)
def create_deal(payload: DealCreate, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude_unset=True)
    # Validations for status
    if data.get("status") and data["status"] not in {
        DealStatusEnum.OPEN,
        DealStatusEnum.WON,
        DealStatusEnum.LOST,
        DealStatusEnum.ON_HOLD,
    }:
        raise HTTPException(status_code=400, detail="Invalid deal status")
    inst = Deal(**data)
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


# PUBLIC_INTERFACE
@router.get(
    "/{deal_id}",
    response_model=DealSchema,
    summary="Get deal",
    description="Retrieve a deal by id.",
)
def get_deal(deal_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, deal_id)


# PUBLIC_INTERFACE
@router.patch(
    "/{deal_id}",
    response_model=DealSchema,
    summary="Update deal",
    description="Partially update fields of a deal.",
)
def patch_deal(deal_id: int, payload: DealUpdate, db: Session = Depends(get_db)):
    inst = _get_or_404(db, deal_id)
    data = payload.model_dump(exclude_unset=True)
    if data.get("status") and data["status"] not in {
        DealStatusEnum.OPEN,
        DealStatusEnum.WON,
        DealStatusEnum.LOST,
        DealStatusEnum.ON_HOLD,
    }:
        raise HTTPException(status_code=400, detail="Invalid deal status")
    for k, v in data.items():
        setattr(inst, k, v)
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


# PUBLIC_INTERFACE
@router.delete(
    "/{deal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete deal",
    description="Delete a deal by id.",
)
def delete_deal(deal_id: int, db: Session = Depends(get_db)):
    inst = _get_or_404(db, deal_id)
    db.delete(inst)
    db.commit()
    return None


# PUBLIC_INTERFACE
@router.post(
    "/{deal_id}/move/{stage_id}",
    response_model=DealSchema,
    summary="Move deal to stage",
    description="Move a deal to a different pipeline stage.",
)
def move_deal_stage(deal_id: int, stage_id: int, db: Session = Depends(get_db)):
    inst = _get_or_404(db, deal_id)
    inst.stage_id = stage_id
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst
