"""
Fix balance history to show proper cumulative balances for each pay period
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def fix_cumulative_balance_history():
    """Fix balance history to show proper cumulative balances"""
    print("=== FIXING CUMULATIVE BALANCE HISTORY ===")

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

            # Get all transactions for this account sorted by date
            all_transactions = tm.get_transactions_by_account(account.id)
            all_transactions.sort(key=lambda t: t.date)

            print(f"Found {len(all_transactions)} transactions")

            # Create balance history array - starts at 0, then tracks cumulative changes
            balance_history = [0.0]  # Starting balance
            running_balance = 0.0

            # For each pay period, calculate the balance at the end
            for pay_period in range(1, num_pay_periods + 1):
                # Get transactions for this pay period
                week1_num = (pay_period - 1) * 2 + 1
                week2_num = week1_num + 1

                # Find the date range for this pay period
                period_start = None
                period_end = None

                for week in weeks:
                    if week.week_number == week1_num:
                        period_start = week.start_date
                    elif week.week_number == week2_num:
                        period_end = week.end_date

                if period_start and period_end:
                    # Get transactions in this period
                    period_transactions = [
                        t for t in all_transactions
                        if period_start <= t.date <= period_end
                    ]

                    # Add up the transaction amounts for this period
                    period_change = sum(t.amount for t in period_transactions)
                    running_balance += period_change

                    print(f"  Pay Period {pay_period}: ${period_change:.2f} -> Balance: ${running_balance:.2f}")
                else:
                    print(f"  Pay Period {pay_period}: No date range found")

                balance_history.append(running_balance)

            print(f"Final balance history length: {len(balance_history)}")
            print(f"History: {balance_history[:5]}...{balance_history[-5:]}")
            print(f"Expected final balance: ${current_balance:.2f}, Calculated: ${balance_history[-1]:.2f}")

            # Update the account
            account.balance_history = balance_history

        tm.db.commit()
        print(f"\nCumulative balance history fix completed!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    fix_cumulative_balance_history()