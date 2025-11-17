from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from utils.db import Base

class ActiveSession(Base):
    __tablename__ = "active_sessions"

    session_id = Column(String(36), primary_key=True, index=True)  # UUID = 36 chars
    subject = Column(String(255), nullable=False)
    teacher_id = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
