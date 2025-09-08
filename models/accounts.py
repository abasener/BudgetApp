"""
Account models
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from models.database import Base


class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    running_total = Column(Float, default=0.0)
    is_default_save = Column(Boolean, default=False)
    goal_amount = Column(Float, default=0.0)  # 0 means no goal set
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        goal_text = f", goal=${self.goal_amount:.2f}" if self.goal_amount > 0 else ""
        return f"<Account(name='{self.name}', balance=${self.running_total:.2f}{goal_text})>"
    
    @property
    def goal_progress_percent(self):
        """Calculate progress toward goal as percentage"""
        if self.goal_amount <= 0:
            return 0
        return min(100, (self.running_total / self.goal_amount) * 100)
    
    @property
    def goal_remaining(self):
        """Calculate amount remaining to reach goal"""
        if self.goal_amount <= 0:
            return 0
        return max(0, self.goal_amount - self.running_total)