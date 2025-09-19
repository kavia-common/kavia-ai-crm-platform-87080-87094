from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PipelineBase(BaseModel):
    name: str = Field(..., description="Pipeline name")
    description: Optional[str] = Field(None, description="Pipeline description")


class PipelineCreate(PipelineBase):
    pass


class PipelineUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class PipelineOut(PipelineBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PipelineStageBase(BaseModel):
    name: str = Field(..., description="Stage name")
    probability: float = Field(0.1, ge=0.0, le=1.0, description="Win probability for stage")
    order: int = Field(0, description="Ordering index")


class PipelineStageCreate(PipelineStageBase):
    pipeline_id: int = Field(..., description="Pipeline ID")


class PipelineStageUpdate(BaseModel):
    name: Optional[str] = None
    probability: Optional[float] = None
    order: Optional[int] = None


class PipelineStageOut(PipelineStageBase):
    id: int
    pipeline_id: int

    class Config:
        from_attributes = True
