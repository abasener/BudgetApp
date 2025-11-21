"""
Reimbursement Manager - CRUD operations for reimbursement tracking
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from models import get_db, Reimbursement, ReimbursementState


class ReimbursementManager:
    """Manager class for reimbursement operations"""

    def __init__(self):
        self.db = get_db()

    def close(self):
        """Close database connection"""
        self.db.close()

    # === CREATE ===

    def add_reimbursement(
        self,
        amount: float,
        date: date,
        notes: str = "",
        category: str = "",
        location: str = "",
        state: str = ReimbursementState.PENDING.value
    ) -> Reimbursement:
        """
        Add a new reimbursement entry
        Auto-updates submitted_date and reimbursed_date based on state
        """
        reimbursement = Reimbursement(
            amount=amount,
            date=date,
            notes=notes,
            category=category,
            location=location,
            state=state
        )

        # Auto-set dates based on initial state
        if state == ReimbursementState.SUBMITTED.value:
            reimbursement.submitted_date = datetime.now().date()
        elif state in [ReimbursementState.REIMBURSED.value, ReimbursementState.PARTIAL.value]:
            reimbursement.submitted_date = datetime.now().date()
            reimbursement.reimbursed_date = datetime.now().date()

        self.db.add(reimbursement)
        self.db.commit()
        self.db.refresh(reimbursement)

        return reimbursement

    # === READ ===

    def get_all_reimbursements(self, sort_by: str = "date", ascending: bool = False) -> List[Reimbursement]:
        """
        Get all reimbursements

        Args:
            sort_by: Field to sort by (date, amount, state, category, location)
            ascending: Sort direction (False = newest first for dates)
        """
        query = self.db.query(Reimbursement)

        # Map sort fields
        sort_fields = {
            "date": Reimbursement.date,
            "amount": Reimbursement.amount,
            "state": Reimbursement.state,
            "category": Reimbursement.category,
            "location": Reimbursement.location
        }

        sort_field = sort_fields.get(sort_by, Reimbursement.date)

        if ascending:
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))

        return query.all()

    def get_reimbursement_by_id(self, reimbursement_id: int) -> Optional[Reimbursement]:
        """Get reimbursement by ID"""
        return self.db.query(Reimbursement).filter(Reimbursement.id == reimbursement_id).first()

    def get_reimbursements_by_state(self, state: str) -> List[Reimbursement]:
        """Get all reimbursements with a specific state"""
        return self.db.query(Reimbursement).filter(Reimbursement.state == state).order_by(desc(Reimbursement.date)).all()

    def get_reimbursements_by_location(self, location: str) -> List[Reimbursement]:
        """Get all reimbursements for a specific location/trip"""
        return self.db.query(Reimbursement).filter(Reimbursement.location == location).order_by(desc(Reimbursement.date)).all()

    def get_reimbursements_by_category(self, category: str) -> List[Reimbursement]:
        """Get all reimbursements in a specific category"""
        return self.db.query(Reimbursement).filter(Reimbursement.category == category).order_by(desc(Reimbursement.date)).all()

    def get_reimbursements_by_date_range(self, start_date: date, end_date: date) -> List[Reimbursement]:
        """Get reimbursements within a date range"""
        return self.db.query(Reimbursement).filter(
            and_(
                Reimbursement.date >= start_date,
                Reimbursement.date <= end_date
            )
        ).order_by(desc(Reimbursement.date)).all()

    def get_pending_reimbursements(self) -> List[Reimbursement]:
        """Get all pending reimbursements (not yet submitted)"""
        return self.get_reimbursements_by_state(ReimbursementState.PENDING.value)

    def get_outstanding_reimbursements(self) -> List[Reimbursement]:
        """Get all reimbursements awaiting payment (submitted or partial)"""
        return self.db.query(Reimbursement).filter(
            or_(
                Reimbursement.state == ReimbursementState.SUBMITTED.value,
                Reimbursement.state == ReimbursementState.PARTIAL.value
            )
        ).order_by(desc(Reimbursement.date)).all()

    def get_unique_categories(self) -> List[str]:
        """Get list of all unique categories used"""
        categories = self.db.query(Reimbursement.category).distinct().all()
        return [cat[0] for cat in categories if cat[0]]  # Filter out None/empty

    def get_unique_locations(self) -> List[str]:
        """Get list of all unique locations/tags used"""
        locations = self.db.query(Reimbursement.location).distinct().all()
        return [loc[0] for loc in locations if loc[0]]  # Filter out None/empty

    # === UPDATE ===

    def update_reimbursement(
        self,
        reimbursement_id: int,
        updates: Dict[str, Any]
    ) -> Optional[Reimbursement]:
        """
        Update a reimbursement
        Auto-updates submitted_date and reimbursed_date when state changes

        Args:
            reimbursement_id: ID of reimbursement to update
            updates: Dictionary of fields to update
        """
        reimbursement = self.get_reimbursement_by_id(reimbursement_id)
        if not reimbursement:
            return None

        old_state = reimbursement.state

        # Apply updates
        for key, value in updates.items():
            if hasattr(reimbursement, key):
                setattr(reimbursement, key, value)

        # Auto-update dates if state changed
        if "state" in updates and updates["state"] != old_state:
            new_state = updates["state"]

            # Moving to SUBMITTED: set submitted_date if not already set
            if new_state == ReimbursementState.SUBMITTED.value:
                if not reimbursement.submitted_date:
                    reimbursement.submitted_date = datetime.now().date()

            # Moving to REIMBURSED or PARTIAL: set both dates if not already set
            elif new_state in [ReimbursementState.REIMBURSED.value, ReimbursementState.PARTIAL.value]:
                if not reimbursement.submitted_date:
                    reimbursement.submitted_date = datetime.now().date()
                if not reimbursement.reimbursed_date:
                    reimbursement.reimbursed_date = datetime.now().date()

        self.db.commit()
        self.db.refresh(reimbursement)

        return reimbursement

    def change_state(self, reimbursement_id: int, new_state: str) -> Optional[Reimbursement]:
        """
        Change reimbursement state (convenience method)
        Auto-updates dates
        """
        return self.update_reimbursement(reimbursement_id, {"state": new_state})

    # === DELETE ===

    def delete_reimbursement(self, reimbursement_id: int) -> bool:
        """Delete a reimbursement"""
        reimbursement = self.get_reimbursement_by_id(reimbursement_id)
        if reimbursement:
            self.db.delete(reimbursement)
            self.db.commit()
            return True
        return False

    def delete_multiple_reimbursements(self, reimbursement_ids: List[int]) -> int:
        """
        Delete multiple reimbursements
        Returns number of reimbursements deleted
        """
        count = 0
        for reimbursement_id in reimbursement_ids:
            if self.delete_reimbursement(reimbursement_id):
                count += 1
        return count

    # === STATISTICS ===

    def get_total_pending_amount(self) -> float:
        """Get total amount of pending reimbursements"""
        pending = self.get_pending_reimbursements()
        return sum(r.amount for r in pending)

    def get_total_outstanding_amount(self) -> float:
        """Get total amount of outstanding reimbursements (submitted but not paid)"""
        outstanding = self.get_outstanding_reimbursements()
        return sum(r.amount for r in outstanding)

    def get_total_reimbursed_amount(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> float:
        """
        Get total amount that has been reimbursed
        Optionally filter by date range
        """
        query = self.db.query(Reimbursement).filter(Reimbursement.state == ReimbursementState.REIMBURSED.value)

        if start_date:
            query = query.filter(Reimbursement.reimbursed_date >= start_date)
        if end_date:
            query = query.filter(Reimbursement.reimbursed_date <= end_date)

        reimbursements = query.all()
        return sum(r.amount for r in reimbursements)
