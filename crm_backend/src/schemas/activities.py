from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from src.db.models import ActivityType


class ActivityBase(BaseModel):
    contact_id: Optional[int] = Field(None, description="Related contact")
    deal_id: Optional[int] = Field(None, description="Related deal")
    activity_type: ActivityType = Field(..., description="Type of activity")
    subject: Optional[str] = Field(None, description="Subject or title")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_by: Optional[str] = Field(None, description="User who created the activity")


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    contact_id: Optional[int] = None
    deal_id: Optional[int] = None
    activity_type: Optional[ActivityType] = None
    subject: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[str] = None


class ActivityOut(ActivityBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
