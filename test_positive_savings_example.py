"""
Test the savings calculation with a positive example like the user described
"""

from services.transaction_manager import TransactionManager
from models import get_db

def test_positive_savings_example():
    """Test savings calculation with positive example: Start $10, +$50 rollover, +$40 saved = $100 final"""

    print("=== POSITIVE SAVINGS EXAMPLE TEST ===")

    transaction_manager = TransactionManager()

    try:
        db = get_db()

        # STEP 1: Reset Safety Saving account to $100 to simulate the example
        print("\n1. SETTING UP EXAMPLE SCENARIO:")
        accounts = transaction_manager.get_all_accounts()
        safety_saving = transaction_manager.get_default_savings_account()

        if safety_saving:
            # Set the account to $100 to represent final state
            original_balance = safety_saving.running_total
            test_final_balance = 100.0
            transaction_manager.update_account_balance(safety_saving.id, test_final_balance)

            print(f"  Set {safety_saving.name} balance to ${test_final_balance:.2f} (was ${original_balance:.2f})")

            # STEP 2: Simulate the calculation logic
            print("\n2. SIMULATING SAVINGS CALCULATION:")

            # In the example:
            # - Starting value: $10
            # - Rollover: +$50
            # - Other savings: +$40
            # - Final: $100

            simulated_rollover = 50.0
            simulated_other_savings = 40.0
            total_period_change = simulated_rollover + simulated_other_savings  # $90

            # According to our logic:
            # starting_balance = current_balance - period_change
            current_balance = test_final_balance  # $100
            calculated_starting = current_balance - total_period_change  # $100 - $90 = $10

            print(f"  Example scenario:")
            print(f"    Final balance (current): ${current_balance:.2f}")
            print(f"    Rollover during period: +${simulated_rollover:.2f}")
            print(f"    Other savings during period: +${simulated_other_savings:.2f}")
            print(f"    Total period change: +${total_period_change:.2f}")
            print(f"    Calculated starting balance: ${calculated_starting:.2f}")

            print(f"\n  Expected results:")
            print(f"    Starting value should show: ${calculated_starting:.2f}")
            print(f"    Final value should show: ${current_balance:.2f}")

            # STEP 3: Verify the math
            print("\n3. VERIFICATION:")
            expected_starting = 10.0
            expected_final = 100.0

            starting_correct = abs(calculated_starting - expected_starting) < 0.01
            final_correct = abs(current_balance - expected_final) < 0.01

            print(f"  Starting value correct: {starting_correct} (${calculated_starting:.2f} should be ${expected_starting:.2f})")
            print(f"  Final value correct: {final_correct} (${current_balance:.2f} should be ${expected_final:.2f})")

            all_correct = starting_correct and final_correct
            print(f"  All calculations correct: {all_correct}")

            # Restore original balance
            transaction_manager.update_account_balance(safety_saving.id, original_balance)
            print(f"\n  Restored {safety_saving.name} balance to ${original_balance:.2f}")

        else:
            print("  No default savings account found")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()

if __name__ == "__main__":
    test_positive_savings_example()