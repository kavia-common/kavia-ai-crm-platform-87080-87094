from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.core.database import get_db
from src.models.crm_models import PipelineStage
from src.schemas.crm import PipelineStage as PipelineStageSchema, PipelineStageCreate, PipelineStageUpdate

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


def _get_or_404(db: Session, stage_id: int) -> PipelineStage:
    inst = db.get(PipelineStage, stage_id)
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline stage not found")
    return inst


# PUBLIC_INTERFACE
@router.get(
    "/stages",
    response_model=List[PipelineStageSchema],
    summary="List pipeline stages",
    description="List all pipeline stages ordered by 'order'.",
)
def list_stages(db: Session = Depends(get_db)):
    stmt = select(PipelineStage).order_by(PipelineStage.order.asc())
    return db.execute(stmt).scalars().all()


# PUBLIC_INTERFACE
@router.post(
    "/stages",
    response_model=PipelineStageSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create pipeline stage",
    description="Create a pipeline stage. If 'is_default' is true, clear previous default.",
)
def create_stage(payload: PipelineStageCreate, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude_unset=True)
    if data.get("is_default"):
        db.query(PipelineStage).update({PipelineStage.is_default: False})
    inst = PipelineStage(**data)
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


# PUBLIC_INTERFACE
@router.get(
    "/stages/{stage_id}",
    response_model=PipelineStageSchema,
    summary="Get pipeline stage",
    description="Get a pipeline stage by id.",
)
def get_stage(stage_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, stage_id)


# PUBLIC_INTERFACE
@router.patch(
    "/stages/{stage_id}",
    response_model=PipelineStageSchema,
    summary="Update pipeline stage",
    description="Partially update a pipeline stage. Handles default stage uniqueness.",
)
def patch_stage(stage_id: int, payload: PipelineStageUpdate, db: Session = Depends(get_db)):
    inst = _get_or_404(db, stage_id)
    data = payload.model_dump(exclude_unset=True)
    if data.get("is_default"):
        db.query(PipelineStage).update({PipelineStage.is_default: False})
    for k, v in data.items():
        setattr(inst, k, v)
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


# PUBLIC_INTERFACE
@router.delete(
    "/stages/{stage_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete pipeline stage",
    description="Delete a pipeline stage by id.",
)
def delete_stage(stage_id: int, db: Session = Depends(get_db)):
    inst = _get_or_404(db, stage_id)
    db.delete(inst)
    db.commit()
    return None


# PUBLIC_INTERFACE
@router.get(
    "/stages/default",
    response_model=PipelineStageSchema,
    summary="Get default pipeline stage",
    description="Retrieve the default pipeline stage.",
)
def get_default_stage(db: Session = Depends(get_db)):
    inst = db.execute(select(PipelineStage).filter(PipelineStage.is_default == True)).scalar_one_or_none()  # noqa: E712
    if not inst:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Default stage not set")
    return inst
