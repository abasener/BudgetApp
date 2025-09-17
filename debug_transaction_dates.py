"""
Debug transaction dates vs week ranges to understand the mismatch
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def debug_transaction_dates():
    """Debug transaction dates vs week ranges"""
    print("=== DEBUGGING TRANSACTION DATES ===")

    tm = TransactionManager()
    try:
        accounts = tm.get_all_accounts()
        weeks = tm.get_all_weeks()

        # Show week ranges
        print("Week date ranges:")
        sorted_weeks = sorted(weeks, key=lambda w: w.week_number)
        for week in sorted_weeks[:10]:  # Show first 10 weeks
            print(f"  Week {week.week_number}: {week.start_date} to {week.end_date}")

        print("\nSafety Saving transactions:")
        safety_saving = next((acc for acc in accounts if acc.name == "Safety Saving"), None)

        if safety_saving:
            transactions = tm.get_transactions_by_account(safety_saving.id)
            transactions.sort(key=lambda t: t.date)

            print(f"Found {len(transactions)} transactions")
            for i, trans in enumerate(transactions):
                print(f"  {i+1}: {trans.date} - ${trans.amount:.2f} - {trans.description}")

            # Check which pay periods these would fall into
            print("\nTransaction to pay period mapping:")
            for i, trans in enumerate(transactions[:10]):  # First 10 transactions
                # Find which week this transaction falls into
                matching_week = None
                for week in weeks:
                    if week.start_date <= trans.date <= week.end_date:
                        matching_week = week
                        break

                if matching_week:
                    pay_period = (matching_week.week_number - 1) // 2 + 1
                    print(f"  Transaction {i+1} ({trans.date}): Week {matching_week.week_number} -> Pay Period {pay_period}")
                else:
                    print(f"  Transaction {i+1} ({trans.date}): No matching week found")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    debug_transaction_dates()