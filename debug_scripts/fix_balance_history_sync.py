"""
Fix balance history sync issues - update final balance history entry to match current running_total
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def fix_balance_history_sync():
    """Fix accounts where balance history final value doesn't match running_total"""
    print("=== FIXING BALANCE HISTORY SYNC ===")

    tm = TransactionManager()
    try:
        accounts = tm.get_all_accounts()

        for account in accounts:
            history = account.get_balance_history_copy()
            if not history:
                print(f"{account.name}: No balance history")
                continue

            current_total = account.running_total
            last_history_value = history[-1]

            print(f"\n{account.name}:")
            print(f"  Current running_total: ${current_total:.2f}")
            print(f"  Last history entry: ${last_history_value:.2f}")
            print(f"  Difference: ${current_total - last_history_value:.2f}")

            # If there's a significant difference, update the balance history
            if abs(current_total - last_history_value) > 0.01:
                print(f"  FIXING: Updating balance history final value to match running_total")

                # Update the last entry in balance history to match current running_total
                updated_history = list(history)
                updated_history[-1] = current_total

                # Update the account's balance history
                account.balance_history = updated_history

                # Verify the fix
                new_history = account.get_balance_history_copy()
                print(f"  AFTER FIX: Last history entry: ${new_history[-1]:.2f}")

        # Commit all changes
        tm.db.commit()
        print(f"\n=== SYNC FIX COMPLETED ===")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        tm.db.rollback()
    finally:
        tm.close()

if __name__ == "__main__":
    fix_balance_history_sync()
