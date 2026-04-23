
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id         = Column(Integer, primary_key=True)
    email      = Column(String, unique=True, nullable=False)
    name       = Column(String)
    hashed_password = Column(String, nullable=False)
    habits     = relationship("Habit", back_populates="user")

class Habit(Base):
    __tablename__ = "habits"
    id          = Column(Integer, primary_key=True)
    user_id     = Column(Integer, ForeignKey("users.id"))
    name        = Column(String, nullable=False)
    frequency   = Column(String, nullable=False)
    goal        = Column(String, nullable=False)             
    reminders   = Column(JSON,   nullable=True, default=[]) 
    icon        = Column(String, nullable=False)              
    created_at  = Column(DateTime, default=datetime.utcnow)
    user        = relationship("User", back_populates="habits")
    logs        = relationship("HabitLog", back_populates="habit")

class HabitLog(Base):
    __tablename__ = "habit_logs"
    id          = Column(Integer, primary_key=True)
    habit_id    = Column(Integer, ForeignKey("habits.id"))
    completed   = Column(Boolean, default=True)
    date        = Column(Date, nullable=False)   
    habit       = relationship("Habit", back_populates="logs")