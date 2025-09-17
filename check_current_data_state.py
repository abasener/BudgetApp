"""
Check what data exists now vs what we had before
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def check_current_data_state():
    """Check current data state"""
    print("=== CHECKING CURRENT DATA STATE ===")

    tm = TransactionManager()
    try:
        accounts = tm.get_all_accounts()
        weeks = tm.get_all_weeks()
        all_transactions = tm.get_all_transactions()
        
        print(f"Current state:")
        print(f"  Accounts: {len(accounts)}")
        print(f"  Weeks: {len(weeks)}")
        print(f"  Transactions: {len(all_transactions)}")
        
        # Check if we're back to the small dataset
        if len(weeks) <= 10:
            print(f"\n🔍 DIAGNOSIS: You're back to a small dataset!")
            print(f"   This explains why balance history is all zeros.")
            print(f"   Likely cause: 'Reset Test Data' was used from the UI")
            
        # Show week numbers
        if weeks:
            week_numbers = sorted([w.week_number for w in weeks])
            print(f"  Week numbers: {week_numbers}")
            
        # Check Safety Saving transactions
        safety_account = next((a for a in accounts if a.name == "Safety Saving"), None)
        if safety_account:
            safety_transactions = tm.get_transactions_by_account(safety_account.id)
            print(f"  Safety Saving transactions: {len(safety_transactions)}")
            
            if safety_transactions:
                print(f"  Recent transactions:")
                for t in safety_transactions[-5:]:
                    print(f"    {t.date}: ${t.amount:.2f} - {t.description}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    check_current_data_state()
