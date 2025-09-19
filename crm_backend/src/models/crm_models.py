from __future__ import annotations

from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import (
    String,
    Text,
    Integer,
    DateTime,
    Date,
    Enum,
    ForeignKey,
    Boolean,
    Float,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class TimestampMixin:
    """Common created_at and updated_at timestamps."""
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Account(Base, TimestampMixin):
    """An organization or company that owns deals and contacts."""
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    domain: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    size: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    owner_user_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)

    contacts: Mapped[List["Contact"]] = relationship(back_populates="account", cascade="all, delete-orphan")
    deals: Mapped[List["Deal"]] = relationship(back_populates="account", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("name", "domain", name="uq_account_name_domain"),
        Index("ix_account_owner", "owner_user_id"),
    )


class Contact(Base, TimestampMixin):
    """A person linked to an account, potential lead or customer contact."""
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_id: Mapped[Optional[int]] = mapped_column(ForeignKey("accounts.id", ondelete="SET NULL"), index=True)

    first_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), index=True, unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    title: Mapped[Optional[str]] = mapped_column(String(100))
    lead_source: Mapped[Optional[str]] = mapped_column(String(100))
    owner_user_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    account: Mapped[Optional[Account]] = relationship(back_populates="contacts")
    deals: Mapped[List["Deal"]] = relationship(back_populates="primary_contact", cascade="all, save-update")

    __table_args__ = (
        Index("ix_contact_name", "first_name", "last_name"),
        Index("ix_contact_owner", "owner_user_id"),
    )


class PipelineStage(Base, TimestampMixin):
    """Sales pipeline stages to which deals belong."""
    __tablename__ = "pipeline_stages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    deals: Mapped[List["Deal"]] = relationship(back_populates="stage")

    __table_args__ = (
        Index("ix_pipeline_stage_order", "order"),
    )


class DealStatusEnum(str):
    OPEN = "open"
    WON = "won"
    LOST = "lost"
    ON_HOLD = "on_hold"


class Deal(Base, TimestampMixin):
    """A sales opportunity linked to an account and optionally a primary contact."""
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), index=True)
    primary_contact_id: Mapped[Optional[int]] = mapped_column(ForeignKey("contacts.id", ondelete="SET NULL"), index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    expected_close_date: Mapped[Optional[date]] = mapped_column(Date)
    probability: Mapped[Optional[float]] = mapped_column(Float)  # 0-100
    status: Mapped[str] = mapped_column(
        Enum(DealStatusEnum.OPEN, DealStatusEnum.WON, DealStatusEnum.LOST, DealStatusEnum.ON_HOLD, name="deal_status"),
        default=DealStatusEnum.OPEN,
        nullable=False,
    )

    stage_id: Mapped[Optional[int]] = mapped_column(ForeignKey("pipeline_stages.id", ondelete="SET NULL"), index=True)

    account: Mapped["Account"] = relationship(back_populates="deals")
    primary_contact: Mapped[Optional["Contact"]] = relationship(back_populates="deals")
    stage: Mapped[Optional["PipelineStage"]] = relationship(back_populates="deals")
    activities: Mapped[List["ActivityLog"]] = relationship(back_populates="deal", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_deal_account_stage", "account_id", "stage_id"),
        Index("ix_deal_status", "status"),
    )


class ActivityTypeEnum(str):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    NOTE = "note"
    TASK = "task"


class ActivityLog(Base, TimestampMixin):
    """Notes and interactions related to a contact or deal."""
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    deal_id: Mapped[Optional[int]] = mapped_column(ForeignKey("deals.id", ondelete="CASCADE"), index=True)
    contact_id: Mapped[Optional[int]] = mapped_column(ForeignKey("contacts.id", ondelete="SET NULL"), index=True)

    type: Mapped[str] = mapped_column(
        Enum(
            ActivityTypeEnum.CALL,
            ActivityTypeEnum.EMAIL,
            ActivityTypeEnum.MEETING,
            ActivityTypeEnum.NOTE,
            ActivityTypeEnum.TASK,
            name="activity_type",
        ),
        default=ActivityTypeEnum.NOTE,
        nullable=False,
    )
    subject: Mapped[Optional[str]] = mapped_column(String(255))
    content: Mapped[Optional[str]] = mapped_column(Text)
    due_date: Mapped[Optional[date]] = mapped_column(Date)  # For tasks
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    performed_by_user_id: Mapped[Optional[str]] = mapped_column(String(64), index=True)

    deal: Mapped[Optional["Deal"]] = relationship(back_populates="activities")
    contact: Mapped[Optional["Contact"]] = relationship()

    __table_args__ = (
        Index("ix_activity_due_completed", "due_date", "completed"),
    )
