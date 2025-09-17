"""
Debug what rollover transactions exist for weeks 47-48 (Pay Period 24)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Transaction
from services.transaction_manager import TransactionManager

def debug_week47_48_rollover():
    """Debug rollover for weeks 47-48"""
    print("=== DEBUGGING WEEKS 47-48 ROLLOVER ===")

    tm = TransactionManager()
    try:
        # Look for rollover transactions from weeks 47 and 48
        all_transactions = tm.get_all_transactions()
        
        week47_rollovers = [
            t for t in all_transactions 
            if t.description and "End-of-period" in t.description and "Week 47" in t.description
        ]
        
        week48_rollovers = [
            t for t in all_transactions 
            if t.description and "End-of-period" in t.description and "Week 48" in t.description
        ]
        
        print(f"Week 47 rollover transactions: {len(week47_rollovers)}")
        for t in week47_rollovers:
            print(f"  {t.date}: ${t.amount:.2f} -> {t.account.name if t.account else 'Unknown'}")
            print(f"    Description: {t.description}")
        
        print(f"\nWeek 48 rollover transactions: {len(week48_rollovers)}")
        for t in week48_rollovers:
            print(f"  {t.date}: ${t.amount:.2f} -> {t.account.name if t.account else 'Unknown'}")
            print(f"    Description: {t.description}")
        
        # Check if there should be rollovers based on our calculation
        print(f"\n=== EXPECTED ROLLOVER CALCULATION ===")
        
        # Get weeks data
        weeks = tm.get_all_weeks()
        week47 = next((w for w in weeks if w.week_number == 47), None)
        week48 = next((w for w in weeks if w.week_number == 48), None)
        
        if week47 and week48:
            print(f"Week 47: {week47.start_date} to {week47.end_date}")
            print(f"Week 48: {week48.start_date} to {week48.end_date}")
            
            # Get all transactions in this period
            period_transactions = [
                t for t in all_transactions 
                if week47.start_date <= t.date <= week48.end_date
            ]
            
            # Calculate period totals
            income_total = sum(t.amount for t in period_transactions if t.is_income)
            spending_total = sum(t.amount for t in period_transactions if t.is_spending)
            savings_total = sum(t.amount for t in period_transactions if t.is_saving)
            
            expected_rollover = income_total - spending_total - savings_total
            
            print(f"Pay Period 24 calculation:")
            print(f"  Income: ${income_total:.2f}")
            print(f"  Spending: ${spending_total:.2f}")
            print(f"  Savings (bills+accounts): ${savings_total:.2f}")
            print(f"  Expected rollover: ${expected_rollover:.2f}")
            
            # Check if we have rollover transactions matching this
            total_rollover_recorded = sum(t.amount for t in week47_rollovers + week48_rollovers)
            print(f"  Actual rollover transactions: ${total_rollover_recorded:.2f}")
            print(f"  Difference: ${expected_rollover - total_rollover_recorded:.2f}")
            
            if abs(expected_rollover - total_rollover_recorded) > 0.01:
                print(f"  ❌ MISMATCH: Expected rollover not recorded!")
                
                # Check if rollover processing was skipped
                print(f"\n=== DIAGNOSIS ===")
                if len(week47_rollovers) == 0 and len(week48_rollovers) == 0:
                    print("  No rollover transactions found - rollover processing may not have run")
                elif abs(total_rollover_recorded) < abs(expected_rollover):
                    print("  Partial rollover recorded - some processing may have failed")
                else:
                    print("  Rollover amount mismatch - calculation error or different logic")
            else:
                print(f"  ✅ Rollover matches expected amount")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    debug_week47_48_rollover()
