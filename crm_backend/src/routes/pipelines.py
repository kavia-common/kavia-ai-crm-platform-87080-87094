from typing import List
from fastapi import APIRouter, HTTPException, Query
from src.db.session import get_session
from src.schemas.pipelines import (
    PipelineCreate, PipelineUpdate, PipelineOut,
    PipelineStageCreate, PipelineStageUpdate, PipelineStageOut
)
from src.services.pipelines import pipeline_service, pipeline_stage_service

router = APIRouter()


@router.get("/", response_model=List[PipelineOut], summary="List pipelines")
# PUBLIC_INTERFACE
def list_pipelines(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
    """
    List pipelines.
    """
    db = get_session()
    skip = (page - 1) * size
    return pipeline_service.list(db, skip=skip, limit=size)


@router.post("/", response_model=PipelineOut, status_code=201, summary="Create pipeline")
# PUBLIC_INTERFACE
def create_pipeline(payload: PipelineCreate):
    """
    Create a pipeline.
    """
    db = get_session()
    return pipeline_service.create(db, payload)


@router.get("/{pipeline_id}", response_model=PipelineOut, summary="Get pipeline")
# PUBLIC_INTERFACE
def get_pipeline(pipeline_id: int):
    """
    Get a pipeline by ID.
    """
    db = get_session()
    obj = pipeline_service.get(db, pipeline_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return obj


@router.put("/{pipeline_id}", response_model=PipelineOut, summary="Update pipeline")
# PUBLIC_INTERFACE
def update_pipeline(pipeline_id: int, payload: PipelineUpdate):
    """
    Update a pipeline.
    """
    db = get_session()
    obj = pipeline_service.get(db, pipeline_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return pipeline_service.update(db, obj, payload)


@router.delete("/{pipeline_id}", status_code=204, summary="Delete pipeline")
# PUBLIC_INTERFACE
def delete_pipeline(pipeline_id: int):
    """
    Delete a pipeline.
    """
    db = get_session()
    obj = pipeline_service.get(db, pipeline_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    pipeline_service.delete(db, obj)
    return None


@router.get("/{pipeline_id}/stages", response_model=List[PipelineStageOut], summary="List stages for pipeline")
# PUBLIC_INTERFACE
def list_stages(pipeline_id: int):
    """
    List stages for a pipeline ordered by 'order'.
    """
    db = get_session()
    return pipeline_stage_service.list_for_pipeline(db, pipeline_id)


@router.post("/stages", response_model=PipelineStageOut, status_code=201, summary="Create stage")
# PUBLIC_INTERFACE
def create_stage(payload: PipelineStageCreate):
    """
    Create a stage within a pipeline.
    """
    db = get_session()
    return pipeline_stage_service.create(db, payload)


@router.put("/stages/{stage_id}", response_model=PipelineStageOut, summary="Update stage")
# PUBLIC_INTERFACE
def update_stage(stage_id: int, payload: PipelineStageUpdate):
    """
    Update a pipeline stage.
    """
    db = get_session()
    obj = pipeline_stage_service.get(db, stage_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Stage not found")
    return pipeline_stage_service.update(db, obj, payload)


@router.delete("/stages/{stage_id}", status_code=204, summary="Delete stage")
# PUBLIC_INTERFACE
def delete_stage(stage_id: int):
    """
    Delete a stage.
    """
    db = get_session()
    obj = pipeline_stage_service.get(db, stage_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Stage not found")
    pipeline_stage_service.delete(db, obj)
    return None
