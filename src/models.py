"""Database models for activities and participants."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# Association table for many-to-many relationship between activities and students
activity_participants = Table(
    'activity_participants',
    Base.metadata,
    Column('activity_id', Integer, ForeignKey('activities.id'), primary_key=True),
    Column('participant_id', Integer, ForeignKey('participants.id'), primary_key=True),
    Column('enrolled_date', DateTime, default=datetime.utcnow)
)


class Activity(Base):
    """Activity/Club model."""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    schedule = Column(String)
    max_participants = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    participants = relationship(
        "Participant",
        secondary=activity_participants,
        back_populates="activities"
    )

    def to_dict(self):
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "schedule": self.schedule,
            "max_participants": self.max_participants,
            "participants": [p.email for p in self.participants],
            "current_count": len(self.participants)
        }


class Participant(Base):
    """Student/Participant model."""
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    activities = relationship(
        "Activity",
        secondary=activity_participants,
        back_populates="participants"
    )

    def to_dict(self):
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "email": self.email,
            "activities": [a.name for a in self.activities]
        }