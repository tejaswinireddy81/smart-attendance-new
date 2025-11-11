from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from utils.db import Base
from datetime import datetime

class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    user_usn = Column(String, ForeignKey("users.usn"))
    classroom_id = Column(Integer, ForeignKey("classrooms.id"))
    subject = Column(String, nullable=True)  # Make sure this exists
    
    qr_match = Column(Boolean, default=False)
    location_match = Column(Boolean, default=False)
    face_match = Column(Boolean, default=False)
    
    marked_by_teacher = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.now)
