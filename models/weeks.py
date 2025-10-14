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

    # CRITICAL: running_total = BASE ALLOCATION ONLY (half of spendable income)
    # This field stores ONLY the initial money allocated to this week from paycheck split
    # It does NOT and NEVER includes rollover amounts!
    #
    # Rollover amounts are stored as separate transactions (transaction_type="rollover")
    # Display logic must ADD rollover transactions to get the true starting amount
    #
    # Example: Paycheck $4237.50, Bills $3328.59, Spendable $908.91
    #   Week 1 running_total: $454.46 (half of $908.91)
    #   Week 2 running_total: $454.46 (half of $908.91)
    #   Week 2 gets rollover transaction: +$312.76 (separate from running_total)
    #   Week 2 display starting: $454.46 + $312.76 = $767.22
    #
    # DO NOT modify this field to include rollovers - it breaks the rollover system!
    running_total = Column(Float, default=0.0)

    rollover_applied = Column(Boolean, default=False)  # Track if rollover has been processed
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Week(week_number={self.week_number}, start={self.start_date}, total=${self.running_total:.2f})>"