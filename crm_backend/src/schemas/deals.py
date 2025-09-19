from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field
from src.db.models import DealStageStatus


class DealBase(BaseModel):
    name: str = Field(..., description="Deal name")
    amount: float = Field(0.0, ge=0.0, description="Deal amount")
    close_date: Optional[date] = Field(None, description="Expected close date")
    account_id: Optional[int] = Field(None, description="Related account")
    contact_id: Optional[int] = Field(None, description="Primary contact")
    pipeline_id: int = Field(..., description="Pipeline ID")
    stage_id: int = Field(..., description="Stage ID within pipeline")
    status: DealStageStatus = Field(default=DealStageStatus.open, description="Deal status")


class DealCreate(DealBase):
    pass


class DealUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    close_date: Optional[date] = None
    account_id: Optional[int] = None
    contact_id: Optional[int] = None
    pipeline_id: Optional[int] = None
    stage_id: Optional[int] = None
    status: Optional[DealStageStatus] = None


class DealOut(DealBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
