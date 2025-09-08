"""
Bill models for recurring payments
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean
from sqlalchemy.sql import func
from models.database import Base


class Bill(Base):
    __tablename__ = "bills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g., "Rent", "School", "Taxes"
    bill_type = Column(String, nullable=False)  # Category for grouping
    payment_frequency = Column(String, nullable=False)  # "weekly", "monthly", "semester", "yearly", "other"
    typical_amount = Column(Float, nullable=False)  # Typical payment amount (can vary)
    amount_to_save = Column(Float, nullable=False)  # Amount to save per bi-weekly period
    running_total = Column(Float, default=0.0)  # Current saved amount
    last_payment_date = Column(Date)  # Last time bill was paid (manual entry only)
    last_payment_amount = Column(Float, default=0.0)  # Last payment amount
    is_variable = Column(Boolean, default=False)  # True for bills like school that vary
    notes = Column(String)  # Additional notes about the bill
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Bill(name='{self.name}', typical=${self.typical_amount:.2f}, saved=${self.running_total:.2f}, {self.payment_frequency})>"