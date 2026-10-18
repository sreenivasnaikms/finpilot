"""Database setup and SQLAlchemy models for FinPilot."""

import json
from datetime import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    DateTime,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from finpilot.config import settings

# Engine and session factory
# connect_args={"check_same_thread": False} allows SQLite usage across FastAPI threads
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DBTransaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    amount = Column(Float, nullable=False)
    merchant = Column(String(255), nullable=False, index=True)
    description = Column(Text, default="")
    category = Column(String(100), default="Uncategorized", index=True)
    category_group = Column(String(100), default="Discretionary Lifestyle")
    is_recurring = Column(Boolean, default=False)
    is_anomaly = Column(Boolean, default=False)
    anomaly_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DBGoal(Base):
    __tablename__ = "financial_goals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    target_date = Column(String(10), nullable=False)
    priority = Column(String(20), default="medium")
    status = Column(String(50), default="on_track")
    created_at = Column(DateTime, default=datetime.utcnow)


class DBRecommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    action = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    priority = Column(String(20), default="medium")
    projected_monthly_savings = Column(Float, default=0.0)
    projected_annual_savings = Column(Float, default=0.0)
    trigger_type = Column(String(50), nullable=False)
    confidence_score = Column(Float, default=0.85)
    reasoning_trail = Column(Text, nullable=False)
    evidence_data = Column(Text, default="{}")  # JSON string
    status = Column(String(20), default="pending")  # pending, accepted, dismissed
    created_at = Column(DateTime, default=datetime.utcnow)


class DBDigest(Base):
    __tablename__ = "proactive_digests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    generated_at = Column(DateTime, default=datetime.utcnow)
    health_score = Column(Integer, default=75)
    key_forward_insight = Column(Text, nullable=False)
    top_action_id = Column(String(64), nullable=True)
    full_digest_json = Column(Text, nullable=False)


def init_db():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)


# Auto-create tables on module load
init_db()


def get_db():
    """FastAPI dependency for yielding database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
