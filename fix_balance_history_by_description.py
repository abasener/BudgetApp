"""
Fix balance history by mapping transactions to pay periods based on their description
"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def fix_balance_history_by_description():
    """Fix balance history by mapping transactions to pay periods based on description"""
    print("=== FIXING BALANCE HISTORY BY DESCRIPTION ===")

    tm = TransactionManager()
    try:
        accounts = tm.get_all_accounts()
        weeks = tm.get_all_weeks()

        if not weeks:
            print("No weeks found")
            return

        max_week = max(w.week_number for w in weeks)
        num_pay_periods = (max_week - 1) // 2 + 1
        print(f"Maximum week: {max_week}, Pay periods: {num_pay_periods}")

        for account in accounts:
            print(f"\n--- {account.name} ---")
            current_balance = account.running_total
            print(f"Current balance: ${current_balance:.2f}")

            # Get all transactions for this account
            all_transactions = tm.get_transactions_by_account(account.id)
            print(f"Found {len(all_transactions)} transactions")

            # Create balance history array - starts at 0
            balance_history = [0.0]  # Starting balance
            running_balance = 0.0

            # Create a mapping of pay periods to transaction amounts
            pay_period_amounts = {}

            # Parse transaction descriptions to determine which pay period they belong to
            for trans in all_transactions:
                # Look for patterns like "End-of-period deficit from Week 8"
                if "Week" in trans.description:
                    # Extract week number from description
                    week_match = re.search(r"Week (\d+)", trans.description)
                    if week_match:
                        week_num = int(week_match.group(1))
                        pay_period = (week_num - 1) // 2 + 1

                        if pay_period not in pay_period_amounts:
                            pay_period_amounts[pay_period] = 0.0
                        pay_period_amounts[pay_period] += trans.amount

                        print(f"  Week {week_num} (Pay Period {pay_period}): ${trans.amount:.2f}")

            # Build the balance history
            for pay_period in range(1, num_pay_periods + 1):
                if pay_period in pay_period_amounts:
                    period_change = pay_period_amounts[pay_period]
                    running_balance += period_change
                    print(f"  Pay Period {pay_period}: ${period_change:.2f} -> Balance: ${running_balance:.2f}")
                else:
                    print(f"  Pay Period {pay_period}: $0.00 -> Balance: ${running_balance:.2f}")

                balance_history.append(running_balance)

            print(f"Final balance history length: {len(balance_history)}")
            print(f"Expected final balance: ${current_balance:.2f}, Calculated: ${balance_history[-1]:.2f}")

            # Update the account
            account.balance_history = balance_history

        tm.db.commit()
        print(f"\nBalance history fix by description completed!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    fix_balance_history_by_description()