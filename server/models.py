from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Photo(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    mission_id = Column(Integer, ForeignKey('missions.id'), nullable=False)  
    filename = Column(String, nullable=False)
    photo_type = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    is_new_image = Column(Boolean, default=True)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    profile = Column(String, default='Client User')

# --- New Mission Model ---
class Mission(Base):
    __tablename__ = 'missions'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    mission_name = Column(String, nullable=False)
    processed = Column(Boolean, default=False)

