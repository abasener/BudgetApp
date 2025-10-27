"""
Bill models for recurring payments
Now uses AccountHistory for balance tracking instead of manual running_total
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.database import Base
from typing import Optional


class Bill(Base):
    """
    Bill model for recurring payment tracking
    Balance is now tracked through AccountHistory entries instead of running_total
    """
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)

    # === Bill definition fields ===
    name = Column(String, nullable=False)  # e.g., "Rent", "School", "Taxes"
    bill_type = Column(String, nullable=False)  # Category for grouping
    payment_frequency = Column(String, nullable=False)  # "weekly", "monthly", "semester", "yearly", "other"
    typical_amount = Column(Float, nullable=False)  # Typical payment amount (can vary)
    amount_to_save = Column(Float, nullable=False)  # Amount to save per bi-weekly period

    # === Payment tracking fields ===
    last_payment_date = Column(Date)  # Last time bill was paid (manual entry only)
    last_payment_amount = Column(Float, default=0.0)  # Last payment amount

    # === Configuration fields ===
    is_variable = Column(Boolean, default=False)  # True for bills like school that vary
    notes = Column(String)  # Additional notes about the bill

    # === Timestamps ===
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # === Relationships ===
    # Back-reference to transactions related to this bill
    transactions = relationship("Transaction", foreign_keys="Transaction.bill_id", back_populates="bill")

    def __repr__(self):
        saved_amount = self.get_current_balance()
        return f"<Bill(name='{self.name}', typical=${self.typical_amount:.2f}, saved=${saved_amount:.2f}, {self.payment_frequency})>"

    def get_current_balance(self, db_session=None) -> float:
        """
        Get current balance from AccountHistory
        Returns the amount currently saved for this bill
        """
        if db_session is None:
            from models import get_db
            db_session = get_db()

        from models.account_history import AccountHistoryManager
        history_manager = AccountHistoryManager(db_session)

        try:
            return history_manager.get_current_balance(self.id, "bill")
        except Exception:
            return 0.0  # Return 0 if no history exists yet

    def get_account_history(self, db_session=None):
        """Get complete transaction history for this bill account"""
        if db_session is None:
            from models import get_db
            db_session = get_db()

        from models.account_history import AccountHistoryManager
        history_manager = AccountHistoryManager(db_session)

        return history_manager.get_account_history(self.id, "bill")

    def initialize_history(self, db_session=None, starting_balance: float = 0.0, start_date=None):
        """Initialize AccountHistory for this bill"""
        if db_session is None:
            from models import get_db
            db_session = get_db()

        from models.account_history import AccountHistoryManager
        history_manager = AccountHistoryManager(db_session)

        return history_manager.initialize_account_history(
            account_id=self.id,
            account_type="bill",
            starting_balance=starting_balance,
            start_date=start_date
        )

    # === Computed properties ===
    @property
    def savings_progress_percent(self) -> float:
        """Calculate what percentage of typical amount is currently saved"""
        if self.typical_amount <= 0:
            return 0.0

        current_balance = self.get_current_balance()
        return min(100.0, (current_balance / self.typical_amount) * 100.0)

    @property
    def savings_needed(self) -> float:
        """Calculate how much more money is needed to cover typical payment"""
        current_balance = self.get_current_balance()
        return max(0.0, self.typical_amount - current_balance)

    @property
    def is_fully_funded(self) -> bool:
        """Returns True if enough money is saved to cover typical payment"""
        return self.get_current_balance() >= self.typical_amount

    @property
    def is_overfunded(self) -> bool:
        """Returns True if more money is saved than the typical payment amount"""
        return self.get_current_balance() > self.typical_amount

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

    def update_last_payment(self, payment_date: Date, payment_amount: float):
        """Update last payment information and reset balance to 0"""
        self.last_payment_date = payment_date
        self.last_payment_amount = payment_amount
        # Note: Balance reset will be handled by creating a bill payment transaction
        # which will create the appropriate AccountHistory entry