"""
Verify the final state is correct
"""

from services.transaction_manager import TransactionManager

def verify_final_state():
    """Verify the final state is correct"""

    print("=== VERIFYING FINAL STATE ===")

    tm = TransactionManager()

    try:
        # Get default savings account directly
        default_savings = tm.get_default_savings_account()
        if default_savings:
            print(f"Safety Saving balance: ${default_savings.running_total:.2f}")
            print(f"Safety Saving history: {default_savings.get_balance_history_copy()}")

        # Check if balance matches expected
        expected_balance = 4204.01 - 1017.00  # $3187.01
        actual_balance = default_savings.running_total

        print(f"\nExpected balance: ${expected_balance:.2f}")
        print(f"Actual balance: ${actual_balance:.2f}")

        if abs(actual_balance - expected_balance) < 0.01:
            print("SUCCESS: Balance is correct!")
        else:
            print("FAIL: Balance mismatch!")

        # Check all rollover transactions
        all_transactions = tm.get_all_transactions()
        rollover_txs = [tx for tx in all_transactions if 'rollover' in tx.description.lower() or 'deficit' in tx.description.lower() or 'surplus' in tx.description.lower()]

        print(f"\nRollover transactions: {len(rollover_txs)}")
        total_rollover_impact = 0
        for tx in rollover_txs:
            impact = ""
            if hasattr(tx, 'account_id') and tx.account_id:
                account = tm.get_account_by_id(tx.account_id)
                if account:
                    impact = f" -> {account.name}"
                    total_rollover_impact += tx.amount

            print(f"  Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}{impact}")

        print(f"\nTotal impact on accounts: ${total_rollover_impact:.2f}")
        expected_impact = -1017.00
        if abs(total_rollover_impact - expected_impact) < 0.01:
            print("SUCCESS: Rollover impact is correct!")
        else:
            print("FAIL: Rollover impact mismatch!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tm.close()

if __name__ == "__main__":
    verify_final_state()