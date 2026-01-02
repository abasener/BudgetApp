"""
Savings Account models
Now uses AccountHistory for balance tracking instead of manual running_total and balance_history arrays
Supports activation periods for seasonal/temporary accounts
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.database import Base
from typing import List, Optional
from datetime import date, datetime
import json


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

    # === Activation periods ===
    # JSON list of {start: "YYYY-MM-DD", end: "YYYY-MM-DD" or null} objects
    # Empty list or null = inactive; end=null means currently active
    activation_periods = Column(JSON, default=list)

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

    # === Activation period methods ===

    def _parse_date(self, date_str: str) -> date:
        """Parse a date string in ISO format to a date object"""
        if isinstance(date_str, date):
            return date_str
        return date.fromisoformat(date_str)

    def _get_periods_list(self) -> List[dict]:
        """Get activation_periods as a list, handling None/empty cases.
        Returns a COPY of the list to avoid SQLAlchemy mutation detection issues."""
        import copy
        if not self.activation_periods:
            return []
        if isinstance(self.activation_periods, str):
            try:
                return json.loads(self.activation_periods)
            except (json.JSONDecodeError, TypeError):
                return []
        # Return a deep copy so modifications are detected by SQLAlchemy
        return copy.deepcopy(self.activation_periods)

    def is_active_on(self, check_date: date) -> bool:
        """
        Check if account was active on a specific date.

        Args:
            check_date: The date to check (date object or ISO string)

        Returns:
            True if account was active on that date, False otherwise
        """
        if isinstance(check_date, str):
            check_date = self._parse_date(check_date)

        periods = self._get_periods_list()
        if not periods:
            return False

        for period in periods:
            start = self._parse_date(period['start'])
            end = self._parse_date(period['end']) if period.get('end') else None

            if start <= check_date:
                # End date is exclusive - if deactivated on a date, not active that day
                if end is None or check_date < end:
                    return True
        return False

    @property
    def is_currently_active(self) -> bool:
        """Check if account is currently active (as of today)"""
        return self.is_active_on(date.today())

    @property
    def current_period(self) -> Optional[dict]:
        """
        Get the current active period, or None if inactive.

        Returns:
            The period dict {start, end} if currently active, None otherwise
        """
        today = date.today()
        periods = self._get_periods_list()

        for period in periods:
            start = self._parse_date(period['start'])
            end = self._parse_date(period['end']) if period.get('end') else None

            if start <= today and (end is None or today <= end):
                return period
        return None

    def activate(self, start_date: date = None, db_session=None):
        """
        Start a new activation period.

        Handles same-day flapping: if the last period ended today (same-day deactivation),
        just reopen that period instead of creating a new one.

        Args:
            start_date: When to start the period (default: today)
            db_session: Database session to commit changes
        """
        if start_date is None:
            start_date = date.today()

        periods = self._get_periods_list()

        # Check for same-day flapping: if last period ended today, just reopen it
        if periods:
            last_period = periods[-1]
            if last_period.get('end'):
                last_end = self._parse_date(last_period['end'])
                if last_end == start_date:
                    # Same-day reactivation - just remove the end date
                    last_period['end'] = None
                    self.activation_periods = periods
                    if db_session:
                        db_session.commit()
                    return

        # Normal case: add new period
        periods.append({
            'start': start_date.isoformat(),
            'end': None
        })

        self.activation_periods = periods

        if db_session:
            db_session.commit()

    def deactivate(self, end_date: date = None, db_session=None):
        """
        End the current activation period.

        Handles same-day flapping: if the current period started today (same-day activation),
        remove that period entirely instead of closing it.

        Args:
            end_date: When to end the period (default: today)
            db_session: Database session to commit changes
        """
        if end_date is None:
            end_date = date.today()

        periods = self._get_periods_list()

        # Find the current open period
        for i, period in enumerate(periods):
            if period.get('end') is None:
                start = self._parse_date(period['start'])
                if start == end_date:
                    # Same-day deactivation - remove the period entirely
                    periods.pop(i)
                else:
                    # Normal case: close the period
                    period['end'] = end_date.isoformat()
                break

        self.activation_periods = periods

        if db_session:
            db_session.commit()

    def get_display_date_range(self) -> str:
        """
        Get human-readable date range for UI display.

        Returns:
            String like "Since Apr 2024" or "Apr 2024 - Aug 2024" or "Inactive"
        """
        periods = self._get_periods_list()

        if not periods:
            return "Never active"

        # Get most recent period
        last_period = periods[-1]
        start = self._parse_date(last_period['start'])
        end = self._parse_date(last_period['end']) if last_period.get('end') else None

        start_str = start.strftime("%b %Y")  # e.g., "Apr 2024"

        if end is None:
            return f"Since {start_str}"
        else:
            end_str = end.strftime("%b %Y")
            if start_str == end_str:
                return start_str  # Same month
            return f"{start_str} - {end_str}"

    def can_deactivate(self) -> tuple[bool, str]:
        """
        Check if this account can be deactivated.

        Returns:
            Tuple of (can_deactivate: bool, reason: str)
            If can_deactivate is False, reason explains why
        """
        if self.is_default_save:
            return False, "This is the default savings account. You must designate a different account as the default before deactivating this one."

        if not self.is_currently_active:
            return False, "This account is already inactive."

        return True, ""

