"""
Complete rollover test - create Week 3 to trigger final rollover to savings
"""

from services.paycheck_processor import PaycheckProcessor
from services.transaction_manager import TransactionManager
from datetime import date, timedelta

def complete_rollover_test():
    """Create Week 3 to trigger Week 2 rollover to savings"""

    print("=== COMPLETING ROLLOVER TEST ===")

    pp = PaycheckProcessor()
    tm = TransactionManager()

    try:
        # Check current state
        print("\n1. CURRENT STATE:")
        default_savings = tm.get_default_savings_account()
        if default_savings:
            print(f"   Safety Saving balance: ${default_savings.running_total:.2f}")
            print(f"   Safety Saving history: {default_savings.get_balance_history_copy()}")

        # Show current weeks
        all_weeks = tm.get_all_weeks()
        print(f"\n   Current weeks: {len(all_weeks)}")
        for week in all_weeks:
            print(f"     Week {week.week_number}: ${week.running_total:.2f} ({week.start_date})")

        # Create Week 3 to trigger Week 2 rollover
        print("\n2. CREATING WEEK 3 TO TRIGGER ROLLOVER:")
        week3_start = date.today() + timedelta(days=14)  # 2 weeks from today
        week3 = pp.create_new_week(week3_start)
        print(f"   Created Week 3 starting {week3_start}")

        # Process rollovers
        print("\n3. PROCESSING ROLLOVERS:")
        pp.check_and_process_rollovers()

        # Check final state
        print("\n4. FINAL STATE:")
        final_savings = tm.get_default_savings_account()
        if final_savings:
            print(f"   Safety Saving balance: ${final_savings.running_total:.2f}")
            print(f"   Safety Saving history: {final_savings.get_balance_history_copy()}")

        # Show all transactions
        print("\n5. ALL TRANSACTIONS:")
        all_transactions = tm.get_all_transactions()
        for tx in all_transactions:
            account_info = ""
            if hasattr(tx, 'account_id') and tx.account_id:
                account = tm.get_account_by_id(tx.account_id)
                if account:
                    account_info = f" -> {account.name}"
            print(f"   Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}{account_info}")

        # Calculate expected result
        print("\n6. EXPECTED VS ACTUAL:")
        # Week 1: -$458.50 - $100 = -$558.50 (rolled to Week 2)
        # Week 2: -$458.50 + (-$558.50) = -$1017.00 (should roll to savings)
        # Expected final balance: $4204.01 + (-$1017.00) = $3187.01

        expected_week2_total = -458.50 + (-558.50)  # -$1017.00
        expected_final_balance = 4204.01 + expected_week2_total  # $3187.01

        print(f"   Expected Week 2 total: ${expected_week2_total:.2f}")
        print(f"   Expected final balance: ${expected_final_balance:.2f}")
        print(f"   Actual final balance: ${final_savings.running_total:.2f}")

        if abs(final_savings.running_total - expected_final_balance) < 1.0:
            print(f"   SUCCESS: Balance matches expected!")
        else:
            print(f"   FAIL: Expected ${expected_final_balance:.2f}, got ${final_savings.running_total:.2f}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pp.close()
        tm.close()

if __name__ == "__main__":
    complete_rollover_test()