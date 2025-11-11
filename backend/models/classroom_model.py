from sqlalchemy import Column, Integer, String, Float
from utils.db import Base

class Classroom(Base):
    __tablename__ = "classrooms"
    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, unique=True, index=True)
    # center coords for room (latitude, longitude)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    # Optional: path to one or more images used for background recognition (comma-separated)
    image_paths = Column(String, nullable=True)
