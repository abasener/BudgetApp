"""
Trace the balance history issue by monitoring account balances during paycheck processing
"""

from services.paycheck_processor import PaycheckProcessor
from services.transaction_manager import TransactionManager
from datetime import date

def trace_balance_history_issue():
    """Trace what happens to balance history during paycheck processing"""

    print("=== TRACING BALANCE HISTORY ISSUE ===")

    pp = PaycheckProcessor()
    tm = TransactionManager()

    try:
        # Get current state before any processing
        print("\n1. INITIAL STATE:")
        default_savings = tm.get_default_savings_account()
        if default_savings:
            print(f"   Safety Saving balance: ${default_savings.running_total:.2f}")
            print(f"   Safety Saving history: {default_savings.get_balance_history_copy()}")

        # Process a test paycheck to see what happens
        print("\n2. PROCESSING TEST PAYCHECK ($1500):")
        paycheck_amount = 1500.0
        paycheck_date = date.today()
        week_start_date = date.today()

        # Monkey patch the record_balance_history method to add debug info
        original_record_method = pp.record_balance_history

        def debug_record_balance_history():
            print("\n   [DEBUG] record_balance_history() called:")
            accounts = tm.get_all_accounts()
            for account in accounts:
                if 'safety' in account.name.lower():
                    print(f"     {account.name} balance before recording: ${account.running_total:.2f}")

            # Call original method
            original_record_method()

            # Check what was recorded
            for account in accounts:
                if 'safety' in account.name.lower():
                    history = account.get_balance_history_copy()
                    print(f"     {account.name} history after recording: {history}")
                    if len(history) >= 2:
                        print(f"     New history entry: ${history[-1]:.2f}")

        # Replace the method temporarily
        pp.record_balance_history = debug_record_balance_history

        # Also monitor rollover processing
        original_process_rollover = pp.process_week_rollover

        def debug_process_week_rollover(week_number):
            print(f"\n   [DEBUG] Processing rollover for Week {week_number}:")

            # Get account balance before rollover
            default_savings = tm.get_default_savings_account()
            if default_savings:
                print(f"     Safety Saving balance before rollover: ${default_savings.running_total:.2f}")

            # Call original method
            result = original_process_rollover(week_number)

            # Get account balance after rollover
            default_savings = tm.get_default_savings_account()
            if default_savings:
                print(f"     Safety Saving balance after rollover: ${default_savings.running_total:.2f}")

            return result

        pp.process_week_rollover = debug_process_week_rollover

        # Process the paycheck
        split = pp.process_new_paycheck(paycheck_amount, paycheck_date, week_start_date)

        print(f"\n3. PAYCHECK PROCESSING RESULTS:")
        print(f"   Bills deducted: ${split.bills_deducted:.2f}")
        print(f"   Week 1 allocation: ${split.week1_allocation:.2f}")
        print(f"   Week 2 allocation: ${split.week2_allocation:.2f}")

        # Check final state
        print(f"\n4. FINAL STATE:")
        final_savings = tm.get_default_savings_account()
        if final_savings:
            print(f"   Safety Saving final balance: ${final_savings.running_total:.2f}")
            final_history = final_savings.get_balance_history_copy()
            print(f"   Safety Saving final history: {final_history}")

            if len(final_history) >= 2:
                expected_change = split.week2_allocation  # This should be the rollover to savings
                actual_change = final_history[-1] - final_history[-2]
                print(f"   Expected change (Week 2 allocation): ${expected_change:.2f}")
                print(f"   Actual change in history: ${actual_change:.2f}")

                if abs(expected_change - actual_change) > 0.01:
                    print(f"   ❌ MISMATCH! Expected ${expected_change:.2f}, got ${actual_change:.2f}")
                else:
                    print(f"   ✅ History change matches expected")

        # Check what rollover transactions were actually created
        print(f"\n5. ROLLOVER TRANSACTIONS CHECK:")
        all_weeks = tm.get_all_weeks()
        for week in all_weeks[-2:]:  # Check last 2 weeks
            transactions = tm.get_transactions_by_week(week.week_number)
            rollover_txs = [tx for tx in transactions if 'rollover' in tx.description.lower() or 'surplus' in tx.description.lower() or 'deficit' in tx.description.lower()]
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
    trace_balance_history_issue()