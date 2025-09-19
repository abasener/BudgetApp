"""
Account History models for tracking all account balance changes
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.database import Base


class AccountHistory(Base):
    """
    Universal history tracking for all account types (Bills and Savings)
    Each account gets its own set of history entries
    """
    __tablename__ = "account_history"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign key relationships
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True, index=True)
    account_id = Column(Integer, nullable=False, index=True)  # Can reference bills.id or accounts.id
    account_type = Column(String, nullable=False, index=True)  # "bill" or "savings"

    # History tracking fields
    change_amount = Column(Float, nullable=False)  # Positive or negative dollar change
    running_total = Column(Float, nullable=False)  # Cumulative balance after this change
    transaction_date = Column(Date, nullable=False)  # Date of the change (from transaction)

    # Description for non-transaction entries (like starting balances)
    description = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    transaction = relationship("Transaction", foreign_keys=[transaction_id], back_populates="history_entries")

    def __repr__(self):
        tx_info = f"tx_id={self.transaction_id}" if self.transaction_id else "no_tx"
        return f"<AccountHistory({self.account_type}:{self.account_id}, change=${self.change_amount:.2f}, total=${self.running_total:.2f}, {tx_info})>"

    @classmethod
    def create_starting_balance_entry(cls, account_id: int, account_type: str,
                                    starting_balance: float, date=None):
        """Create the initial balance entry for an account"""
        from datetime import date as date_class
        if date is None:
            date = date_class.today()

        return cls(
            transaction_id=None,  # No transaction for starting balance
            account_id=account_id,
            account_type=account_type,
            change_amount=starting_balance,
            running_total=starting_balance,
            transaction_date=date,
            description=f"Starting balance for {account_type} account"
        )

    @classmethod
    def create_transaction_entry(cls, account_id: int, account_type: str,
                               transaction_id: int, change_amount: float,
                               previous_total: float, transaction_date):
        """Create a history entry from a transaction"""
        new_total = previous_total + change_amount

        return cls(
            transaction_id=transaction_id,
            account_id=account_id,
            account_type=account_type,
            change_amount=change_amount,
            running_total=new_total,
            transaction_date=transaction_date,
            description=None  # Description comes from the transaction
        )


class AccountHistoryManager:
    """
    Helper class for managing account history operations
    Provides common functionality for both Bills and Savings accounts
    """

    def __init__(self, db_session):
        self.db = db_session

    def get_account_history(self, account_id: int, account_type: str):
        """Get all history entries for an account, ordered by date"""
        return self.db.query(AccountHistory).filter(
            AccountHistory.account_id == account_id,
            AccountHistory.account_type == account_type
        ).order_by(AccountHistory.transaction_date, AccountHistory.id).all()

    def get_current_balance(self, account_id: int, account_type: str) -> float:
        """Get the current balance for an account from history"""
        latest_entry = self.db.query(AccountHistory).filter(
            AccountHistory.account_id == account_id,
            AccountHistory.account_type == account_type
        ).order_by(AccountHistory.transaction_date.desc(), AccountHistory.id.desc()).first()

        return latest_entry.running_total if latest_entry else 0.0

    def _get_balance_at_date(self, account_id: int, account_type: str, target_date) -> float:
        """Get the balance as of a specific date (latest entry on or before that date)"""
        latest_entry = self.db.query(AccountHistory).filter(
            AccountHistory.account_id == account_id,
            AccountHistory.account_type == account_type,
            AccountHistory.transaction_date <= target_date
        ).order_by(AccountHistory.transaction_date.desc(), AccountHistory.id.desc()).first()

        return latest_entry.running_total if latest_entry else 0.0

    def add_transaction_change(self, account_id: int, account_type: str,
                             transaction_id: int, change_amount: float, transaction_date):
        """Add a new history entry for a transaction"""
        # Get balance as of the transaction date (not the absolute latest)
        balance_at_date = self._get_balance_at_date(account_id, account_type, transaction_date)

        # Create new history entry
        history_entry = AccountHistory.create_transaction_entry(
            account_id=account_id,
            account_type=account_type,
            transaction_id=transaction_id,
            change_amount=change_amount,
            previous_total=balance_at_date,
            transaction_date=transaction_date
        )

        self.db.add(history_entry)
        self.db.flush()  # Get the ID without committing

        # Update all subsequent entries' running totals
        self._update_running_totals_from_entry(history_entry, change_amount)

        return history_entry

    def update_transaction_change(self, transaction_id: int, new_change_amount: float, new_date):
        """Update a history entry when its transaction is modified"""
        # Find the history entry for this transaction
        history_entry = self.db.query(AccountHistory).filter(
            AccountHistory.transaction_id == transaction_id
        ).first()

        if not history_entry:
            raise ValueError(f"No history entry found for transaction {transaction_id}")

        # Calculate the difference in change amount
        old_change = history_entry.change_amount
        change_difference = new_change_amount - old_change

        # Update this entry and all subsequent entries in the same account
        self._update_running_totals_from_entry(history_entry, change_difference)

        # Update the entry details
        history_entry.change_amount = new_change_amount
        history_entry.transaction_date = new_date
        history_entry.running_total = history_entry.running_total  # Already updated above

    def delete_transaction_change(self, transaction_id: int):
        """Remove a history entry when its transaction is deleted"""
        history_entry = self.db.query(AccountHistory).filter(
            AccountHistory.transaction_id == transaction_id
        ).first()

        if not history_entry:
            return  # Already deleted or never existed

        # Update all subsequent entries to remove this change
        change_to_remove = -history_entry.change_amount  # Reverse the change
        self._update_running_totals_from_entry(history_entry, change_to_remove, skip_current=True)

        # Delete the entry
        self.db.delete(history_entry)

    def _update_running_totals_from_entry(self, start_entry: AccountHistory,
                                        change_difference: float, skip_current: bool = False):
        """Update running totals for all entries after (and including) the start entry"""
        # Get all entries in the same account and recalculate from the start entry forward
        all_entries = self.db.query(AccountHistory).filter(
            AccountHistory.account_id == start_entry.account_id,
            AccountHistory.account_type == start_entry.account_type
        ).order_by(AccountHistory.transaction_date, AccountHistory.id).all()

        # Find the position of the start entry in chronological order
        start_index = None
        for i, entry in enumerate(all_entries):
            if entry.id == start_entry.id:
                start_index = i
                break

        if start_index is None:
            return  # Entry not found

        # Recalculate running totals from this point forward
        for i in range(start_index + (1 if skip_current else 0), len(all_entries)):
            # Get the previous entry's running total
            prev_total = all_entries[i-1].running_total if i > 0 else 0.0
            # Calculate new running total
            all_entries[i].running_total = prev_total + all_entries[i].change_amount

    def initialize_account_history(self, account_id: int, account_type: str,
                                 starting_balance: float = 0.0, start_date=None):
        """Initialize history for a new account with starting balance"""
        # Check if history already exists
        existing = self.get_account_history(account_id, account_type)
        if existing:
            raise ValueError(f"History already exists for {account_type} account {account_id}")

        # Create starting balance entry
        starting_entry = AccountHistory.create_starting_balance_entry(
            account_id=account_id,
            account_type=account_type,
            starting_balance=starting_balance,
            date=start_date
        )

        self.db.add(starting_entry)
        self.db.flush()
        return starting_entry

    def recalculate_account_history(self, account_id: int, account_type: str):
        """Recalculate all running totals for an account (useful for fixing data issues)"""
        entries = self.get_account_history(account_id, account_type)

        running_total = 0.0
        for entry in entries:
            running_total += entry.change_amount
            entry.running_total = running_total

        self.db.flush()
        return entries