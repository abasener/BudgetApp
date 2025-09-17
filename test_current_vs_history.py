"""
Compare current running_total vs balance history to identify sync issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def test_current_vs_history():
    """Compare current state vs balance history"""
    print("=== COMPARING CURRENT VS HISTORY ===")

    tm = TransactionManager()
    try:
        account = tm.db.query(Account).filter(Account.name == "Safety Saving").first()
        
        if account:
            print(f"Safety Saving:")
            print(f"  Current running_total: ${account.running_total:.2f}")
            
            history = account.get_balance_history_copy()
            if history:
                print(f"  Balance history length: {len(history)}")
                print(f"  Last 10 history values: {[f'${v:.2f}' for v in history[-10:]]}")
                print(f"  Final history value: ${history[-1]:.2f}")
                print(f"  Difference: ${account.running_total - history[-1]:.2f}")
                
                # Check if this period should use current running_total
                weeks = tm.get_all_weeks()
                current_week_count = len(weeks)
                print(f"  Total weeks: {current_week_count}")
                print(f"  History covers pay periods: 1 to {len(history) - 1}")
                
                if current_week_count > len(history) - 1:
                    print(f"  Current period ({current_week_count}) exceeds history - should use running_total")
                else:
                    print(f"  Current period is covered by history")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    test_current_vs_history()
