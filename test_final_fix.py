"""
Test the final fix for multiple rollover processing during paycheck
"""

from services.paycheck_processor import PaycheckProcessor
from services.transaction_manager import TransactionManager
from datetime import date

def test_final_fix():
    """Test that paycheck processing doesn't trigger multiple rollovers"""

    print("=== TESTING FINAL FIX ===")

    pp = PaycheckProcessor()
    tm = TransactionManager()

    try:
        # Check initial state
        print("\n1. INITIAL STATE:")
        default_savings = tm.get_default_savings_account()
        if default_savings:
            print(f"   Safety Saving balance: ${default_savings.running_total:.2f}")
            print(f"   Safety Saving history: {default_savings.get_balance_history_copy()}")

        # Process paycheck
        print("\n2. PROCESSING PAYCHECK ($1500):")
        paycheck_amount = 1500.0
        paycheck_date = date.today()
        week_start_date = date.today()

        split = pp.process_new_paycheck(paycheck_amount, paycheck_date, week_start_date)

        # Check state after paycheck
        print("\n3. AFTER PAYCHECK:")
        after_savings = tm.get_default_savings_account()
        if after_savings:
            print(f"   Safety Saving balance: ${after_savings.running_total:.2f}")
            print(f"   Safety Saving history: {after_savings.get_balance_history_copy()}")

        print(f"   Week 1 allocation: ${split.week1_allocation:.2f}")
        print(f"   Week 2 allocation: ${split.week2_allocation:.2f}")

        # Add a single spending transaction
        print("\n4. ADDING ONE SPENDING TRANSACTION ($100):")

        before_spending = tm.get_default_savings_account()
        before_balance = before_spending.running_total
        before_history = before_spending.get_balance_history_copy()

        spending_tx = {
            "transaction_type": "spending",
            "week_number": 1,
            "amount": 100.0,
            "date": paycheck_date,
            "description": "Test spending",
            "category": "Food"
        }
        tm.add_transaction(spending_tx)

        after_spending = tm.get_default_savings_account()
        after_balance = after_spending.running_total
        after_history = after_spending.get_balance_history_copy()

        print(f"   Before spending: balance=${before_balance:.2f}, history={before_history}")
        print(f"   After spending:  balance=${after_balance:.2f}, history={after_history}")

        # Calculate expected vs actual
        print("\n5. EXPECTED VS ACTUAL:")

        # Expected: Week 2 allocation should roll to savings (-$458.50)
        # Plus Week 1 rollover: (-$458.50 - $100 = -$558.50)
        # Total rollover to savings should be: -$558.50 + (-$458.50) = -$1017.00
        expected_week1_rollover = split.week1_allocation - 100  # -$558.50
        expected_week2_total = split.week2_allocation + expected_week1_rollover  # -$1017.00
        expected_final_balance = 4204.01 + expected_week2_total  # Should be $3187.01

        print(f"   Expected Week 1 rollover: ${expected_week1_rollover:.2f}")
        print(f"   Expected Week 2 total: ${expected_week2_total:.2f}")
        print(f"   Expected final balance: ${expected_final_balance:.2f}")
        print(f"   Actual final balance: ${after_balance:.2f}")

        if len(after_history) >= 2:
            history_change = after_history[-1] - after_history[0]
            print(f"   Expected history change: ${expected_week2_total:.2f}")
            print(f"   Actual history change: ${history_change:.2f}")

            if abs(history_change - expected_week2_total) < 1.0:
                print(f"   PASS: History change matches expected!")
            else:
                print(f"   FAIL: Expected ${expected_week2_total:.2f}, got ${history_change:.2f}")
                print(f"   Difference: ${history_change - expected_week2_total:.2f}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pp.close()
        tm.close()

if __name__ == "__main__":
    test_final_fix()