"""
Check current database state of balance history
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def check_balance_state():
    """Check current state of balance history in database"""
    print("=== CHECKING BALANCE STATE ===")

    tm = TransactionManager()
    try:
        # Get fresh account data directly from database
        account = tm.db.query(Account).filter(Account.name == "Safety Saving").first()
        
        if account:
            print(f"Safety Saving account:")
            print(f"  running_total: ${account.running_total:.2f}")
            print(f"  balance_history length: {len(account.balance_history) if account.balance_history else 0}")
            
            if account.balance_history:
                history = list(account.balance_history)
                print(f"  First 5 entries: {[f'${v:.2f}' for v in history[:5]]}")
                print(f"  Last 5 entries: {[f'${v:.2f}' for v in history[-5:]]}")
                print(f"  Final value: ${history[-1]:.2f}")
                print(f"  Length: {len(history)}")
            else:
                print("  No balance history")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    check_balance_state()
