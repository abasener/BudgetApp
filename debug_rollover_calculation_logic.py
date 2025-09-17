"""
Debug the rollover calculation logic to see why Week 2 current amount isn't being transferred correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Transaction, Week
from services.transaction_manager import TransactionManager

def debug_rollover_calculation_logic():
    """Debug the rollover calculation step by step"""
    print("=== DEBUGGING ROLLOVER CALCULATION LOGIC ===")

    tm = TransactionManager()
    try:
        # Focus on Pay Period 24 (Weeks 47-48)
        weeks = tm.get_all_weeks()
        week47 = next((w for w in weeks if w.week_number == 47), None)
        week48 = next((w for w in weeks if w.week_number == 48), None)
        
        if not (week47 and week48):
            print("Could not find weeks 47 and 48")
            return
            
        print(f"Week 47: {week47.start_date} to {week47.end_date}")
        print(f"Week 48: {week48.start_date} to {week48.end_date}")
        
        # Get all transactions
        all_transactions = tm.get_all_transactions()
        
        # 1. Check the paycheck and bill allocations for the pay period
        print(f"\n=== 1. PAY PERIOD SETUP ===")
        
        # Income for the period (should be one paycheck)
        period_income = [
            t for t in all_transactions 
            if week47.start_date <= t.date <= week48.end_date and t.is_income
            and "paycheck" in (t.description or "").lower()
        ]
        
        total_paycheck = sum(t.amount for t in period_income)
        print(f"Paycheck total: ${total_paycheck:.2f}")
        
        # Bill allocations for the period
        period_bill_savings = [
            t for t in all_transactions 
            if week47.start_date <= t.date <= week48.end_date 
            and t.is_saving and t.bill_id is not None
        ]
        
        total_bill_allocations = sum(t.amount for t in period_bill_savings)
        print(f"Bill allocations: ${total_bill_allocations:.2f}")
        
        # Money available for 2 weeks
        available_for_weeks = total_paycheck - total_bill_allocations
        print(f"Available for weeks: ${available_for_weeks:.2f}")
        print(f"Per week allocation: ${available_for_weeks / 2:.2f}")
        
        # 2. Check Week 47 transactions and rollover
        print(f"\n=== 2. WEEK 47 ANALYSIS ===")
        
        week47_transactions = [
            t for t in all_transactions 
            if week47.start_date <= t.date <= week47.end_date
        ]
        
        week47_spending = [t for t in week47_transactions if t.is_spending and not ("rollover" in (t.description or "").lower())]
        week47_spending_total = sum(t.amount for t in week47_spending)
        
        print(f"Week 47 spending: ${week47_spending_total:.2f}")
        
        week47_starting = available_for_weeks / 2
        week47_current = week47_starting - week47_spending_total
        
        print(f"Week 47 starting: ${week47_starting:.2f}")
        print(f"Week 47 current (rollover): ${week47_current:.2f}")
        
        # Check if there's a Week 47 rollover transaction
        week47_rollover_tx = [
            t for t in all_transactions 
            if "rollover" in (t.description or "").lower() and "Week 47" in (t.description or "")
        ]
        
        print(f"Week 47 rollover transactions: {len(week47_rollover_tx)}")
        for tx in week47_rollover_tx:
            print(f"  {tx.date}: ${tx.amount:.2f} - {tx.description}")
        
        # 3. Check Week 48 transactions and final rollover
        print(f"\n=== 3. WEEK 48 ANALYSIS ===")
        
        week48_transactions = [
            t for t in all_transactions 
            if week48.start_date <= t.date <= week48.end_date
        ]
        
        week48_spending = [t for t in week48_transactions if t.is_spending and not ("rollover" in (t.description or "").lower())]
        week48_spending_total = sum(t.amount for t in week48_spending)
        
        print(f"Week 48 spending: ${week48_spending_total:.2f}")
        
        week48_starting = (available_for_weeks / 2) + week47_current  # Week 47 rollover
        week48_current = week48_starting - week48_spending_total
        
        print(f"Week 48 starting (base + week47 rollover): ${week48_starting:.2f}")
        print(f"Week 48 current (should go to savings): ${week48_current:.2f}")
        
        # Check what actually happened with Week 48 rollover
        week48_rollover_tx = [
            t for t in all_transactions 
            if "End-of-period" in (t.description or "") and "Week 48" in (t.description or "")
        ]
        
        print(f"Week 48 rollover transactions: {len(week48_rollover_tx)}")
        for tx in week48_rollover_tx:
            print(f"  {tx.date}: ${tx.amount:.2f} - {tx.description}")
            print(f"  Account: {tx.account.name if tx.account else 'Unknown'}")
        
        # 4. Compare expected vs actual
        print(f"\n=== 4. EXPECTED VS ACTUAL ===")
        
        expected_savings_transfer = week48_current
        actual_savings_transfer = sum(tx.amount for tx in week48_rollover_tx)
        
        print(f"Expected transfer to savings: ${expected_savings_transfer:.2f}")
        print(f"Actual transfer to savings: ${actual_savings_transfer:.2f}")
        print(f"Difference: ${expected_savings_transfer - actual_savings_transfer:.2f}")
        
        if abs(expected_savings_transfer - actual_savings_transfer) > 0.01:
            print(f"PROBLEM: Rollover calculation is wrong!")
            print(f"  Week 48 current amount should directly transfer to savings")
            print(f"  But the rollover system calculated a different amount")
            
            # Check if the rollover system is using a different calculation
            print(f"\n=== 5. ROLLOVER SYSTEM CALCULATION ===")
            print("The rollover system might be using a different formula")
            print("Let's see what it thinks the rollover should be...")
            
            # Try to reverse-engineer what the rollover system calculated
            # If it shows -$22.80, what inputs could lead to that?
            
            print(f"Actual rollover: ${actual_savings_transfer:.2f}")
            print(f"This suggests the rollover system calculated Week 48 current as: ${actual_savings_transfer:.2f}")
            print(f"But we calculated it as: ${expected_savings_transfer:.2f}")
            print(f"The difference is: ${expected_savings_transfer - actual_savings_transfer:.2f}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    debug_rollover_calculation_logic()
