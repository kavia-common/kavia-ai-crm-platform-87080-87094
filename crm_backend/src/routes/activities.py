from typing import List
from fastapi import APIRouter, HTTPException, Query
from src.db.session import get_session
from src.schemas.activities import ActivityCreate, ActivityOut, ActivityUpdate
from src.services.activities import activity_service

router = APIRouter()


@router.get("/", response_model=List[ActivityOut], summary="List activities")
# PUBLIC_INTERFACE
def list_activities(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
    """
    List activities with pagination.
    """
    db = get_session()
    skip = (page - 1) * size
    return activity_service.list(db, skip=skip, limit=size)


@router.post("/", response_model=ActivityOut, status_code=201, summary="Create activity")
# PUBLIC_INTERFACE
def create_activity(payload: ActivityCreate):
    """
    Create a new activity log entry.
    """
    db = get_session()
    return activity_service.create(db, payload)


@router.get("/{activity_id}", response_model=ActivityOut, summary="Get activity")
# PUBLIC_INTERFACE
def get_activity(activity_id: int):
    """
    Get activity by ID.
    """
    db = get_session()
    obj = activity_service.get(db, activity_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Activity not found")
    return obj


@router.put("/{activity_id}", response_model=ActivityOut, summary="Update activity")
# PUBLIC_INTERFACE
def update_activity(activity_id: int, payload: ActivityUpdate):
    """
    Update activity fields.
    """
    db = get_session()
    obj = activity_service.get(db, activity_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity_service.update(db, obj, payload)


@router.delete("/{activity_id}", status_code=204, summary="Delete activity")
# PUBLIC_INTERFACE
def delete_activity(activity_id: int):
    """
    Delete activity by ID.
    """
    db = get_session()
    obj = activity_service.get(db, activity_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Activity not found")
    activity_service.delete(db, obj)
    return None
