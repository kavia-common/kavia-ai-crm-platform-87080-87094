from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class ContactBase(BaseModel):
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    title: Optional[str] = Field(None, description="Job title")
    account_id: Optional[int] = Field(None, description="Linked account id")


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    account_id: Optional[int] = None


class ContactOut(ContactBase):
    id: int = Field(..., description="Contact ID")
    created_at: datetime
    lead_score: Optional[float] = Field(None, description="AI computed lead score")

    class Config:
        from_attributes = True
