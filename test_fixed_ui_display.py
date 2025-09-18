"""
Test the fixed UI display logic for savings values
"""

from services.transaction_manager import TransactionManager

def test_fixed_ui_display():
    """Test the fixed UI calculations for savings display"""

    tm = TransactionManager()

    try:
        # Get all accounts
        accounts = tm.get_all_accounts()

        # Simulate the current pay period calculation for Week 53-54
        # Using the same logic as the UI
        week1_num = 53  # Simulating week1_detail.week_data.week_number
        current_pay_period_index = (week1_num - 1) // 2 + 1  # Convert to 1-based pay period

        print(f"=== TESTING UI LOGIC FOR PAY PERIOD {current_pay_period_index} (Weeks 53-54) ===")

        for account in accounts[:1]:  # Test with just the first account
            print(f"\nAccount: {account.name}")

            # Get balance history
            history = account.get_balance_history_copy()
            print(f"History length: {len(history) if history else 0}")

            if not history:
                print("  No history available")
                continue

            # Calculate starting and final balances (using fixed UI logic)
            starting_index = current_pay_period_index - 1  # Convert to 0-based (index 26)
            final_index = current_pay_period_index  # index 27

            print(f"  Pay period {current_pay_period_index}: starting_index={starting_index}, final_index={final_index}")

            # Get starting balance (beginning of this pay period)
            if starting_index < len(history):
                starting_balance = history[starting_index]
                print(f"  Starting balance (history[{starting_index}]): ${starting_balance:.2f}")
            else:
                starting_balance = history[-1] if history else account.running_total
                print(f"  Starting balance (fallback): ${starting_balance:.2f}")

            # Get final balance (end of this pay period)
            if final_index < len(history):
                final_balance = history[final_index]
                print(f"  Final balance (history[{final_index}]): ${final_balance:.2f}")
            else:
                # This pay period hasn't finished yet, use current balance
                final_balance = account.running_total
                print(f"  Final balance (current): ${final_balance:.2f}")

            # Calculate amount change (what UI shows as "Amount paid to Savings")
            amount_change = final_balance - starting_balance
            print(f"  Amount paid to account: ${amount_change:.2f}")

            # Expected results for Week 53-54:
            # - Week 54 rollover hasn't been processed yet (pay period incomplete)
            # - So final balance should equal current balance
            # - Amount change should be 0 (since period isn't complete)
            print(f"\n  Expected for incomplete pay period 27:")
            print(f"    Starting: history[26] = ${history[26]:.2f}")
            print(f"    Final: current balance = ${account.running_total:.2f}")
            print(f"    Amount paid: ${account.running_total - history[26]:.2f}")

    finally:
        tm.close()

if __name__ == "__main__":
    test_fixed_ui_display()