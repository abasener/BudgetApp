"""
Paycheck Processor - Handles bi-weekly paycheck logic and rollover handling
Based on the NewWeekFlowChart.png flowchart
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
        bills_deducted = self.calculate_bills_deduction(paycheck_amount)
        
        # Step 2: Calculate automatic savings (fixed percentage or amount)
        automatic_savings = self.calculate_automatic_savings(paycheck_amount)
        
        # Step 3: Calculate account auto-savings (happens after bills)
        account_auto_savings = self.calculate_account_auto_savings()
        
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
        
        # Record the transactions
        self.record_paycheck_transactions(paycheck_date, split)
        
        # Check for and process any pending rollovers after adding new paycheck
        self.check_and_process_rollovers()

        # Record balance history for all accounts at the end of this pay period
        self.record_balance_history()

        return split
    
    def calculate_bills_deduction(self, paycheck_amount: float = 0.0) -> float:
        """Calculate how much to deduct for bills in this bi-weekly period"""
        bills = self.transaction_manager.get_all_bills()
        total_deduction = 0.0
        
        for bill in bills:
            # Handle percentage-based vs fixed amount savings
            if bill.amount_to_save < 1.0 and bill.amount_to_save > 0:
                # Percentage-based saving (e.g., 0.1 = 10% of paycheck)
                bi_weekly_savings = bill.amount_to_save * paycheck_amount
            else:
                # Fixed dollar amount saving
                bi_weekly_savings = bill.amount_to_save
            
            total_deduction += bi_weekly_savings
            
        return total_deduction
    
    def calculate_account_auto_savings(self) -> float:
        """Calculate auto-savings for accounts (happens after bills)"""
        accounts = self.transaction_manager.get_all_accounts()
        total_auto_savings = 0.0
        
        for account in accounts:
            if hasattr(account, 'auto_save_amount') and account.auto_save_amount > 0:
                total_auto_savings += account.auto_save_amount
                
        return total_auto_savings
    
    def calculate_automatic_savings(self, paycheck_amount: float) -> float:
        """Calculate automatic savings - REMOVED: No hardcoded automatic savings"""
        # No automatic savings - only account-specific auto-savings
        return 0.0
    
    def record_paycheck_transactions(self, paycheck_date: date, split: PaycheckSplit):
        """Record all transactions from paycheck processing"""

        print("=" * 60)
        print("DEBUG: Starting paycheck transaction recording")
        print(f"DEBUG: Paycheck date: {paycheck_date}")
        print(f"DEBUG: Week start date: {split.week_start_date}")
        print(f"DEBUG: Week 1 allocation: ${split.week1_allocation}")
        print(f"DEBUG: Week 2 allocation: ${split.week2_allocation}")

        # Create both weeks for the bi-weekly period
        # Always create new weeks for a new paycheck based on the week_start date

        # Create first week starting from week_start date
        week_start = split.week_start_date  # This should be passed from the dialog
        print(f"DEBUG: Creating Week 1 starting {week_start}")
        current_week = self.create_new_week(week_start)

        # Create the second week for bi-weekly period
        next_week_start = week_start + timedelta(days=7)  # Start date for week 2
        print(f"DEBUG: Creating Week 2 starting {next_week_start}")
        next_week = self.create_new_week(next_week_start)
        
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
        self.update_account_auto_savings(current_week.week_number, paycheck_date)
        
        # 3. Update bill savings (allocate money for upcoming bills)
        self.update_bill_savings(current_week.week_number, paycheck_date, split.gross_paycheck)

        # 4. Update week allocations with the calculated amounts
        print(f"DEBUG: Setting Week {current_week.week_number} allocation to ${split.week1_allocation}")
        print(f"DEBUG: Setting Week {next_week.week_number} allocation to ${split.week2_allocation}")
        current_week.running_total = split.week1_allocation
        next_week.running_total = split.week2_allocation
        self.db.commit()

        print(f"DEBUG: Final Week {current_week.week_number}: ${current_week.running_total}")
        print(f"DEBUG: Final Week {next_week.week_number}: ${next_week.running_total}")
        print("DEBUG: Paycheck transaction recording completed")
        print("=" * 60)
    
    def update_bill_savings(self, week_number: int, transaction_date: date, paycheck_amount: float):
        """Update bill savings accounts based on bi-weekly deductions"""
        bills = self.transaction_manager.get_all_bills()

        for bill in bills:
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

                # Add to the bill's running total (money saved up for this bill)
                new_total = bill.running_total + actual_amount
                bill.running_total = new_total
                self.db.commit()

                # Record a transaction for bill savings with correct amount
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
                print(f"DEBUG: Bill savings - {bill.name}: ${actual_amount:.2f}")

    def update_account_auto_savings(self, week_number: int, transaction_date: date):
        """Update account auto-savings based on each account's auto_save_amount"""
        accounts = self.transaction_manager.get_all_accounts()

        for account in accounts:
            # Check if account has auto_save_amount attribute and it's > 0
            if hasattr(account, 'auto_save_amount') and account.auto_save_amount > 0:
                # Add to the account's running total
                new_balance = account.running_total + account.auto_save_amount
                self.transaction_manager.update_account_balance(account.id, new_balance)

                # Record a transaction for account auto-savings
                account_saving_transaction = {
                    "transaction_type": TransactionType.SAVING.value,
                    "week_number": week_number,
                    "amount": account.auto_save_amount,
                    "date": transaction_date,
                    "description": f"Auto-savings allocation for {account.name}",
                    "account_id": account.id,
                    "account_saved_to": account.name
                }
                self.transaction_manager.add_transaction(account_saving_transaction)
                print(f"DEBUG: Added ${account.auto_save_amount} to {account.name}")

    def create_new_week(self, start_date: date) -> Week:
        """Create a new week when processing paycheck"""
        # Find the highest week number and increment
        current_week = self.transaction_manager.get_current_week()
        next_week_number = (current_week.week_number + 1) if current_week else 1

        print(f"DEBUG: Creating new week {next_week_number} starting {start_date}")

        new_week = Week(
            week_number=next_week_number,
            start_date=start_date,
            end_date=start_date + timedelta(days=6),  # 7-day week
            running_total=0.0  # Will be updated when allocations are made
        )

        self.db.add(new_week)
        self.db.commit()
        self.db.refresh(new_week)

        print(f"DEBUG: Successfully created Week {new_week.week_number} (ID: {new_week.id})")
        return new_week
    
    def calculate_week_rollover(self, week_number: int) -> WeekRollover:
        """Calculate rollover amount for a completed week"""
        week = self.transaction_manager.get_week_by_number(week_number)
        if not week:
            raise ValueError(f"Week {week_number} not found")

        # Get week's transactions
        week_transactions = self.transaction_manager.get_transactions_by_week(week_number)

        # Calculate effective allocated amount (base allocation + income like rollovers)
        base_allocated_amount = week.running_total
        income_amount = sum(
            t.amount for t in week_transactions
            if t.transaction_type == TransactionType.INCOME.value
        )
        allocated_amount = base_allocated_amount + income_amount

        # Calculate total spent in this week (spending + bills, not including income/savings)
        spent_amount = sum(
            t.amount for t in week_transactions
            if t.transaction_type in [TransactionType.SPENDING.value, TransactionType.BILL_PAY.value]
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
            if existing_tx.transaction_type == TransactionType.INCOME.value:
                total_adjustment -= existing_tx.amount  # Remove previous positive rollover
            else:
                total_adjustment += existing_tx.amount  # Remove previous negative rollover

            self.db.delete(existing_tx)

        # Only create rollover transaction if there's an actual rollover amount
        # The transaction itself will automatically update the week's effective balance
        if rollover.rollover_amount == 0:
            return

        # Record new rollover transaction
        rollover_description = f"Rollover from Week {rollover.week_number}"
        if rollover.rollover_amount < 0:
            rollover_description = f"Deficit rollover from Week {rollover.week_number}"

        rollover_transaction = {
            "transaction_type": TransactionType.INCOME.value if rollover.rollover_amount > 0 else TransactionType.SPENDING.value,
            "week_number": target_week_number,
            "amount": abs(rollover.rollover_amount),
            "date": date.today(),
            "description": rollover_description,
            "category": "Rollover"
        }
        self.transaction_manager.add_transaction(rollover_transaction)

        # CASCADING: Reset target week's rollover flag so it gets recalculated
        # This is needed because the target week's surplus/deficit changed
        target_week.rollover_applied = False
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


        # Update default savings account balance with net adjustment
        old_balance = default_savings_account.running_total
        new_balance = old_balance + balance_adjustment
        self.transaction_manager.update_account_balance(default_savings_account.id, new_balance)

        # Verify the update worked
        updated_account = self.transaction_manager.get_default_savings_account()

        # Record new rollover transaction
        if rollover.rollover_amount > 0:
            # Positive rollover - money goes TO savings
            savings_transaction = {
                "transaction_type": TransactionType.SAVING.value,
                "week_number": rollover.week_number,
                "amount": rollover.rollover_amount,
                "date": date.today(),
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
                "date": date.today(),
                "description": f"End-of-period deficit from Week {rollover.week_number}",
                "account_id": default_savings_account.id,
                "account_saved_to": default_savings_account.name
            }

        self.transaction_manager.add_transaction(savings_transaction)
    
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
            print(f"Checking for pending rollovers... (iteration {iteration})")

            # Get all weeks that haven't had rollover applied yet
            weeks = self.db.query(Week).filter(Week.rollover_applied == False).order_by(Week.week_number).all()

            if not weeks:
                print("No rollovers needed")
                return True

            processed_any = False
            for week in weeks:
                # Check if this week is "complete" (has a subsequent week, or is more than 7 days old)
                next_week = self.db.query(Week).filter(Week.week_number == week.week_number + 1).first()
                week_ended = date.today() > week.end_date

                if next_week or week_ended:
                    # This week should have rollover processed
                    try:
                        # Determine if this is week 1 or week 2 of a pay period
                        is_week1_of_period = (week.week_number % 2) == 1

                        if is_week1_of_period and next_week:
                            # Week 1: rollover to Week 2
                            print(f"Processing Week {week.week_number} rollover to Week {next_week.week_number}")
                            self.process_week_rollover(week.week_number, next_week.week_number)
                        elif not is_week1_of_period:
                            # Week 2: rollover to savings
                            print(f"Processing Week {week.week_number} rollover to savings")
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

        print("Rollover processing completed")
        return True

    def record_balance_history(self):
        """Record current account balances in balance history at the end of pay period"""
        accounts = self.transaction_manager.get_all_accounts()

        for account in accounts:
            # Ensure running_total and balance history are in sync
            current_balance = account.running_total

            # Append current balance to balance history
            account.append_period_balance(current_balance)

            # Verify the balance history was updated correctly
            history = account.get_balance_history_copy()
            if history and abs(history[-1] - current_balance) > 0.01:
                print(f"WARNING: Balance history sync issue for {account.name}")
                print(f"  Running total: ${current_balance:.2f}")
                print(f"  Last history entry: ${history[-1]:.2f}")

            print(f"DEBUG: Recorded balance history for {account.name}: ${current_balance:.2f}")

        self.db.commit()
        print("DEBUG: Balance history recorded for all accounts")