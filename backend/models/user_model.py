from sqlalchemy import Column, Integer, String, Boolean
from utils.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    usn = Column(String, unique=True, index=True)          # student unique id
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=False)         # store hashed in prod
    is_teacher = Column(Boolean, default=False)
    photo_path = Column(String, nullable=True)             # path to ID photo (for face recog)
