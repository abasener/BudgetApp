"""
Rebuild balance history by matching transaction descriptions to week numbers
instead of relying on dates which are mismatched
"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def rebuild_balance_history():
    """Rebuild balance history from transactions using week numbers"""
    print("=== REBUILDING BALANCE HISTORY ===")

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

            # For each pay period, find transactions by week number in description
            for pay_period in range(1, num_pay_periods + 1):
                week1_num = (pay_period - 1) * 2 + 1
                week2_num = week1_num + 1

                # Find transactions for weeks in this pay period
                period_transactions = []
                for t in all_transactions:
                    if t.description:
                        # Look for "Week X" in description
                        week_match = re.search(r'Week (\d+)', t.description)
                        if week_match:
                            week_num = int(week_match.group(1))
                            if week_num == week1_num or week_num == week2_num:
                                period_transactions.append(t)

                # Add up the transaction amounts for this period
                period_change = sum(t.amount for t in period_transactions)
                running_balance += period_change

                print(f"  Pay Period {pay_period} (weeks {week1_num}-{week2_num}): ${period_change:.2f} -> Balance: ${running_balance:.2f}")
                balance_history.append(running_balance)

            print(f"Final balance history length: {len(balance_history)}")
            print(f"History: {balance_history[:5]}...{balance_history[-5:]}")
            print(f"Expected final balance: ${current_balance:.2f}, Calculated: ${balance_history[-1]:.2f}")

            # Update the account's balance history
            account.balance_history = balance_history
            print(f"Updated {account.name} balance history")

        # Commit changes
        tm.db.commit()
        print("\nBalance history rebuild completed!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        tm.db.rollback()
    finally:
        tm.close()

if __name__ == "__main__":
    rebuild_balance_history()
