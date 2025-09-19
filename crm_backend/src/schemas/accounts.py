from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AccountBase(BaseModel):
    name: str = Field(..., description="Account name")
    industry: Optional[str] = Field(None, description="Industry sector")
    website: Optional[str] = Field(None, description="Website URL")
    owner: Optional[str] = Field(None, description="Owner or account manager")


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None)
    industry: Optional[str] = Field(None)
    website: Optional[str] = Field(None)
    owner: Optional[str] = Field(None)


class AccountOut(AccountBase):
    id: int = Field(..., description="Account ID")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True
