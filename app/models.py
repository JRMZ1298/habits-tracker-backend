
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

class Badge(Base):
    __tablename__ = "badges"
    id          = Column(Integer, primary_key=True)
    key         = Column(String, unique=True, nullable=False)  # "water_5_days"
    name        = Column(String, nullable=False)               # "Fluid Flow"
    icon        = Column(String, nullable=False)               # "water_drop"
    description = Column(String)                               # "5 días tomando agua"
    required_streak = Column(Integer, nullable=False)          # 5
    category    = Column(String, nullable=False)               # "water_drop" — coincide con el icon del hábito
    user_badges = relationship("UserBadge", back_populates="badge")

class UserBadge(Base):
    __tablename__ = "user_badges"
    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    badge_id   = Column(Integer, ForeignKey("badges.id"))
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    user       = relationship("User")
    badge      = relationship("Badge", back_populates="user_badges")