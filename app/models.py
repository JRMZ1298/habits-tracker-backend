from typing import Optional
from datetime import datetime, date
from sqlalchemy import String, Boolean, Date, ForeignKey, DateTime, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    name: Mapped[Optional[str]] = mapped_column(String)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    daily_reminder: Mapped[bool] = mapped_column(Boolean, default=True)
    weekly_summary: Mapped[bool] = mapped_column(Boolean, default=True)

    habits: Mapped[list["Habit"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email})"


class Habit(Base):
    __tablename__ = "habits"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    frequency: Mapped[str] = mapped_column(String, nullable=False)
    goal: Mapped[str] = mapped_column(String, nullable=False)
    reminders: Mapped[Optional[list[str]]] = mapped_column(JSON, default=list)
    icon: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="habits")
    logs: Mapped[list["HabitLog"]] = relationship(back_populates="habit", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Habit(id={self.id}, name={self.name})"


class HabitLog(Base):
    __tablename__ = "habit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    habit_id: Mapped[int] = mapped_column(ForeignKey("habits.id"), index=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    habit: Mapped["Habit"] = relationship(back_populates="logs")

    def __repr__(self) -> str:
        return f"HabitLog(id={self.id}, habit_id={self.habit_id}, date={self.date})"


class Badge(Base):
    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    icon: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    required_streak: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)

    user_badges: Mapped[list["UserBadge"]] = relationship(back_populates="badge")

    def __repr__(self) -> str:
        return f"Badge(id={self.id}, key={self.key})"


class UserBadge(Base):
    __tablename__ = "user_badges"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    badge_id: Mapped[int] = mapped_column(ForeignKey("badges.id"), index=True)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship()
    badge: Mapped["Badge"] = relationship(back_populates="user_badges")

    def __repr__(self) -> str:
        return f"UserBadge(user_id={self.user_id}, badge_id={self.badge_id})"
