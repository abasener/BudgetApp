"""
Savings Account models
Now uses AccountHistory for balance tracking instead of manual running_total and balance_history arrays
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.database import Base
from typing import List, Optional


class Account(Base):
    """
    Savings Account model for goal-oriented saving
    Balance is now tracked through AccountHistory entries instead of running_total
    """
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)

    # === Account definition fields ===
    name = Column(String, unique=True, nullable=False)
    is_default_save = Column(Boolean, default=False)  # Default target for rollover surpluses/deficits

    # === Goal tracking fields ===
    goal_amount = Column(Float, default=0.0)  # 0 means no goal set
    auto_save_amount = Column(Float, default=0.0)  # Amount to auto-save each paycheck (after bills)

    # === Timestamps ===
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # === Relationships ===
    # Back-reference to transactions related to this account
    transactions = relationship("Transaction", foreign_keys="Transaction.account_id", back_populates="account")

    def __repr__(self):
        current_balance = self.get_current_balance()
        goal_text = f", goal=${self.goal_amount:.2f}" if self.goal_amount > 0 else ""
        return f"<Account(name='{self.name}', balance=${current_balance:.2f}{goal_text})>"

    def get_current_balance(self, db_session=None) -> float:
        """
        Get current balance from AccountHistory
        Returns the current balance for this savings account
        """
        if db_session is None:
            from models import get_db
            db_session = get_db()

        from models.account_history import AccountHistoryManager
        history_manager = AccountHistoryManager(db_session)

        try:
            return history_manager.get_current_balance(self.id, "savings")
        except Exception:
            return 0.0  # Return 0 if no history exists yet

    def get_account_history(self, db_session=None):
        """Get complete transaction history for this savings account"""
        if db_session is None:
            from models import get_db
            db_session = get_db()

        from models.account_history import AccountHistoryManager
        history_manager = AccountHistoryManager(db_session)

        return history_manager.get_account_history(self.id, "savings")

    def initialize_history(self, db_session=None, starting_balance: float = 0.0, start_date=None):
        """Initialize AccountHistory for this savings account"""
        if db_session is None:
            from models import get_db
            db_session = get_db()

        from models.account_history import AccountHistoryManager
        history_manager = AccountHistoryManager(db_session)

        return history_manager.initialize_account_history(
            account_id=self.id,
            account_type="savings",
            starting_balance=starting_balance,
            start_date=start_date
        )

    # === Goal tracking properties ===
    @property
    def goal_progress_percent(self) -> float:
        """Calculate progress toward goal as percentage"""
        if self.goal_amount <= 0:
            return 0.0

        current_balance = self.get_current_balance()
        return min(100.0, (current_balance / self.goal_amount) * 100.0)

    @property
    def goal_remaining(self) -> float:
        """Calculate amount remaining to reach goal"""
        if self.goal_amount <= 0:
            return 0.0

        current_balance = self.get_current_balance()
        return max(0.0, self.goal_amount - current_balance)

    @property
    def is_goal_reached(self) -> bool:
        """Returns True if goal has been reached or exceeded"""
        if self.goal_amount <= 0:
            return False  # No goal set

        return self.get_current_balance() >= self.goal_amount

    @property
    def goal_excess(self) -> float:
        """Returns amount saved beyond the goal (0 if goal not reached)"""
        if self.goal_amount <= 0:
            return 0.0

        current_balance = self.get_current_balance()
        return max(0.0, current_balance - self.goal_amount)

    # === Backward compatibility properties ===
    @property
    def running_total(self) -> float:
        """
        Backward compatibility property
        Returns current balance from AccountHistory
        """
        return self.get_current_balance()

    @running_total.setter
    def running_total(self, value: float):
        """
        Backward compatibility setter
        This should not be used in new code - balance changes should go through AccountHistory
        """
        # For now, just ignore direct running_total assignments
        # In production, we might want to log a warning or raise an exception
        pass

