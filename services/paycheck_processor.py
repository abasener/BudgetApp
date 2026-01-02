"""
Paycheck Processor - Handles bi-weekly paycheck logic and rollover handling
Based on the NewWeekFlowChart.png flowchart

CRITICAL UNDERSTANDING: ROLLOVER FLOW IS SIMPLE
================================================

Money flows in exactly TWO directions:
1. Week 1 → Week 2 (one rollover transaction per pay period)
2. Week 2 → Savings (one rollover transaction per pay period)

NO OTHER ROLLOVERS EXIST!

How it works:
- Paycheck arrives and is split 50/50 between Week 1 and Week 2
- Week 1 allocation goes into Week.running_total (base only, no rollover)
- Week 2 allocation goes into Week.running_total (base only, no rollover)
- Rollover transactions are created IMMEDIATELY and UPDATED LIVE as spending changes
- When Week 1 spending happens, Week 1→Week 2 rollover updates automatically
- When Week 2 spending happens, Week 2→Savings rollover updates automatically

Example:
- Paycheck: $4237.50
- Bills: $3328.59
- Spendable: $908.91
- Week 1 base: $454.46 (set in Week.running_total)
- Week 2 base: $454.46 (set in Week.running_total)
- Week 1 spending: $141.70
- Week 1 rollover to Week 2: $312.76 (separate transaction)
- Week 2 total: $454.46 + $312.76 = $767.22 (base + rollover)
- Week 2 spending: $0.00
- Week 2 rollover to Savings: $767.22 (separate transaction)

IMPORTANT:
- Week.running_total NEVER includes rollovers
- Rollovers are stored as separate transactions
- Display logic ADDS rollover transactions to base for "Starting" amount
- Live updates happen automatically via recalculate_period_rollovers()
"""

from typing import Dict, List, Optional, Tuple
from datetime import date, timedelta
from dataclasses import dataclass

from models import get_db, Week, Transaction, Account, Bill, TransactionType
from sqlalchemy import or_
from services.transaction_manager import TransactionManager


@dataclass
class PaycheckSplit:
    """Result of paycheck splitting logic"""
    gross_paycheck: float
    bills_deducted: float  
    automatic_savings: float
    account_auto_savings: float
    remaining_for_weeks: float
    week1_allocation: float
    week2_allocation: float
    week_start_date: date


@dataclass
class WeekRollover:
    """Week rollover calculation result"""
    week_number: int
    allocated_amount: float
    spent_amount: float
    remaining_amount: float
    rollover_amount: float  # Positive = surplus, Negative = deficit


