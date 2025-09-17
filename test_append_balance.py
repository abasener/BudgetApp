"""
Test if append_period_balance works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def test_append_balance():
    """Test append_period_balance function"""
    print("=== TESTING APPEND_PERIOD_BALANCE ===")

    tm = TransactionManager()
    try:
        account = tm.db.query(Account).filter(Account.name == "Safety Saving").first()
        
        if account:
            print(f"Before append:")
            print(f"  running_total: ${account.running_total:.2f}")
            print(f"  balance_history: {account.get_balance_history_copy()}")
            
            # Test appending the current balance
            test_balance = account.running_total
            print(f"\nTesting append_period_balance with: ${test_balance:.2f}")
            
            account.append_period_balance(test_balance)
            tm.db.commit()
            
            print(f"\nAfter append:")
            print(f"  running_total: ${account.running_total:.2f}")
            print(f"  balance_history: {account.get_balance_history_copy()}")
            
            # Test appending a different balance
            test_balance2 = account.running_total + 100
            print(f"\nTesting append_period_balance with: ${test_balance2:.2f}")
            
            account.append_period_balance(test_balance2)
            tm.db.commit()
            
            print(f"\nAfter second append:")
            print(f"  running_total: ${account.running_total:.2f}")
            print(f"  balance_history: {account.get_balance_history_copy()}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    test_append_balance()
