"""
Test the cumulative addition theory with CLEAN database
"""

from services.paycheck_processor import PaycheckProcessor
from services.transaction_manager import TransactionManager
from datetime import date, timedelta

def test_clean_cumulative_theory():
    """Test cumulative addition with clean database"""

    print("=== TESTING CUMULATIVE THEORY WITH CLEAN DATA ===")

    pp = PaycheckProcessor()
    tm = TransactionManager()

    try:
        # Verify clean state
        print("\n1. VERIFIED CLEAN STATE:")
        default_savings = tm.get_default_savings_account()
        if default_savings:
            print(f"   Safety Saving balance: ${default_savings.running_total:.2f}")
            print(f"   Safety Saving history: {default_savings.get_balance_history_copy()}")

        # Add paycheck and track balance changes step by step
        print("\n2. PROCESSING PAYCHECK WITH DETAILED TRACKING:")

        paycheck_amount = 1500.0
        paycheck_date = date.today()
        week_start_date = date.today()

        split = pp.process_new_paycheck(paycheck_amount, paycheck_date, week_start_date)

        # Check state after paycheck
        after_paycheck_savings = tm.get_default_savings_account()
        if after_paycheck_savings:
            history_after_paycheck = after_paycheck_savings.get_balance_history_copy()
            print(f"   After paycheck - balance: ${after_paycheck_savings.running_total:.2f}")
            print(f"   After paycheck - history: {history_after_paycheck}")

        print(f"   Week allocations: Week 1=${split.week1_allocation:.2f}, Week 2=${split.week2_allocation:.2f}")

        # Add spending to Week 1
        print("\n3. ADDING SPENDING AND TRACKING BALANCE HISTORY:")

        spending_amounts = [100.0, 50.0]  # Total: $150
        cumulative_spending = 0

        for i, amount in enumerate(spending_amounts):
            cumulative_spending += amount
            print(f"\n   Adding spending #{i+1}: ${amount:.2f} (cumulative: ${cumulative_spending:.2f})")

            # Check balance BEFORE adding transaction
            before_savings = tm.get_default_savings_account()
            before_balance = before_savings.running_total
            before_history = before_savings.get_balance_history_copy()

            # Add spending transaction
            spending_tx = {
                "transaction_type": "spending",
                "week_number": 1,
                "amount": amount,
                "date": paycheck_date,
                "description": f"Test spending #{i+1}",
                "category": "Food"
            }
            tm.add_transaction(spending_tx)

            # Check balance AFTER adding transaction
            after_savings = tm.get_default_savings_account()
            after_balance = after_savings.running_total
            after_history = after_savings.get_balance_history_copy()

            print(f"     Before: balance=${before_balance:.2f}, history={before_history}")
            print(f"     After:  balance=${after_balance:.2f}, history={after_history}")

            # Check if history changed
            if len(after_history) > len(before_history):
                new_entry = after_history[-1]
                print(f"     NEW HISTORY ENTRY ADDED: ${new_entry:.2f}")
            elif len(after_history) == len(before_history) and after_history[-1] != before_history[-1]:
                old_last = before_history[-1]
                new_last = after_history[-1]
                change = new_last - old_last
                print(f"     HISTORY ENTRY CHANGED: ${old_last:.2f} -> ${new_last:.2f} (change: ${change:.2f})")

        # Force completion of rollover process
        print("\n4. FORCING ROLLOVER COMPLETION:")

        # Create Week 3 to trigger Week 2 rollover
        week3_start = week_start_date + timedelta(days=14)
        week3 = pp.create_new_week(week3_start)

        # Track balance before rollover
        before_rollover_savings = tm.get_default_savings_account()
        before_rollover_balance = before_rollover_savings.running_total
        before_rollover_history = before_rollover_savings.get_balance_history_copy()

        print(f"   Before final rollover: balance=${before_rollover_balance:.2f}")
        print(f"   Before final rollover: history={before_rollover_history}")

        # Process rollovers
        pp.check_and_process_rollovers()

        # Track balance after rollover
        after_rollover_savings = tm.get_default_savings_account()
        after_rollover_balance = after_rollover_savings.running_total
        after_rollover_history = after_rollover_savings.get_balance_history_copy()

        print(f"   After final rollover: balance=${after_rollover_balance:.2f}")
        print(f"   After final rollover: history={after_rollover_history}")

        # Calculate expected vs actual
        print("\n5. EXPECTED VS ACTUAL ANALYSIS:")

        expected_week1_rollover = split.week1_allocation - cumulative_spending  # -458.50 - 150 = -608.50
        expected_week2_total = split.week2_allocation + expected_week1_rollover  # -458.50 + (-608.50) = -1067
        expected_final_balance = 4204.01 + expected_week2_total  # Starting + rollover

        print(f"   Expected Week 1 rollover: ${expected_week1_rollover:.2f}")
        print(f"   Expected Week 2 total: ${expected_week2_total:.2f}")
        print(f"   Expected final balance: ${expected_final_balance:.2f}")
        print(f"   Actual final balance: ${after_rollover_balance:.2f}")

        if len(after_rollover_history) >= 2:
            actual_history_change = after_rollover_history[-1] - after_rollover_history[0]
            print(f"   Expected history change: ${expected_week2_total:.2f}")
            print(f"   Actual history change: ${actual_history_change:.2f}")

            if abs(actual_history_change - expected_week2_total) < 1.0:
                print(f"   PASS History change matches expected!")
            else:
                print(f"   FAIL MISMATCH! Difference: ${actual_history_change - expected_week2_total:.2f}")

                # Check if it's cumulative addition
                if actual_history_change > abs(expected_week2_total) * 2:
                    print(f"   CUMULATIVE ADDITION CONFIRMED: History change much larger than expected")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pp.close()
        tm.close()

if __name__ == "__main__":
    test_clean_cumulative_theory()