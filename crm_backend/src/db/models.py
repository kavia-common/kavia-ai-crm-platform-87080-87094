from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Enum, Date
from sqlalchemy.orm import relationship
from src.db.session import Base
import enum


class ActivityType(str, enum.Enum):
    call = "call"
    email = "email"
    meeting = "meeting"
    note = "note"


class DealStageStatus(str, enum.Enum):
    open = "open"
    won = "won"
    lost = "lost"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    industry = Column(String(120), nullable=True)
    website = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = Column(String(120), nullable=True)

    contacts = relationship("Contact", back_populates="account", cascade="all,delete")
    deals = relationship("Deal", back_populates="account", cascade="all,delete")


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(120), nullable=False)
    last_name = Column(String(120), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(40), nullable=True)
    title = Column(String(120), nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    lead_score = Column(Float, nullable=True)  # computed by AI

    account = relationship("Account", back_populates="contacts")
    activities = relationship("ActivityLog", back_populates="contact", cascade="all,delete")
    deals = relationship("Deal", back_populates="contact")


class Pipeline(Base):
    __tablename__ = "pipelines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    stages = relationship("PipelineStage", back_populates="pipeline", cascade="all,delete")
    deals = relationship("Deal", back_populates="pipeline")


class PipelineStage(Base):
    __tablename__ = "pipeline_stages"

    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False)
    name = Column(String(120), nullable=False)
    probability = Column(Float, nullable=False, default=0.1)  # default probability associated with stage
    order = Column(Integer, nullable=False, default=0)

    pipeline = relationship("Pipeline", back_populates="stages")
    deals = relationship("Deal", back_populates="stage")


class Deal(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False, default=0.0)
    close_date = Column(Date, nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"), nullable=False)
    stage_id = Column(Integer, ForeignKey("pipeline_stages.id"), nullable=False)
    status = Column(Enum(DealStageStatus), default=DealStageStatus.open, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", back_populates="deals")
    contact = relationship("Contact", back_populates="deals")
    pipeline = relationship("Pipeline", back_populates="deals")
    stage = relationship("PipelineStage", back_populates="deals")
    activities = relationship("ActivityLog", back_populates="deal", cascade="all,delete")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=True)
    activity_type = Column(Enum(ActivityType), nullable=False)
    subject = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(120), nullable=True)

    contact = relationship("Contact", back_populates="activities")
    deal = relationship("Deal", back_populates="activities")
