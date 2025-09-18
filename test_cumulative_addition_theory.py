"""
Test the theory that balance history is being cumulatively added instead of replaced
"""

from services.paycheck_processor import PaycheckProcessor
from services.transaction_manager import TransactionManager
from datetime import date, timedelta

def test_cumulative_addition_theory():
    """Test if balance history is accumulating instead of replacing values"""

    print("=== TESTING CUMULATIVE ADDITION THEORY ===")

    pp = PaycheckProcessor()
    tm = TransactionManager()

    try:
        # Step 1: Check initial state
        print("\n1. INITIAL STATE:")
        default_savings = tm.get_default_savings_account()
        if default_savings:
            print(f"   Safety Saving balance: ${default_savings.running_total:.2f}")
            print(f"   Safety Saving history: {default_savings.get_balance_history_copy()}")

        # Step 2: Add first paycheck and track what happens
        print("\n2. ADDING FIRST PAYCHECK ($1500):")

        # Monitor account balance changes during paycheck processing
        def monitor_account_balance(stage_name):
            current_savings = tm.get_default_savings_account()
            if current_savings:
                print(f"   {stage_name}: balance=${current_savings.running_total:.2f}")

        paycheck_amount = 1500.0
        paycheck_date = date.today()
        week_start_date = date.today()

        monitor_account_balance("Before paycheck")
        split = pp.process_new_paycheck(paycheck_amount, paycheck_date, week_start_date)
        monitor_account_balance("After paycheck")

        # Check what happened to balance history
        updated_savings = tm.get_default_savings_account()
        if updated_savings:
            history = updated_savings.get_balance_history_copy()
            print(f"   History after paycheck: {history}")
            if len(history) >= 2:
                change = history[-1] - history[-2]
                print(f"   History change: ${change:.2f}")

        # Step 3: Add some spending and see what happens to balances
        print("\n3. ADDING SPENDING TRANSACTIONS:")

        # Add some spending transactions to Week 1
        spending_amounts = [50.0, 100.0, 75.0]  # Total: $225
        week_1 = tm.get_week_by_number(1)

        for i, amount in enumerate(spending_amounts):
            print(f"\n   Adding spending #{i+1}: ${amount:.2f}")

            # Monitor balance before adding transaction
            monitor_account_balance(f"Before spending ${amount:.2f}")

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

            # Monitor balance after adding transaction
            monitor_account_balance(f"After spending ${amount:.2f}")

            # Check if history changed
            current_savings = tm.get_default_savings_account()
            if current_savings:
                current_history = current_savings.get_balance_history_copy()
                print(f"   History after spending: {current_history}")

        # Step 4: Force rollover processing and track balance changes
        print("\n4. FORCING ROLLOVER PROCESSING:")

        # Create Week 3 to trigger Week 2 rollover
        week3_start = week_start_date + timedelta(days=14)
        week3 = pp.create_new_week(week3_start)
        print(f"   Created Week 3 to trigger rollovers")

        monitor_account_balance("Before rollover processing")

        # Process rollovers
        pp.check_and_process_rollovers()

        monitor_account_balance("After rollover processing")

        # Check final history
        final_savings = tm.get_default_savings_account()
        if final_savings:
            final_history = final_savings.get_balance_history_copy()
            print(f"   Final history: {final_history}")

            if len(final_history) >= 2:
                final_change = final_history[-1] - final_history[-2]
                print(f"   Final history change: ${final_change:.2f}")

                # Calculate expected change
                expected_rollover = split.week2_allocation  # Should be around -$458.50
                total_spending = sum(spending_amounts)  # $225
                expected_week1_rollover = split.week1_allocation - total_spending  # -$458.50 - $225 = -$683.50
                expected_week2_total = split.week2_allocation + expected_week1_rollover  # -$458.50 + (-$683.50) = -$1142

                print(f"\n5. ANALYSIS:")
                print(f"   Expected Week 1 rollover: ${expected_week1_rollover:.2f}")
                print(f"   Expected Week 2 total: ${expected_week2_total:.2f}")
                print(f"   Expected final rollover to savings: ${expected_week2_total:.2f}")
                print(f"   Actual history change: ${final_change:.2f}")

                if abs(final_change - expected_week2_total) < 1.0:
                    print(f"   ✅ History change matches expected rollover!")
                else:
                    print(f"   ❌ MISMATCH! Expected ${expected_week2_total:.2f}, got ${final_change:.2f}")

                    # If much larger, it might be cumulative
                    if final_change > expected_week2_total * 5:
                        print(f"   🔍 THEORY CONFIRMED: History change is much larger than expected")
                        print(f"   This suggests cumulative addition instead of replacement")

        # Step 6: Check individual rollover transactions
        print("\n6. INDIVIDUAL ROLLOVER TRANSACTIONS:")
        all_weeks = tm.get_all_weeks()
        for week in all_weeks:
            transactions = tm.get_transactions_by_week(week.week_number)
            rollover_txs = [tx for tx in transactions if 'rollover' in tx.description.lower() or 'surplus' in tx.description.lower() or 'deficit' in tx.description.lower()]
            if rollover_txs:
                print(f"   Week {week.week_number} rollover transactions:")
                for tx in rollover_txs:
                    print(f"     {tx.transaction_type}: ${tx.amount:.2f} - {tx.description}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pp.close()
        tm.close()

if __name__ == "__main__":
    test_cumulative_addition_theory()