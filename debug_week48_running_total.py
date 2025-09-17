"""
Debug Week 48 running_total vs what it should be
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Week, Transaction
from services.transaction_manager import TransactionManager

def debug_week48_running_total():
    """Debug Week 48 running_total"""
    print("=== DEBUGGING WEEK 48 RUNNING_TOTAL ===")

    tm = TransactionManager()
    try:
        # Get Week 48
        week48 = tm.get_week_by_number(48)
        if not week48:
            print("Week 48 not found")
            return
            
        print(f"Week 48 current running_total: ${week48.running_total:.2f}")
        
        # Get all income transactions for Week 48
        all_transactions = tm.get_all_transactions()
        week48_income = [
            t for t in all_transactions 
            if t.week_number == 48 and t.is_income
        ]
        
        print(f"\nWeek 48 income transactions:")
        total_income = 0
        for t in week48_income:
            print(f"  {t.date}: ${t.amount:.2f} - {t.description}")
            total_income += t.amount
        
        print(f"Total Week 48 income: ${total_income:.2f}")
        
        # Check if rollover from Week 47 exists
        week47_rollover = [
            t for t in week48_income 
            if "rollover from Week 47" in (t.description or "").lower()
        ]
        
        print(f"\nWeek 47 rollover to Week 48:")
        rollover_amount = 0
        for t in week47_rollover:
            print(f"  {t.date}: ${t.amount:.2f} - {t.description}")
            rollover_amount += t.amount
        
        print(f"Week 47 rollover amount: ${rollover_amount:.2f}")
        
        # Calculate what Week 48 running_total should be
        print(f"\n=== WHAT WEEK 48 RUNNING_TOTAL SHOULD BE ===")
        
        # Week 48 should start with base allocation + Week 47 rollover
        # Base allocation should be half of (paycheck - bill allocations)
        
        # Get pay period data
        weeks = tm.get_all_weeks()
        week47 = next((w for w in weeks if w.week_number == 47), None)
        
        period_income = [
            t for t in all_transactions 
            if week47.start_date <= t.date <= week48.end_date 
            and t.is_income and "paycheck" in (t.description or "").lower()
        ]
        
        period_bill_savings = [
            t for t in all_transactions 
            if week47.start_date <= t.date <= week48.end_date 
            and t.is_saving and t.bill_id is not None
        ]
        
        total_paycheck = sum(t.amount for t in period_income)
        total_bill_allocations = sum(t.amount for t in period_bill_savings)
        available_for_weeks = total_paycheck - total_bill_allocations
        base_allocation = available_for_weeks / 2
        
        expected_week48_total = base_allocation + rollover_amount
        
        print(f"Base allocation per week: ${base_allocation:.2f}")
        print(f"Week 47 rollover: ${rollover_amount:.2f}")
        print(f"Expected Week 48 running_total: ${expected_week48_total:.2f}")
        print(f"Actual Week 48 running_total: ${week48.running_total:.2f}")
        print(f"Difference: ${expected_week48_total - week48.running_total:.2f}")
        
        if abs(expected_week48_total - week48.running_total) > 0.01:
            print(f"PROBLEM: Week 48 running_total is not including the rollover!")
            print(f"This explains why the rollover calculation is wrong.")
            print(f"The running_total should be updated when rollover income is added.")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    debug_week48_running_total()
