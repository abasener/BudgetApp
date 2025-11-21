"""
Reimbursement model for tracking expenses awaiting reimbursement
Used for work travel, personal loans to friends, etc.
These are NOT included in budget calculations - they're for tracking only.
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.sql import func
from enum import Enum
from models.database import Base


class ReimbursementState(Enum):
    """State enum for tracking reimbursement lifecycle"""
    PENDING = "pending"      # Purchased, not yet submitted
    SUBMITTED = "submitted"  # Submitted for reimbursement
    REIMBURSED = "reimbursed"  # Money received
    PARTIAL = "partial"      # Partially reimbursed
    DENIED = "denied"        # Not getting reimbursed


class Reimbursement(Base):
    """
    Reimbursement tracking model
    Completely separate from main transaction system - used for tracking only
    """
    __tablename__ = "reimbursements"

    id = Column(Integer, primary_key=True, index=True)

    # === Core fields ===
    amount = Column(Float, nullable=False)  # Amount spent
    date = Column(Date, nullable=False, index=True)  # Purchase date
    state = Column(String, nullable=False, default=ReimbursementState.PENDING.value)  # Current state

    # === Description fields ===
    notes = Column(String)  # User description of expense
    category = Column(String)  # Category tag (e.g., "Meals", "Hotel", "Transportation")
    location = Column(String)  # Location/trip tag (e.g., "Spain", "Florida", "Conference2024")

    # === Lifecycle dates (auto-populated when state changes) ===
    submitted_date = Column(Date, nullable=True)  # When submitted for reimbursement
    reimbursed_date = Column(Date, nullable=True)  # When money was received

    # === Timestamps ===
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Reimbursement(id={self.id}, amount=${self.amount:.2f}, state={self.state}, date={self.date}, location={self.location})>"

    # === Helper properties ===
    @property
    def is_pending(self):
        return self.state == ReimbursementState.PENDING.value

    @property
    def is_submitted(self):
        return self.state == ReimbursementState.SUBMITTED.value

    @property
    def is_reimbursed(self):
        return self.state == ReimbursementState.REIMBURSED.value

    @property
    def is_partial(self):
        return self.state == ReimbursementState.PARTIAL.value

    @property
    def is_denied(self):
        return self.state == ReimbursementState.DENIED.value

    @property
    def is_complete(self):
        """Returns True if reimbursement process is complete (reimbursed or denied)"""
        return self.state in [ReimbursementState.REIMBURSED.value, ReimbursementState.DENIED.value]

    @property
    def status_display(self):
        """Returns user-friendly status string"""
        status_map = {
            ReimbursementState.PENDING.value: "Pending Submission",
            ReimbursementState.SUBMITTED.value: "Awaiting Payment",
            ReimbursementState.REIMBURSED.value: "Reimbursed",
            ReimbursementState.PARTIAL.value: "Partially Reimbursed",
            ReimbursementState.DENIED.value: "Denied"
        }
        return status_map.get(self.state, self.state)
