"""
Test the weekly view calculations after balance history rebuild
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def test_weekly_calculations():
    """Test weekly view style calculations"""
    print("=== TESTING WEEKLY CALCULATIONS ===")

    tm = TransactionManager()
    try:
        account = tm.db.query(Account).filter(Account.name == "Safety Saving").first()
        
        if account:
            history = account.get_balance_history_copy()
            print(f"Safety Saving balance history length: {len(history)}")
            print(f"Last 5 values: {[f'${v:.2f}' for v in history[-5:]]}")
            
            # Test Pay Period 24 calculations (your example)
            pay_period = 24
            starting_index = pay_period - 1  # 23 (0-based)
            final_index = pay_period  # 24
            
            if final_index < len(history):
                starting_balance = history[starting_index]
                final_balance = history[final_index]
                amount_change = final_balance - starting_balance
                
                print(f"\nPay Period {pay_period} calculation:")
                print(f"  Starting balance (index {starting_index}): ${starting_balance:.2f}")
                print(f"  Final balance (index {final_index}): ${final_balance:.2f}")
                print(f"  Amount change: ${amount_change:.2f}")
                print(f"  Expected by user: $226.96")
                print(f"  Difference: ${amount_change - 226.96:.2f}")
                
                # Check if it's now working correctly
                print(f"  Status: {'✓ WORKING' if abs(amount_change) > 0.01 else '✗ STILL BROKEN'}")
            else:
                print(f"Pay period {pay_period} index {final_index} exceeds history length {len(history)}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    test_weekly_calculations()
