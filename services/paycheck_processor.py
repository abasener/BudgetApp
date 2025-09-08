"""
Paycheck Processor - Handles bi-weekly paycheck logic and rollover handling
Based on the NewWeekFlowChart.png flowchart
"""

from typing import Dict, List, Optional, Tuple
from datetime import date, timedelta
from dataclasses import dataclass

from models import get_db, Week, Transaction, Account, Bill, TransactionType
from services.transaction_manager import TransactionManager


@dataclass
class PaycheckSplit:
    """Result of paycheck splitting logic"""
    gross_paycheck: float
    bills_deducted: float  
    automatic_savings: float
    remaining_for_weeks: float
    week1_allocation: float
    week2_allocation: float


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
    
    def process_new_paycheck(self, paycheck_amount: float, paycheck_date: date) -> PaycheckSplit:
        """
        Process a new bi-weekly paycheck according to the flowchart logic
        
        Flow:
        1. Start with gross paycheck
        2. Deduct bills (based on bi-weekly savings requirements)
        3. Deduct automatic savings
        4. Split remainder between Week 1 and Week 2
        """
        
        # Step 1: Calculate bills to deduct (bi-weekly portion)
        bills_deducted = self.calculate_bills_deduction()
        
        # Step 2: Calculate automatic savings (fixed percentage or amount)
        automatic_savings = self.calculate_automatic_savings(paycheck_amount)
        
        # Step 3: Calculate remaining for weeks
        remaining_for_weeks = paycheck_amount - bills_deducted - automatic_savings
        
        # Step 4: Split between weeks (default 50/50, but could be customized)
        week1_allocation = remaining_for_weeks / 2
        week2_allocation = remaining_for_weeks / 2
        
        # Create the paycheck split result
        split = PaycheckSplit(
            gross_paycheck=paycheck_amount,
            bills_deducted=bills_deducted,
            automatic_savings=automatic_savings,
            remaining_for_weeks=remaining_for_weeks,
            week1_allocation=week1_allocation,
            week2_allocation=week2_allocation
        )
        
        # Record the transactions
        self.record_paycheck_transactions(paycheck_date, split)
        
        return split
    
    def calculate_bills_deduction(self) -> float:
        """Calculate how much to deduct for bills in this bi-weekly period"""
        bills = self.transaction_manager.get_all_bills()
        total_deduction = 0.0
        
        for bill in bills:
            # Calculate bi-weekly savings requirement
            # amount_to_save is typically the per-period amount the user wants to save
            bi_weekly_savings = bill.amount_to_save
            total_deduction += bi_weekly_savings
            
        return total_deduction
    
    def calculate_automatic_savings(self, paycheck_amount: float) -> float:
        """Calculate automatic savings (could be percentage or fixed amount)"""
        # For now, use 10% as automatic savings
        # This could be made configurable later
        return paycheck_amount * 0.10
    
    def record_paycheck_transactions(self, paycheck_date: date, split: PaycheckSplit):
        """Record all transactions from paycheck processing"""
        
        # Find current week to associate transactions
        current_week = self.transaction_manager.get_current_week()
        if not current_week:
            # Create a new week if none exists
            current_week = self.create_new_week(paycheck_date)
        
        # 1. Record the income transaction
        income_transaction = {
            "transaction_type": TransactionType.INCOME.value,
            "week_number": current_week.week_number,
            "amount": split.gross_paycheck,
            "date": paycheck_date,
            "description": "Bi-weekly paycheck"
        }
        self.transaction_manager.add_transaction(income_transaction)
        
        # 2. Record automatic savings transaction
        default_savings_account = self.transaction_manager.get_default_savings_account()
        if default_savings_account and split.automatic_savings > 0:
            savings_transaction = {
                "transaction_type": TransactionType.SAVING.value,
                "week_number": current_week.week_number,
                "amount": split.automatic_savings,
                "date": paycheck_date,
                "description": "Automatic savings deduction",
                "account_id": default_savings_account.id,
                "account_saved_to": default_savings_account.name
            }
            self.transaction_manager.add_transaction(savings_transaction)
            
            # Update account balance
            new_balance = default_savings_account.running_total + split.automatic_savings
            self.transaction_manager.update_account_balance(default_savings_account.id, new_balance)
        
        # 3. Update bill savings (allocate money for upcoming bills)
        self.update_bill_savings(current_week.week_number, paycheck_date)
    
    def update_bill_savings(self, week_number: int, transaction_date: date):
        """Update bill savings accounts based on bi-weekly deductions"""
        bills = self.transaction_manager.get_all_bills()
        
        for bill in bills:
            if bill.amount_to_save > 0:
                # Add to the bill's running total (money saved up for this bill)
                new_total = bill.running_total + bill.amount_to_save
                bill.running_total = new_total
                self.db.commit()
                
                # Optionally record a transaction for bill savings
                bill_saving_transaction = {
                    "transaction_type": TransactionType.SAVING.value,
                    "week_number": week_number,
                    "amount": bill.amount_to_save,
                    "date": transaction_date,
                    "description": f"Savings allocation for {bill.name}",
                    "bill_id": bill.id,
                    "bill_type": bill.bill_type
                }
                self.transaction_manager.add_transaction(bill_saving_transaction)
    
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
    
    def calculate_week_rollover(self, week_number: int) -> WeekRollover:
        """Calculate rollover amount for a completed week"""
        week = self.transaction_manager.get_week_by_number(week_number)
        if not week:
            raise ValueError(f"Week {week_number} not found")
        
        # Get week's allocated amount (from week.running_total)
        allocated_amount = week.running_total
        
        # Calculate total spent in this week (spending + bills, not including income/savings)
        week_transactions = self.transaction_manager.get_transactions_by_week(week_number)
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
        
        # Update target week's running total
        new_total = target_week.running_total + rollover.rollover_amount
        self.transaction_manager.update_week_total(target_week_number, new_total)
        
        # Record rollover transaction
        rollover_description = f"Rollover from Week {rollover.week_number}"
        if rollover.rollover_amount < 0:
            rollover_description = f"Deficit rollover from Week {rollover.week_number}"
        
        rollover_transaction = {
            "transaction_type": TransactionType.INCOME.value if rollover.rollover_amount > 0 else TransactionType.SPENDING.value,
            "week_number": target_week_number,
            "amount": abs(rollover.rollover_amount),
            "date": date.today(),
            "description": rollover_description,
            "category": "Rollover" if rollover.rollover_amount < 0 else None
        }
        self.transaction_manager.add_transaction(rollover_transaction)
    
    def rollover_to_savings(self, rollover: WeekRollover):
        """Roll over surplus/deficit to savings account (end of bi-weekly period)"""
        if rollover.rollover_amount <= 0:
            return  # Don't process negative rollovers to savings
        
        # Get default savings account
        savings_account = self.transaction_manager.get_default_savings_account()
        if not savings_account:
            print("Warning: No default savings account found for rollover")
            return
        
        # Update savings account balance
        new_balance = savings_account.running_total + rollover.rollover_amount
        self.transaction_manager.update_account_balance(savings_account.id, new_balance)
        
        # Record savings transaction
        savings_transaction = {
            "transaction_type": TransactionType.SAVING.value,
            "week_number": rollover.week_number,
            "amount": rollover.rollover_amount,
            "date": date.today(),
            "description": f"End-of-period surplus from Week {rollover.week_number}",
            "account_id": savings_account.id,
            "account_saved_to": savings_account.name
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