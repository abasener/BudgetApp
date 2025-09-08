"""
Transaction models for all types of financial transactions
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from models.database import Base


class TransactionType(Enum):
    SPENDING = "spending"
    BILL_PAY = "bill_pay" 
    SAVING = "saving"
    INCOME = "income"


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Common fields for all transaction types
    transaction_type = Column(String, nullable=False)  # TransactionType enum value
    week_number = Column(Integer, ForeignKey("weeks.week_number"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String)  # Optional description
    
    # Spending-specific fields
    category = Column(String)  # For spending transactions
    include_in_analytics = Column(Boolean, default=True)  # Your new boolean flag!
    
    # Bill-specific fields
    bill_id = Column(Integer, ForeignKey("bills.id"))  # For bill pay transactions
    bill_type = Column(String)  # Alternative to bill_id for ad-hoc bills
    
    # Saving-specific fields
    account_id = Column(Integer, ForeignKey("accounts.id"))  # For saving transactions
    account_saved_to = Column(String)  # Alternative to account_id
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    week = relationship("Week", foreign_keys=[week_number])
    bill = relationship("Bill", foreign_keys=[bill_id])
    account = relationship("Account", foreign_keys=[account_id])
    
    def __repr__(self):
        return f"<Transaction(type={self.transaction_type}, amount=${self.amount:.2f}, date={self.date})>"
    
    @property
    def is_spending(self):
        return self.transaction_type == TransactionType.SPENDING.value
    
    @property
    def is_bill_pay(self):
        return self.transaction_type == TransactionType.BILL_PAY.value
    
    @property
    def is_saving(self):
        return self.transaction_type == TransactionType.SAVING.value
    
    @property
    def is_income(self):
        return self.transaction_type == TransactionType.INCOME.value