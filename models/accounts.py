"""
Account models
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from models.database import Base
from typing import List, Optional


class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    running_total = Column(Float, default=0.0)
    is_default_save = Column(Boolean, default=False)
    goal_amount = Column(Float, default=0.0)  # 0 means no goal set
    auto_save_amount = Column(Float, default=0.0)  # Amount to auto-save each paycheck (after bills)
    balance_history = Column(JSON, default=list)  # Historical balance tracking: [start, end_period1, end_period2, ...]
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

    # Balance History Methods
    def initialize_balance_history(self, starting_balance: float = None):
        """Initialize balance history with starting balance"""
        if starting_balance is None:
            starting_balance = self.running_total

        self.balance_history = [starting_balance]
        self.updated_at = func.now()

    def append_period_balance(self, new_balance: float):
        """Add balance at end of pay period"""
        if self.balance_history is None:
            self.balance_history = []

        # Ensure we have the history list
        history = list(self.balance_history) if self.balance_history else []
        history.append(new_balance)

        self.balance_history = history
        self.running_total = new_balance  # Keep running_total in sync
        self.updated_at = func.now()

    def update_historical_balance(self, period_index: int, new_balance: float):
        """Update specific period balance and propagate changes to subsequent periods"""
        if self.balance_history is None or period_index >= len(self.balance_history):
            return False

        history = list(self.balance_history)
        old_balance = history[period_index]
        difference = new_balance - old_balance

        # Update the target period and all subsequent periods
        for i in range(period_index, len(history)):
            history[i] += difference

        self.balance_history = history

        # Update running_total if we modified the last period
        if period_index == len(history) - 1:
            self.running_total = new_balance
        else:
            self.running_total = history[-1]

        self.updated_at = func.now()
        return True

    def get_balance_at_period(self, period_index: int) -> Optional[float]:
        """Retrieve balance for specific period (0 = starting balance)"""
        if self.balance_history is None or period_index >= len(self.balance_history):
            return None

        return self.balance_history[period_index]

    def get_period_count(self) -> int:
        """Get number of periods tracked (length of history - 1)"""
        if self.balance_history is None:
            return 0

        return max(0, len(self.balance_history) - 1)

    def get_balance_history_copy(self) -> List[float]:
        """Get a copy of the balance history array"""
        if self.balance_history is None:
            return []

        return list(self.balance_history)