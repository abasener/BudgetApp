"""
Test the UI savings display logic to see if there are any issues
"""

from services.transaction_manager import TransactionManager

def test_savings_display_logic():
    """Test the savings display calculations"""

    tm = TransactionManager()

    try:
        # Get all accounts
        accounts = tm.get_all_accounts()

        # Test with the most recent pay period (Week 53-54 = pay period 27)
        current_pay_period_index = 27  # Week 53-54

        print(f"=== TESTING PAY PERIOD {current_pay_period_index} (Weeks 53-54) ===")

        for account in accounts:
            print(f"\nAccount: {account.name}")
            print(f"Current balance: ${account.running_total:.2f}")

            # Get balance history
            history = account.get_balance_history_copy()
            print(f"History length: {len(history) if history else 0}")

            if history and len(history) > 5:
                print(f"Last 5 history entries: {history[-5:]}")
            elif history:
                print(f"Full history: {history}")

            if not history:
                print("  No history available")
                continue

            # Calculate starting and final balances (same logic as UI)
            starting_index = current_pay_period_index - 1  # Convert to 0-based (index 26)
            final_index = current_pay_period_index  # index 27

            print(f"  Starting index: {starting_index}, Final index: {final_index}")

            # Get starting balance
            if starting_index < len(history):
                starting_balance = history[starting_index]
                print(f"  Starting balance (history[{starting_index}]): ${starting_balance:.2f}")
            else:
                starting_balance = history[-1] if history else account.running_total
                print(f"  Starting balance (fallback): ${starting_balance:.2f}")

            # Get final balance
            if final_index < len(history):
                final_balance = history[final_index]
                print(f"  Final balance (history[{final_index}]): ${final_balance:.2f}")
            else:
                final_balance = account.running_total
                print(f"  Final balance (current): ${final_balance:.2f}")

            # Calculate change
            amount_change = final_balance - starting_balance
            print(f"  Amount paid to account: ${amount_change:.2f}")

    finally:
        tm.close()

if __name__ == "__main__":
    test_savings_display_logic()