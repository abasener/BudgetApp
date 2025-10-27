"""
Unified Transaction model for all types of financial transactions
All transaction types use the same model - unused fields are left NULL
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from models.database import Base


class TransactionType(Enum):
    """Transaction type enum - kept for backward compatibility"""
    SPENDING = "spending"
    BILL_PAY = "bill_pay"
    SAVING = "saving"
    INCOME = "income"
    ROLLOVER = "rollover"


class Transaction(Base):
    """
    Unified transaction model for all financial transactions
    Fields are used as needed based on transaction type - unused fields remain NULL
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    # === Core fields (used by all transaction types) ===
    transaction_type = Column(String, nullable=False)  # TransactionType enum value
    week_number = Column(Integer, ForeignKey("weeks.week_number"), nullable=False, index=True)
    amount = Column(Float, nullable=False)  # Can be positive or negative
    date = Column(Date, nullable=False)
    description = Column(String)  # Optional description

    # === Spending transaction fields ===
    category = Column(String)  # Spending category (e.g., "Food", "Gas", "Entertainment")
    include_in_analytics = Column(Boolean, default=True)  # Include in spending analytics

    # === Bill-related fields ===
    bill_id = Column(Integer, ForeignKey("bills.id"))  # For bill payments and savings
    bill_type = Column(String)  # Alternative to bill_id for ad-hoc bills

    # === Account-related fields ===
    account_id = Column(Integer, ForeignKey("accounts.id"))  # For savings transactions
    account_saved_to = Column(String)  # Alternative to account_id (account name)

    # === Timestamps ===
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # === Relationships ===
    week = relationship("Week", foreign_keys=[week_number])
    bill = relationship("Bill", foreign_keys=[bill_id])
    account = relationship("Account", foreign_keys=[account_id])

    # Back-reference to account history entries created by this transaction
    history_entries = relationship("AccountHistory", back_populates="transaction")

    def __repr__(self):
        account_info = ""
        if self.bill_id:
            account_info = f", bill_id={self.bill_id}"
        elif self.account_id:
            account_info = f", account_id={self.account_id}"
        elif self.category:
            account_info = f", category={self.category}"

        return f"<Transaction(id={self.id}, type={self.transaction_type}, amount=${self.amount:.2f}, date={self.date}{account_info})>"

    # === Helper properties (kept for backward compatibility) ===
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

    @property
    def is_rollover(self):
        return self.transaction_type == TransactionType.ROLLOVER.value

    # === New helper methods ===
    @property
    def affects_account(self):
        """Returns True if this transaction affects an account (bill or savings)"""
        return self.bill_id is not None or self.account_id is not None

    @property
    def account_type(self):
        """Returns the type of account this transaction affects"""
        if self.bill_id:
            return "bill"
        elif self.account_id:
            return "savings"
        return None

    @property
    def affected_account_id(self):
        """Returns the ID of the account this transaction affects"""
        if self.bill_id:
            return self.bill_id
        elif self.account_id:
            return self.account_id
        return None

    def get_change_amount_for_account(self):
        """
        Returns the change amount this transaction makes to its associated account
        Positive = money going into account, Negative = money coming out of account
        """
        if not self.affects_account:
            return 0.0

        if self.is_saving:
            # Saving transactions: positive amount = money going INTO account
            return self.amount
        elif self.is_bill_pay:
            # Bill payment: positive amount = money coming OUT of bill account
            return -self.amount

        # Other transaction types don't directly affect account balances
        return 0.0