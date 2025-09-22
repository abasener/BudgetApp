"""
Check if balance history exists and is being built properly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def check_balance_history_state():
    """Check current balance history state"""
    print("=== CHECKING BALANCE HISTORY STATE ===")

    tm = TransactionManager()
    try:
        accounts = tm.get_all_accounts()
        weeks = tm.get_all_weeks()
        
        print(f"Found {len(accounts)} accounts and {len(weeks)} weeks")
        
        for account in accounts:
            print(f"\n{account.name}:")
            print(f"  running_total: ${account.running_total:.2f}")
            print(f"  balance_history exists: {account.balance_history is not None}")
            
            if account.balance_history is not None:
                history = account.get_balance_history_copy()
                print(f"  balance_history length: {len(history)}")
                print(f"  balance_history type: {type(account.balance_history)}")
                print(f"  First 5 entries: {[f'${v:.2f}' for v in history[:5]]}")
                print(f"  Last 5 entries: {[f'${v:.2f}' for v in history[-5:]]}")
            else:
                print(f"  balance_history is None!")

        # Check if there are any savings transactions
        all_transactions = tm.get_all_transactions()
        savings_transactions = [t for t in all_transactions if t.is_saving and t.account_id]
        print(f"\nFound {len(savings_transactions)} savings transactions")
        
        if savings_transactions:
            print("Recent savings transactions:")
            for t in savings_transactions[-5:]:
                print(f"  {t.date}: ${t.amount:.2f} to {t.account.name if t.account else 'Unknown'}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    check_balance_history_state()