class PaycheckProcessor:
    def __init__(self):
        self.transaction_manager = TransactionManager()
        self.db = get_db()
        
    def close(self):
        """Close database connections"""
        self.transaction_manager.close()
        self.db.close()
    
    def process_new_paycheck(self, paycheck_amount: float, paycheck_date: date, week_start_date: date) -> PaycheckSplit:
        """
        Process a new bi-weekly paycheck according to the flowchart logic
        
        Flow:
        1. Start with gross paycheck
        2. Deduct bills (based on bi-weekly savings requirements)
        3. Deduct automatic savings
        4. Split remainder between Week 1 and Week 2
        """
        
        # Step 1: Calculate bills to deduct (bi-weekly portion, including percentage-based)
        # Only active bills on week_start_date are included
        bills_deducted = self.calculate_bills_deduction(paycheck_amount, week_start_date)

        # Step 2: Calculate automatic savings (fixed percentage or amount)
        automatic_savings = self.calculate_automatic_savings(paycheck_amount)

        # Step 3: Calculate account auto-savings (happens after bills)
        # Only active accounts on week_start_date are included
        account_auto_savings = self.calculate_account_auto_savings(paycheck_amount, week_start_date)
        
        # Step 4: Calculate remaining for weeks
        remaining_for_weeks = paycheck_amount - bills_deducted - automatic_savings - account_auto_savings
        
        # Step 5: Split between weeks (default 50/50, but could be customized)
        week1_allocation = remaining_for_weeks / 2
        week2_allocation = remaining_for_weeks / 2
        
        # Create the paycheck split result
        split = PaycheckSplit(
            gross_paycheck=paycheck_amount,
            bills_deducted=bills_deducted,
            automatic_savings=automatic_savings,
            account_auto_savings=account_auto_savings,
            remaining_for_weeks=remaining_for_weeks,
            week1_allocation=week1_allocation,
            week2_allocation=week2_allocation,
            week_start_date=week_start_date
        )
        
        # Record the transactions (this now creates immediate live rollover transactions)
        self.record_paycheck_transactions(paycheck_date, split)

        self.db.commit()

        # NOTE: Live rollover system is now active - rollovers are created immediately
        # and updated dynamically as spending changes. No need to wait for week end.
        # self.check_and_process_rollovers()  # DISABLED - using live rollover system instead

        # Account balance history is automatically maintained through AccountHistory transactions

        return split
    
    def calculate_bills_deduction(self, paycheck_amount: float = 0.0, week_start_date: date = None) -> float:
        """
        Calculate how much to deduct for bills in this bi-weekly period.

        Only includes bills that are ACTIVE on the week_start_date.
        Inactive bills are skipped - no auto-allocation happens for them.

        Args:
            paycheck_amount: The gross paycheck amount (for percentage-based savings)
            week_start_date: The start date of the pay period (for activation check)
                            If None, uses today's date
        """
        if week_start_date is None:
            week_start_date = date.today()

        bills = self.transaction_manager.get_all_bills()
        total_deduction = 0.0

        for bill in bills:
            # Skip inactive bills - they don't receive auto-allocations
            if not bill.is_active_on(week_start_date):
                continue

            # Handle percentage-based vs fixed amount savings
            if bill.amount_to_save < 1.0 and bill.amount_to_save > 0:
                # Percentage-based saving (e.g., 0.1 = 10% of paycheck)
                bi_weekly_savings = bill.amount_to_save * paycheck_amount
            else:
                # Fixed dollar amount saving
                bi_weekly_savings = bill.amount_to_save

            total_deduction += bi_weekly_savings

        return total_deduction
    
    def calculate_account_auto_savings(self, paycheck_amount: float = 0, week_start_date: date = None) -> float:
        """
        Calculate auto-savings for accounts (happens after bills).

        Only includes accounts that are ACTIVE on the week_start_date.
        Inactive accounts are skipped - no auto-allocation happens for them.

        Args:
            paycheck_amount: The gross paycheck amount (for percentage-based savings)
            week_start_date: The start date of the pay period (for activation check)
                            If None, uses today's date
        """
        if week_start_date is None:
            week_start_date = date.today()

        accounts = self.transaction_manager.get_all_accounts()
        total_auto_savings = 0.0

        for account in accounts:
            # Skip inactive accounts - they don't receive auto-allocations
            if not account.is_active_on(week_start_date):
                continue

            if hasattr(account, 'auto_save_amount') and account.auto_save_amount > 0:
                # Handle percentage-based vs fixed amount auto-saves
                if account.auto_save_amount < 1.0 and account.auto_save_amount > 0:
                    # Percentage-based auto-save (e.g., 0.1 = 10% of paycheck)
                    auto_save_amount = account.auto_save_amount * paycheck_amount
                else:
                    # Fixed dollar amount auto-save
                    auto_save_amount = account.auto_save_amount

                total_auto_savings += auto_save_amount

        return total_auto_savings
    
    def calculate_automatic_savings(self, paycheck_amount: float) -> float:
        """Calculate automatic savings - REMOVED: No hardcoded automatic savings"""
        # No automatic savings - only account-specific auto-savings
        return 0.0
    
    def record_paycheck_transactions(self, paycheck_date: date, split: PaycheckSplit):
        """Record all transactions from paycheck processing"""

        print("=" * 60)

        # Create both weeks for the bi-weekly period
        # Always create new weeks for a new paycheck based on the week_start date

        # Create first week starting from week_start date
        week_start = split.week_start_date  # This should be passed from the dialog
        current_week = self.create_new_week(week_start)

        # Create the second week for bi-weekly period
        next_week_start = week_start + timedelta(days=7)  # Start date for week 2
        next_week = self.create_new_week(next_week_start)

        # Load any pre-existing transactions for these weeks
        self._assign_existing_transactions_to_weeks(current_week)
        self._assign_existing_transactions_to_weeks(next_week)

        # Set appropriate rollover flags for new bi-weekly period
        # Week 1 (odd): Can process rollover immediately when complete
        # Week 2 (even): Should only process rollover at end of bi-weekly period
        is_week1_odd = (current_week.week_number % 2) == 1
        is_week2_even = (next_week.week_number % 2) == 0

        if is_week2_even:
            # Week 2 should not process rollover until bi-weekly period is complete
            next_week.rollover_applied = True  # Prevent premature rollover processing
            self.db.commit()

        # 1. Record the income transaction
        income_transaction = {
            "transaction_type": TransactionType.INCOME.value,
            "week_number": current_week.week_number,
            "amount": split.gross_paycheck,
            "date": paycheck_date,
            "description": "Bi-weekly paycheck"
        }
        self.transaction_manager.add_transaction(income_transaction)
        
        # 2. Record account auto-savings transactions
        self.update_account_auto_savings(current_week.week_number, paycheck_date, split.gross_paycheck)

        # 3. Update bill savings (allocate money for upcoming bills)
        # Disable automatic rollover recalculation during bill processing to prevent multiple triggers
        self.transaction_manager.set_auto_rollover_disabled(True)
        self.update_bill_savings(current_week.week_number, paycheck_date, split.gross_paycheck)
        # Re-enable automatic rollover recalculation
        self.transaction_manager.set_auto_rollover_disabled(False)

        # 4. Update week allocations with the calculated amounts
        current_week.running_total = split.week1_allocation
        next_week.running_total = split.week2_allocation
        self.db.commit()

        # 5. IMMEDIATELY create live rollover transactions
        # Week 1 -> Week 2 rollover (full Week 1 budget, will update as spending happens)
        self._create_live_week1_to_week2_rollover(current_week, next_week)

        # Week 2 -> Emergency Fund rollover (full Week 1 + Week 2 budgets, will update as spending happens)
        self._create_live_week2_to_savings_rollover(current_week, next_week)

        print("=" * 60)
    
    def update_bill_savings(self, week_number: int, transaction_date: date, paycheck_amount: float):
        """
        Update bill savings accounts based on bi-weekly deductions.

        Only creates allocations for bills that are ACTIVE on the transaction_date.
        Inactive bills are skipped - no auto-allocation transaction is created.
        Manual bill payments can still be made to inactive bills via the UI.
        """
        bills = self.transaction_manager.get_all_bills()

        for bill in bills:
            # Skip inactive bills - they don't receive auto-allocations
            # (User can still manually pay bills or transfer money to inactive bill accounts)
            if not bill.is_active_on(transaction_date):
                continue

            if bill.amount_to_save > 0:
                # Calculate actual amount using same logic as calculate_bills_deduction
                if bill.amount_to_save < 1.0 and bill.amount_to_save > 0:
                    # Percentage-based saving (e.g., 0.1 = 10% of paycheck)
                    actual_amount = bill.amount_to_save * paycheck_amount
                    description = f"Savings allocation for {bill.name} ({bill.amount_to_save*100:.1f}% of paycheck)"
                else:
                    # Fixed dollar amount saving
                    actual_amount = bill.amount_to_save
                    description = f"Savings allocation for {bill.name}"

                # Record a transaction for bill savings with correct amount
                # The TransactionManager will automatically update AccountHistory
                bill_saving_transaction = {
                    "transaction_type": TransactionType.SAVING.value,
                    "week_number": week_number,
                    "amount": actual_amount,
                    "date": transaction_date,
                    "description": description,
                    "bill_id": bill.id,
                    "bill_type": bill.bill_type
                }
                self.transaction_manager.add_transaction(bill_saving_transaction)

    def update_account_auto_savings(self, week_number: int, transaction_date: date, paycheck_amount: float = 0):
        """
        Update account auto-savings based on each account's auto_save_amount.

        Only creates allocations for accounts that are ACTIVE on the transaction_date.
        Inactive accounts are skipped - no auto-allocation transaction is created.
        Manual transfers can still be made to/from inactive accounts via the UI.
        """
        accounts = self.transaction_manager.get_all_accounts()

        for account in accounts:
            # Skip inactive accounts - they don't receive auto-allocations
            # (User can still manually transfer money to/from inactive accounts)
            if not account.is_active_on(transaction_date):
                continue

            # Check if account has auto_save_amount attribute and it's > 0
            if hasattr(account, 'auto_save_amount') and account.auto_save_amount > 0:
                # Calculate actual amount using same logic as calculate_account_auto_savings
                if account.auto_save_amount < 1.0 and account.auto_save_amount > 0:
                    # Percentage-based auto-save (e.g., 0.1 = 10% of paycheck)
                    actual_amount = account.auto_save_amount * paycheck_amount
                    description = f"Auto-savings allocation for {account.name} ({account.auto_save_amount*100:.1f}% of paycheck)"
                else:
                    # Fixed dollar amount auto-save
                    actual_amount = account.auto_save_amount
                    description = f"Auto-savings allocation for {account.name}"

                # Record a transaction for account auto-savings
                # The TransactionManager will automatically update AccountHistory
                account_saving_transaction = {
                    "transaction_type": TransactionType.SAVING.value,
                    "week_number": week_number,
                    "amount": actual_amount,
                    "date": transaction_date,
                    "description": description,
                    "account_id": account.id,
                    "account_saved_to": account.name
                }
                self.transaction_manager.add_transaction(account_saving_transaction)

    def create_new_week(self, start_date: date) -> Week:
        """Create a new week when processing paycheck"""
        # Find the highest week number and increment
        current_week = self.transaction_manager.get_current_week()
        next_week_number = (current_week.week_number + 1) if current_week else 1


        new_week = Week(
            week_number=next_week_number,
            start_date=start_date,
            end_date=start_date + timedelta(days=6),  # 7-day week
            running_total=0.0  # Will be updated when allocations are made
        )

        self.db.add(new_week)
        self.db.commit()
        self.db.refresh(new_week)

        return new_week

    def _assign_existing_transactions_to_weeks(self, week: Week):
        """
        Find and assign any pre-existing transactions to this newly created week.

        This handles the case where a user added transactions for a future date
        before the paycheck was processed. When the paycheck is added, those
        transactions need to be assigned to the appropriate week.
        """
        # Get all transactions that don't have a week number assigned (week_number is None)
        # and fall within this week's date range
        orphaned_transactions = self.db.query(Transaction).filter(
            Transaction.week_number == None,
            Transaction.date >= week.start_date,
            Transaction.date <= week.end_date
        ).all()

        if orphaned_transactions:
            print(f"Found {len(orphaned_transactions)} pre-existing transaction(s) for Week {week.week_number}")

            for txn in orphaned_transactions:
                txn.week_number = week.week_number
                print(f"  Assigned transaction ID {txn.id} (${txn.amount}, {txn.date}) to Week {week.week_number}")

            self.db.commit()

    def calculate_week_rollover(self, week_number: int) -> WeekRollover:
        """Calculate rollover amount for a completed week"""
        week = self.transaction_manager.get_week_by_number(week_number)
        if not week:
            raise ValueError(f"Week {week_number} not found")

        # Get week's transactions
        week_transactions = self.transaction_manager.get_transactions_by_week(week_number)

        # Calculate effective allocated amount (base allocation + ALL rollover amounts, both positive and negative)
        base_allocated_amount = week.running_total
        rollover_adjustments = sum(
            t.amount for t in week_transactions
            if t.transaction_type == TransactionType.ROLLOVER.value
        )
        allocated_amount = base_allocated_amount + rollover_adjustments

        # Calculate total spent in this week (spending only, not bill pays)
        # Bill pays come from bill accounts, not weekly spending money
        spent_amount = sum(
            t.amount for t in week_transactions
            if t.transaction_type == TransactionType.SPENDING.value
        )

        # Calculate remaining and rollover
        remaining_amount = allocated_amount - spent_amount
        rollover_amount = remaining_amount  # Positive = surplus, Negative = deficit
        
        return WeekRollover(
            week_number=week_number,
            allocated_amount=allocated_amount,
            spent_amount=spent_amount,
            remaining_amount=remaining_amount,
            rollover_amount=rollover_amount
        )
    
    def process_week_rollover(self, week_number: int, target_week_number: Optional[int] = None) -> WeekRollover:
        """
        Process rollover from one week to another (or to savings)
        
        Logic from flowchart:
        - If Week 1 has surplus/deficit, it rolls to Week 2
        - If Week 2 has surplus/deficit, it rolls to savings account
        """
        rollover = self.calculate_week_rollover(week_number)
        
        if rollover.rollover_amount == 0:
            return rollover  # No rollover needed
        
        # Determine where to roll over
        if target_week_number:
            # Roll over to specific week
            self.rollover_to_week(rollover, target_week_number)
        else:
            # Roll over to default savings (end of bi-weekly period)
            self.rollover_to_savings(rollover)
        
        return rollover
    
    def rollover_to_week(self, rollover: WeekRollover, target_week_number: int):
        """Roll over surplus/deficit to another week"""
        target_week = self.transaction_manager.get_week_by_number(target_week_number)
        if not target_week:
            raise ValueError(f"Target week {target_week_number} not found")

        # REPROCESSING: Remove any existing rollover transactions from source week to target week
        existing_rollover_transactions = self.db.query(Transaction).filter(
            Transaction.week_number == target_week_number,
            Transaction.description.like(f"%rollover from Week {rollover.week_number}"),
        ).all()

        # Calculate how much to adjust target week total
        total_adjustment = rollover.rollover_amount
        for existing_tx in existing_rollover_transactions:
            # Reverse the effect of the old rollover transaction
            # For ROLLOVER type, the amount already has the correct sign, so just subtract it
            total_adjustment -= existing_tx.amount

            self.db.delete(existing_tx)

        # Only create rollover transaction if there's an actual rollover amount
        # The transaction itself will automatically update the week's effective balance
        if rollover.rollover_amount == 0:
            return

        # Record new rollover transaction
        rollover_description = f"Rollover from Week {rollover.week_number}"
        if rollover.rollover_amount < 0:
            rollover_description = f"Deficit rollover from Week {rollover.week_number}"

        # Get the end date of the source week for proper transaction dating
        source_week = self.transaction_manager.get_week_by_number(rollover.week_number)
        transaction_date = source_week.end_date if source_week else date.today()

        rollover_transaction = {
            "transaction_type": TransactionType.ROLLOVER.value,
            "week_number": target_week_number,
            "amount": rollover.rollover_amount,  # Keep original sign
            "date": transaction_date,
            "description": rollover_description,
            "account_id": None,  # Week-to-week rollovers don't affect specific accounts
            "category": None  # No longer using category for rollover identification
        }
        # Disable auto-rollover to prevent infinite loops during rollover processing
        self.transaction_manager.set_auto_rollover_disabled(True)
        self.transaction_manager.add_transaction(rollover_transaction)
        self.transaction_manager.set_auto_rollover_disabled(False)

        # CASCADING: Reset target week's rollover flag so it gets recalculated
        # This is needed because the target week's surplus/deficit changed
        # But only if the target week is actually complete (for Week 2s)
        is_target_week1_of_period = (target_week.week_number % 2) == 1

        if is_target_week1_of_period:
            # Target is Week 1, always reset (Week 1 can rollover immediately when Week 2 exists)
            target_week.rollover_applied = False
        else:
            # Target is Week 2, only reset if bi-weekly period is complete
            week3_exists = self.db.query(Week).filter(Week.week_number == target_week.week_number + 1).first()
            week_ended = date.today() > target_week.end_date
            if week3_exists or week_ended:
                target_week.rollover_applied = False
            else:
                # Otherwise, leave Week 2 as rollover_applied = True to prevent premature processing
                pass

        self.transaction_manager.db.commit()
    
    def rollover_to_savings(self, rollover: WeekRollover):
        """Roll over surplus/deficit to default savings account (end of bi-weekly period)"""

        if rollover.rollover_amount == 0:
            return  # Nothing to process

        # Get the default savings account (is_default_save = True)
        default_savings_account = self.transaction_manager.get_default_savings_account()

        if not default_savings_account:
            print("Warning: No default savings account found for rollover")
            return


        # REPROCESSING: Remove any existing rollover-to-savings transactions from this week
        # Look for both positive and negative rollover transactions
        existing_savings_transactions = self.db.query(Transaction).filter(
            Transaction.week_number == rollover.week_number,
            Transaction.account_id == default_savings_account.id,
            or_(
                Transaction.description.like(f"End-of-period surplus from Week {rollover.week_number}"),
                Transaction.description.like(f"End-of-period deficit from Week {rollover.week_number}")
            )
        ).all()


        # Calculate how much to adjust savings account balance
        balance_adjustment = rollover.rollover_amount
        for existing_tx in existing_savings_transactions:
            # All rollover transactions are now SAVING type, just reverse their effect
            balance_adjustment -= existing_tx.amount  # Remove previous rollover (works for both + and -)
            self.db.delete(existing_tx)


        # Note: Account balance will be updated automatically when the rollover transaction is created
        # No need to manually update account balance here since transaction creation handles it

        # Record new rollover transaction
        # Get the end date of the week for proper transaction dating
        source_week = self.transaction_manager.get_week_by_number(rollover.week_number)
        transaction_date = source_week.end_date if source_week else date.today()

        if rollover.rollover_amount > 0:
            # Positive rollover - money goes TO savings
            savings_transaction = {
                "transaction_type": TransactionType.SAVING.value,
                "week_number": rollover.week_number,
                "amount": rollover.rollover_amount,
                "date": transaction_date,
                "description": f"End-of-period surplus from Week {rollover.week_number}",
                "account_id": default_savings_account.id,
                "account_saved_to": default_savings_account.name
            }
        else:
            # Negative rollover - money comes FROM savings to cover deficit
            # Use SAVING transaction with negative amount to decrease account balance
            savings_transaction = {
                "transaction_type": TransactionType.SAVING.value,
                "week_number": rollover.week_number,
                "amount": rollover.rollover_amount,  # Keep negative amount
                "date": transaction_date,
                "description": f"End-of-period deficit from Week {rollover.week_number}",
                "account_id": default_savings_account.id,
                "account_saved_to": default_savings_account.name
            }

        # Disable auto-rollover to prevent infinite loops during rollover processing
        self.transaction_manager.set_auto_rollover_disabled(True)
        self.transaction_manager.add_transaction(savings_transaction)
        self.transaction_manager.set_auto_rollover_disabled(False)

    def _create_live_week1_to_week2_rollover(self, week1: Week, week2: Week):
        """Create immediate Week 1 -> Week 2 rollover transaction (will update live as spending changes)"""
        # Check if rollover already exists for this direction
        existing_rollover = self.db.query(Transaction).filter(
            Transaction.transaction_type == TransactionType.ROLLOVER.value,
            Transaction.week_number == week2.week_number,
            Transaction.description.like(f"%Week {week1.week_number}%")
        ).first()

        if existing_rollover:
            return  # Already exists, don't create duplicate

        # Calculate Week 1's expected rollover (its full budget initially)
        week1_rollover = self.calculate_week_rollover(week1.week_number)

        if week1_rollover.rollover_amount == 0:
            return  # Nothing to rollover

        # Create rollover transaction dated to Week 1's end date
        rollover_description = f"Rollover from Week {week1.week_number}"
        if week1_rollover.rollover_amount < 0:
            rollover_description = f"Deficit rollover from Week {week1.week_number}"

        rollover_transaction = {
            "transaction_type": TransactionType.ROLLOVER.value,
            "week_number": week2.week_number,
            "amount": week1_rollover.rollover_amount,
            "date": week1.end_date,  # Dated to Week 1 end
            "description": rollover_description,
            "account_id": None,
            "category": None
        }

        self.transaction_manager.set_auto_rollover_disabled(True)
        self.transaction_manager.add_transaction(rollover_transaction)
        self.transaction_manager.set_auto_rollover_disabled(False)

    def _create_live_week2_to_savings_rollover(self, week1: Week, week2: Week):
        """Create immediate Week 2 -> Emergency Fund transaction (will update live as spending changes)"""
        default_savings_account = self.transaction_manager.get_default_savings_account()
        if not default_savings_account:
            print("Warning: No default savings account found for live rollover")
            return

        # Check if savings rollover already exists for this week
        existing_savings = self.db.query(Transaction).filter(
            Transaction.transaction_type == TransactionType.SAVING.value,
            Transaction.week_number == week2.week_number,
            Transaction.account_id == default_savings_account.id,
            Transaction.description.like(f"%Week {week2.week_number}%")
        ).first()

        if existing_savings:
            return  # Already exists, don't create duplicate

        # Calculate Week 2's expected rollover (Week 2 budget + Week 1 budget - Week 1 spending)
        # This is the total amount that will go to savings at the end
        week2_rollover = self.calculate_week_rollover(week2.week_number)

        if week2_rollover.rollover_amount == 0:
            return  # Nothing to rollover

        # Create savings transaction dated to Week 2's end date (future date - shows it's pending)
        savings_transaction = {
            "transaction_type": TransactionType.SAVING.value,
            "week_number": week2.week_number,
            "amount": week2_rollover.rollover_amount,
            "date": week2.end_date,  # FUTURE DATE - shows this is pending/in flux
            "description": f"End-of-period surplus from Week {week2.week_number}",
            "account_id": default_savings_account.id,
            "account_saved_to": default_savings_account.name
        }

        self.transaction_manager.set_auto_rollover_disabled(True)
        self.transaction_manager.add_transaction(savings_transaction)
        self.transaction_manager.set_auto_rollover_disabled(False)

    def get_current_pay_period_summary(self) -> Dict:
        """Get summary of current bi-weekly pay period"""
        current_week = self.transaction_manager.get_current_week()
        if not current_week:
            return {"error": "No current week found"}
        
        # Assume bi-weekly periods (Week 1 and Week 2 pairs)
        period_start_week = current_week.week_number - (current_week.week_number % 2)
        if period_start_week == 0:
            period_start_week = current_week.week_number
        
        week1_number = period_start_week
        week2_number = period_start_week + 1
        
        # Get summaries for both weeks
        week1_summary = self.transaction_manager.get_week_summary(week1_number)
        week2_summary = self.transaction_manager.get_week_summary(week2_number) if week2_number <= current_week.week_number else {}
        
        return {
            "period_weeks": [week1_number, week2_number],
            "week1": week1_summary,
            "week2": week2_summary,
            "current_week": current_week.week_number
        }
    
    def check_and_process_rollovers(self):
        """
        Check for weeks that need rollover processing and process them automatically.
        This should be called during app refresh or when adding new paychecks.
        Processes in a loop to handle cascading rollover updates.
        """
        max_iterations = 10  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Get all weeks that haven't had rollover applied yet
            weeks = self.db.query(Week).filter(Week.rollover_applied == False).order_by(Week.week_number).all()

            if not weeks:
                return True

            processed_any = False
            for week in weeks:
                # Check if this week is "complete" (has a subsequent week, or is more than 7 days old)
                next_week = self.db.query(Week).filter(Week.week_number == week.week_number + 1).first()
                week_ended = date.today() > week.end_date

                # For Week 2s, additional check: only process if bi-weekly period is actually complete
                is_week2_of_period = (week.week_number % 2) == 0
                if is_week2_of_period:
                    # Week 2 should only process if there's a Week 3 (next bi-weekly period started)
                    week3_exists = self.db.query(Week).filter(Week.week_number == week.week_number + 1).first()
                    if not (week3_exists or week_ended):
                        continue  # Skip this Week 2, it's not ready yet

                if next_week or week_ended:
                    # This week should have rollover processed
                    try:
                        # Determine if this is week 1 or week 2 of a pay period
                        is_week1_of_period = (week.week_number % 2) == 1

                        if is_week1_of_period and next_week:
                            # Week 1: rollover to Week 2
                            self.process_week_rollover(week.week_number, next_week.week_number)
                        elif not is_week1_of_period:
                            # Week 2: rollover to savings
                            self.process_week_rollover(week.week_number)

                        # Mark rollover as applied
                        week.rollover_applied = True
                        self.db.commit()
                        processed_any = True

                    except Exception as e:
                        print(f"Error processing rollover for Week {week.week_number}: {e}")
                        continue

            if not processed_any:
                # No more rollovers to process, exit the loop
                break

        return True



    def recalculate_period_rollovers(self, week_number: int):
        """
        Recalculate rollovers for the entire bi-weekly period containing the given week.
        This should be called whenever a transaction is added/updated/deleted in a week.
        """
        # Determine which bi-weekly period this week belongs to
        is_odd_week = (week_number % 2) == 1

        if is_odd_week:
            # Week 1 of a period (odd number)
            week1_number = week_number
            week2_number = week_number + 1
        else:
            # Week 2 of a period (even number)
            week1_number = week_number - 1
            week2_number = week_number

        # Get both weeks
        week1 = self.transaction_manager.get_week_by_number(week1_number)
        week2 = self.transaction_manager.get_week_by_number(week2_number)

        if not week1:
            return  # Week 1 doesn't exist, nothing to recalculate


        # Step 1: Remove existing rollover transactions for this period
        self._remove_period_rollover_transactions(week1_number, week2_number)

        # Step 2: Recalculate Week 1 rollover (to Week 2)
        if week2:  # Only if Week 2 exists
            week1_rollover = self.calculate_week_rollover(week1_number)
            if week1_rollover.rollover_amount != 0:
                self._create_rollover_transaction(week1_rollover, week2_number)

        # Step 3: Recalculate Week 2 rollover (to savings)
        if week2:
            week2_rollover = self.calculate_week_rollover(week2_number)
            if week2_rollover.rollover_amount != 0:
                self._create_rollover_to_savings_transaction(week2_rollover)

    def _remove_period_rollover_transactions(self, week1_number: int, week2_number: int):
        """Remove all rollover transactions for a bi-weekly period"""
        # Remove Week 1 -> Week 2 rollover transactions (more specific filter)
        week1_to_week2_rollovers = self.db.query(Transaction).filter(
            Transaction.transaction_type == TransactionType.ROLLOVER.value,
            Transaction.week_number == week2_number,
            Transaction.description.like(f"%rollover from Week {week1_number}")
        ).all()

        for tx in week1_to_week2_rollovers:
            self.transaction_manager.delete_transaction(tx.id)

        # Remove Week 2 -> savings rollover transactions (more specific filter)
        default_savings_account = self.transaction_manager.get_default_savings_account()
        if default_savings_account:
            week2_to_savings_rollovers = self.db.query(Transaction).filter(
                Transaction.transaction_type == TransactionType.SAVING.value,
                Transaction.week_number == week2_number,
                Transaction.account_id == default_savings_account.id,
                or_(
                    Transaction.description.like(f"End-of-period surplus from Week {week2_number}"),
                    Transaction.description.like(f"End-of-period deficit from Week {week2_number}")
                )
            ).all()

            for tx in week2_to_savings_rollovers:
                self.transaction_manager.delete_transaction(tx.id)

    def _create_rollover_transaction(self, rollover: WeekRollover, target_week_number: int):
        """Create a rollover transaction from one week to another"""
        rollover_description = f"Rollover from Week {rollover.week_number}"
        if rollover.rollover_amount < 0:
            rollover_description = f"Deficit rollover from Week {rollover.week_number}"

        # Get the end date of the source week for proper transaction dating
        source_week = self.transaction_manager.get_week_by_number(rollover.week_number)
        transaction_date = source_week.end_date if source_week else date.today()

        rollover_transaction = {
            "transaction_type": TransactionType.ROLLOVER.value,
            "week_number": target_week_number,
            "amount": rollover.rollover_amount,  # Keep original sign
            "date": transaction_date,
            "description": rollover_description,
            "account_id": None,  # Week-to-week rollovers don't affect specific accounts
            "category": None  # No longer using category for rollover identification
        }
        # Disable auto-rollover to prevent infinite loops during rollover processing
        self.transaction_manager.set_auto_rollover_disabled(True)
        self.transaction_manager.add_transaction(rollover_transaction)
        self.transaction_manager.set_auto_rollover_disabled(False)

    def _create_rollover_to_savings_transaction(self, rollover: WeekRollover):
        """Create a rollover transaction from a week to savings"""
        default_savings_account = self.transaction_manager.get_default_savings_account()
        if not default_savings_account:
            print("Warning: No default savings account found for rollover")
            return

        # Get the end date of the week for proper transaction dating
        source_week = self.transaction_manager.get_week_by_number(rollover.week_number)
        transaction_date = source_week.end_date if source_week else date.today()

        if rollover.rollover_amount > 0:
            # Positive rollover - money goes TO savings
            savings_transaction = {
                "transaction_type": TransactionType.SAVING.value,
                "week_number": rollover.week_number,
                "amount": rollover.rollover_amount,
                "date": transaction_date,
                "description": f"End-of-period surplus from Week {rollover.week_number}",
                "account_id": default_savings_account.id,
                "account_saved_to": default_savings_account.name
            }
        else:
            # Negative rollover - money comes FROM savings to cover deficit
            savings_transaction = {
                "transaction_type": TransactionType.SAVING.value,
                "week_number": rollover.week_number,
                "amount": rollover.rollover_amount,  # Keep negative amount
                "date": transaction_date,
                "description": f"End-of-period deficit from Week {rollover.week_number}",
                "account_id": default_savings_account.id,
                "account_saved_to": default_savings_account.name
            }

        # Disable auto-rollover to prevent infinite loops during rollover processing
        self.transaction_manager.set_auto_rollover_disabled(True)
        self.transaction_manager.add_transaction(savings_transaction)
        self.transaction_manager.set_auto_rollover_disabled(False)