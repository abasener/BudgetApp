"""
Week models for bi-weekly pay periods
"""

from sqlalchemy import Column, Integer, Float, Date, DateTime, Boolean
from sqlalchemy.sql import func
from models.database import Base


class Week(Base):
    __tablename__ = "weeks"
    
    id = Column(Integer, primary_key=True, index=True)
    week_number = Column(Integer, nullable=False, index=True)  # Unique week identifier
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    running_total = Column(Float, default=0.0)  # Available money for this week
    rollover_applied = Column(Boolean, default=False)  # Track if rollover has been processed
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Week(week_number={self.week_number}, start={self.start_date}, total=${self.running_total:.2f})>"