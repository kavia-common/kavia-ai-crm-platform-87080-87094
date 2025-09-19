from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class Timestamp(BaseModel):
    created_at: datetime = Field(..., description="Record creation timestamp")
    updated_at: datetime = Field(..., description="Record last updated timestamp")

    class Config:
        from_attributes = True


class AccountBase(BaseModel):
    name: str = Field(..., description="Account name")
    domain: Optional[str] = Field(None, description="Company domain")
    industry: Optional[str] = Field(None, description="Industry vertical")
    size: Optional[str] = Field(None, description="Company size")
    description: Optional[str] = Field(None, description="Account description")
    owner_user_id: Optional[str] = Field(None, description="User responsible for the account")


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    description: Optional[str] = None
    owner_user_id: Optional[str] = None


class Account(AccountBase, Timestamp):
    id: int = Field(..., description="Primary key")

    class Config:
        from_attributes = True


class ContactBase(BaseModel):
    account_id: Optional[int] = Field(None, description="Related account")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    title: Optional[str] = Field(None, description="Job title")
    lead_source: Optional[str] = Field(None, description="Lead source")
    owner_user_id: Optional[str] = Field(None, description="Owner user ID")
    is_active: Optional[bool] = Field(default=True, description="Active status")


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    account_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    lead_source: Optional[str] = None
    owner_user_id: Optional[str] = None
    is_active: Optional[bool] = None


class Contact(ContactBase, Timestamp):
    id: int

    class Config:
        from_attributes = True


class PipelineStageBase(BaseModel):
    name: str = Field(..., description="Stage name")
    order: int = Field(..., description="Display order")
    is_default: Optional[bool] = Field(default=False, description="Default stage")


class PipelineStageCreate(PipelineStageBase):
    pass


class PipelineStageUpdate(BaseModel):
    name: Optional[str] = None
    order: Optional[int] = None
    is_default: Optional[bool] = None


class PipelineStage(PipelineStageBase, Timestamp):
    id: int

    class Config:
        from_attributes = True


class DealBase(BaseModel):
    account_id: int = Field(..., description="Account id")
    primary_contact_id: Optional[int] = Field(None, description="Primary contact id")
    name: str = Field(..., description="Deal name")
    amount: float = Field(..., description="Deal amount")
    currency: str = Field(default="USD", description="Currency code")
    expected_close_date: Optional[date] = Field(None, description="Expected close date")
    probability: Optional[float] = Field(None, description="Probability 0-100")
    status: Optional[str] = Field(default="open", description="Deal status")
    stage_id: Optional[int] = Field(None, description="Pipeline stage")


class DealCreate(DealBase):
    pass


class DealUpdate(BaseModel):
    account_id: Optional[int] = None
    primary_contact_id: Optional[int] = None
    name: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    expected_close_date: Optional[date] = None
    probability: Optional[float] = None
    status: Optional[str] = None
    stage_id: Optional[int] = None


class Deal(DealBase, Timestamp):
    id: int

    class Config:
        from_attributes = True


class ActivityBase(BaseModel):
    deal_id: Optional[int] = Field(None, description="Related deal")
    contact_id: Optional[int] = Field(None, description="Related contact")
    type: Optional[str] = Field(default="note", description="Activity type")
    subject: Optional[str] = Field(None, description="Subject/title")
    content: Optional[str] = Field(None, description="Body/content")
    due_date: Optional[date] = Field(None, description="Due date for tasks")
    completed: Optional[bool] = Field(default=False, description="Completion flag")
    performed_by_user_id: Optional[str] = Field(None, description="User who performed the activity")


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    deal_id: Optional[int] = None
    contact_id: Optional[int] = None
    type: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    due_date: Optional[date] = None
    completed: Optional[bool] = None
    performed_by_user_id: Optional[str] = None


class Activity(ActivityBase, Timestamp):
    id: int

    class Config:
        from_attributes = True
