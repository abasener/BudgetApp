"""
Test the rollover and savings calculation fixes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def test_savings_calculations():
    """Test that savings calculations show balance changes correctly"""
    print("=== TESTING SAVINGS CALCULATION FIXES ===")

    tm = TransactionManager()
    try:
        accounts = tm.get_all_accounts()
        
        print("Testing pay period 24 (the one you mentioned):")
        current_pay_period_index = 24  # Pay period 24
        
        for account in accounts:
            if account.name == "Safety Saving":  # Focus on the problematic account
                print(f"\n{account.name}:")
                print(f"  Current running_total: ${account.running_total:.2f}")
                
                history = account.get_balance_history_copy()
                if history and len(history) > current_pay_period_index:
                    starting_index = current_pay_period_index - 1  # 23
                    final_index = current_pay_period_index  # 24
                    
                    starting_balance = history[starting_index]
                    final_balance = history[final_index]
                    amount_change = final_balance - starting_balance
                    
                    print(f"  Starting balance (index {starting_index}): ${starting_balance:.2f}")
                    print(f"  Final balance (index {final_index}): ${final_balance:.2f}")
                    print(f"  Amount change: ${amount_change:.2f}")
                    print(f"  Expected: $226.96 (your target)")
                    print(f"  Match: {'YES' if abs(amount_change - 226.96) < 1.0 else 'NO'}")
                else:
                    print(f"  Insufficient history data (need index {current_pay_period_index})")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    test_savings_calculations()
