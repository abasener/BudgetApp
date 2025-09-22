"""
Check what happened to the balance history we just rebuilt
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def check_what_happened():
    """Check the current state vs what we expect"""
    print("=== CHECKING WHAT HAPPENED TO BALANCE HISTORY ===")

    # Test with direct database access
    try:
        db = get_db()
        account = db.query(Account).filter(Account.name == "Safety Saving").first()
        
        if account:
            print(f"Direct DB access:")
            print(f"  running_total: ${account.running_total:.2f}")
            print(f"  balance_history exists: {account.balance_history is not None}")
            
            if account.balance_history:
                print(f"  balance_history type: {type(account.balance_history)}")
                print(f"  balance_history length: {len(account.balance_history)}")
                print(f"  First 5: {account.balance_history[:5]}")
                print(f"  Last 5: {account.balance_history[-5:]}")
            else:
                print(f"  balance_history is None!")
        
        db.close()
        
    except Exception as e:
        print(f"ERROR with direct DB: {e}")
        import traceback
        traceback.print_exc()

    # Test with TransactionManager
    print(f"\nTransactionManager access:")
    tm = TransactionManager()
    try:
        account = tm.db.query(Account).filter(Account.name == "Safety Saving").first()
        
        if account:
            print(f"  running_total: ${account.running_total:.2f}")
            print(f"  balance_history exists: {account.balance_history is not None}")
            
            if account.balance_history:
                print(f"  balance_history length: {len(account.balance_history)}")
                print(f"  First 5: {account.balance_history[:5]}")
                print(f"  Last 5: {account.balance_history[-5:]}")
                
                # Check if all zeros
                all_zeros = all(v == 0.0 for v in account.balance_history)
                print(f"  All zeros: {all_zeros}")
            else:
                print(f"  balance_history is None!")
    
    except Exception as e:
        print(f"ERROR with TM: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    check_what_happened()
