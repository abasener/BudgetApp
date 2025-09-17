"""
Test week savings start/final/change calculations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import get_db, Account
from services.transaction_manager import TransactionManager

def test_week_savings_values():
    """Test if week savings calculations are working correctly"""
    print("=== TESTING WEEK SAVINGS VALUES ===")

    tm = TransactionManager()
    try:
        # Get accounts and their balance history
        accounts = tm.get_all_accounts()
        weeks = tm.get_all_weeks()

        print(f"Found {len(accounts)} accounts and {len(weeks)} weeks")

        # Test a few specific pay periods
        for account in accounts:
            if account.name == "Safety Saving":  # Focus on the one with data
                print(f"\n--- Testing {account.name} ---")
                print(f"Current balance: ${account.running_total:.2f}")

                history = account.get_balance_history_copy()
                if not history:
                    print("No balance history found")
                    continue

                print(f"Balance history length: {len(history)}")
                print(f"History values: {history[:10]}...")  # First 10 values

                # Show last 10 values to see current state
                print(f"Last 10 history values: {[f'${v:.2f}' for v in history[-10:]]}")
                print(f"Final history value: ${history[-1]:.2f}")
                print(f"Account running_total: ${account.running_total:.2f}")
                print(f"Sync status: {'SYNCED' if abs(history[-1] - account.running_total) < 0.01 else 'OUT OF SYNC'}")

                # Test specific pay periods
                test_periods = [1, 2, 3, 24, 25, 26]  # Include the one that showed -4512
                for pay_period in test_periods:
                    if pay_period <= len(history) - 1:  # Make sure we have data
                        starting_index = pay_period - 1  # Convert to 0-based
                        final_index = pay_period

                        if starting_index < len(history) and final_index < len(history):
                            starting_value = history[starting_index]
                            final_value = history[final_index]
                            change = final_value - starting_value

                            print(f"  Pay Period {pay_period}:")
                            print(f"    Starting (index {starting_index}): ${starting_value:.2f}")
                            print(f"    Final (index {final_index}): ${final_value:.2f}")
                            print(f"    Change: ${change:.2f}")

        print(f"\n=== SIMULATING WEEKLY VIEW CALCULATION ===")

        # Simulate what the weekly view would calculate for a specific pay period
        # Let's test pay period 3 (which should use indices 2 and 3)
        test_pay_period = 3

        for account in accounts:
            if account.name == "Safety Saving":
                history = account.get_balance_history_copy()
                if history and len(history) > test_pay_period:
                    starting_index = test_pay_period - 1  # 2
                    final_index = test_pay_period  # 3

                    starting_balance = history[starting_index]
                    final_balance = history[final_index]
                    amount_change = final_balance - starting_balance

                    print(f"\nWeekly view simulation for Pay Period {test_pay_period}:")
                    print(f"  {account.name}:")
                    print(f"    Starting: ${starting_balance:.2f}")
                    print(f"    Final: ${final_balance:.2f}")
                    print(f"    Amount added: ${amount_change:.2f}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    test_week_savings_values()