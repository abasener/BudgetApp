"""
Test the complete rollover flow with fresh data to see if the $92.72 issue is resolved
"""

from services.paycheck_processor import PaycheckProcessor
from services.transaction_manager import TransactionManager
from datetime import date, timedelta

def test_fresh_rollover_flow():
    """Test rollover flow with clean data"""

    pp = PaycheckProcessor()
    tm = TransactionManager()

    try:
        print("=== TESTING FRESH ROLLOVER FLOW ===")

        # Add a simple paycheck for testing - using a smaller amount for easier tracking
        paycheck_amount = 1500.0
        paycheck_date = date.today()
        week_start_date = date.today()

        print(f"\n1. Adding paycheck: ${paycheck_amount:.2f}")
        split = pp.process_new_paycheck(paycheck_amount, paycheck_date, week_start_date)

        print(f"   Paycheck split results:")
        print(f"   - Bills deducted: ${split.bills_deducted:.2f}")
        print(f"   - Account auto-savings: ${split.account_auto_savings:.2f}")
        print(f"   - Remaining for weeks: ${split.remaining_for_weeks:.2f}")
        print(f"   - Week 1 allocation: ${split.week1_allocation:.2f}")
        print(f"   - Week 2 allocation: ${split.week2_allocation:.2f}")

        # Get the created weeks
        all_weeks = tm.get_all_weeks()
        print(f"\n2. Weeks created: {len(all_weeks)}")
        for week in all_weeks:
            print(f"   Week {week.week_number}: ${week.running_total:.2f} (rollover_applied: {week.rollover_applied})")

        # Check savings account state after paycheck
        default_savings = tm.get_default_savings_account()
        print(f"\n3. Savings account after paycheck:")
        print(f"   Balance: ${default_savings.running_total:.2f}")
        print(f"   History: {default_savings.get_balance_history_copy()}")

        # Now let's simulate some spending and trigger rollovers
        print(f"\n4. Adding some spending to Week 1...")

        # Add some spending to week 1
        week1 = tm.get_week_by_number(1)
        if week1:
            spending_tx = {
                "transaction_type": "spending",
                "week_number": 1,
                "amount": 100.0,
                "date": paycheck_date,
                "description": "Test spending",
                "category": "Food"
            }
            tm.add_transaction(spending_tx)
            print(f"   Added $100 spending to Week 1")

        # Force Week 1 to be considered complete by marking Week 2 as having a next week
        # Create a dummy Week 3 to trigger Week 2 rollover
        print(f"\n5. Creating Week 3 to trigger rollovers...")
        week3_start = week_start_date + timedelta(days=14)
        week3 = pp.create_new_week(week3_start)
        print(f"   Created Week 3: {week3.week_number}")

        # Now process rollovers
        print(f"\n6. Processing rollovers...")
        pp.check_and_process_rollovers()

        # Check the results
        print(f"\n7. Results after rollover processing:")

        updated_weeks = tm.get_all_weeks()
        for week in updated_weeks:
            rollover_calc = pp.calculate_week_rollover(week.week_number)
            print(f"   Week {week.week_number}:")
            print(f"     Running total: ${week.running_total:.2f}")
            print(f"     Allocated amount: ${rollover_calc.allocated_amount:.2f}")
            print(f"     Spent amount: ${rollover_calc.spent_amount:.2f}")
            print(f"     Rollover amount: ${rollover_calc.rollover_amount:.2f}")
            print(f"     Rollover applied: {week.rollover_applied}")

        # Check savings account final state
        updated_savings = tm.get_default_savings_account()
        print(f"\n8. Final savings account state:")
        print(f"   Balance: ${updated_savings.running_total:.2f}")
        print(f"   History: {updated_savings.get_balance_history_copy()}")

        # Calculate expected vs actual for Pay Period 1
        if len(updated_savings.get_balance_history_copy()) >= 2:
            history = updated_savings.get_balance_history_copy()
            starting = history[0]  # Should be 0.0
            final = history[1]     # Should reflect rollover from Week 2
            amount_paid = final - starting
            print(f"\n9. Pay Period 1 Analysis:")
            print(f"   Starting balance: ${starting:.2f}")
            print(f"   Final balance: ${final:.2f}")
            print(f"   Amount paid to savings: ${amount_paid:.2f}")

            # Expected calculation based on your scenario:
            # Week 1: allocation - spending = rollover to Week 2
            # Week 2: allocation + Week 1 rollover - Week 2 spending = rollover to savings
            expected_week1_rollover = split.week1_allocation - 100.0  # $100 spending
            expected_week2_total = split.week2_allocation + expected_week1_rollover
            print(f"   Expected Week 1 rollover: ${expected_week1_rollover:.2f}")
            print(f"   Expected Week 2 total: ${expected_week2_total:.2f}")
            print(f"   Expected rollover to savings: ${expected_week2_total:.2f} (assuming no Week 2 spending)")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pp.close()
        tm.close()

if __name__ == "__main__":
    test_fresh_rollover_flow()