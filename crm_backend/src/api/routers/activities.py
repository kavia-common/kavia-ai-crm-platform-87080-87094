from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.core.database import get_db
from src.models.crm_models import ActivityLog
from src.schemas.crm import Activity as ActivitySchema, ActivityCreate, ActivityUpdate

router = APIRouter(prefix="/activities", tags=["activities"])


def _get_or_404(db: Session, activity_id: int) -> ActivityLog:
    inst = db.get(ActivityLog, activity_id)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
    return inst


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[ActivitySchema],
    summary="List activities",
    description="Retrieve activity logs filtered by deal, contact, due state, and completion.",
)
def list_activities(
    db: Session = Depends(get_db),
    deal_id: Optional[int] = Query(default=None),
    contact_id: Optional[int] = Query(default=None),
    completed: Optional[bool] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    stmt = select(ActivityLog)
    if deal_id is not None:
        stmt = stmt.filter(ActivityLog.deal_id == deal_id)
    if contact_id is not None:
        stmt = stmt.filter(ActivityLog.contact_id == contact_id)
    if completed is not None:
        stmt = stmt.filter(ActivityLog.completed == completed)
    stmt = stmt.order_by(ActivityLog.created_at.desc()).limit(limit).offset(offset)
    return db.execute(stmt).scalars().all()


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=ActivitySchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create activity",
    description="Create a new activity log item.",
)
def create_activity(payload: ActivityCreate, db: Session = Depends(get_db)):
    inst = ActivityLog(**payload.model_dump(exclude_unset=True))
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


# PUBLIC_INTERFACE
@router.get(
    "/{activity_id}",
    response_model=ActivitySchema,
    summary="Get activity",
    description="Retrieve an activity by id.",
)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, activity_id)


# PUBLIC_INTERFACE
@router.patch(
    "/{activity_id}",
    response_model=ActivitySchema,
    summary="Update activity",
    description="Partially update fields of an activity.",
)
def patch_activity(activity_id: int, payload: ActivityUpdate, db: Session = Depends(get_db)):
    inst = _get_or_404(db, activity_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(inst, k, v)
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


# PUBLIC_INTERFACE
@router.delete(
    "/{activity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete activity",
    description="Delete an activity by id.",
)
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    inst = _get_or_404(db, activity_id)
    db.delete(inst)
    db.commit()
    return None
