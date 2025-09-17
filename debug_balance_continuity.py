"""
Debug balance history continuity between pay periods
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def debug_balance_continuity():
    """Debug balance history to check continuity between pay periods"""

    print("=== DEBUGGING BALANCE HISTORY CONTINUITY ===")

    transaction_manager = TransactionManager()

    try:
        # Get all accounts
        accounts = transaction_manager.get_all_accounts()
        all_weeks = transaction_manager.get_all_weeks()

        print(f"Found {len(accounts)} accounts and {len(all_weeks)} weeks")

        for account in accounts:
            print(f"\n--- {account.name} ---")

            # Get balance history
            history = account.get_balance_history_copy()
            print(f"Balance history: {history}")
            print(f"Current running_total: ${account.running_total:.2f}")

            if len(history) < 2:
                print("  Not enough history to check continuity")
                continue

            # Check continuity for each pay period
            max_periods = len(history) - 1
            print(f"Checking {max_periods} pay periods:")

            for period in range(1, max_periods + 1):
                # Calculate what the GUI would show for this period
                starting_index = period - 1  # Convert to 0-based
                final_index = period

                if starting_index < len(history) and final_index < len(history):
                    starting_balance = history[starting_index]
                    final_balance = history[final_index]
                    amount_added = final_balance - starting_balance

                    print(f"  Pay Period {period}:")
                    print(f"    Starting: ${starting_balance:.2f} (index {starting_index})")
                    print(f"    Final:    ${final_balance:.2f} (index {final_index})")
                    print(f"    Added:    ${amount_added:.2f}")

                    # Check continuity with next period
                    if period < max_periods:
                        next_starting_index = period  # Next period's starting index
                        if next_starting_index < len(history):
                            next_starting_balance = history[next_starting_index]

                            continuity_ok = abs(final_balance - next_starting_balance) < 0.01
                            print(f"    Continuity with Period {period + 1}: {'OK' if continuity_ok else 'ERROR'}")

                            if not continuity_ok:
                                print(f"      ERROR: Final ${final_balance:.2f} != Next Starting ${next_starting_balance:.2f}")
                                print(f"      Difference: ${abs(final_balance - next_starting_balance):.2f}")

            # Also check mapping to weeks
            print(f"\nWeek to Pay Period Mapping:")
            for week in sorted(all_weeks, key=lambda w: w.week_number):
                week_num = week.week_number
                pay_period = (week_num - 1) // 2 + 1
                position_in_period = "Week 1" if (week_num - 1) % 2 == 0 else "Week 2"
                print(f"  Week {week_num} -> Pay Period {pay_period} ({position_in_period})")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()

if __name__ == "__main__":
    debug_balance_continuity()