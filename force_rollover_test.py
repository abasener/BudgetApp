"""
Force rollover processing to see what happens
"""

from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor
from models import get_db

def force_rollover_test():
    """Reset rollover flags and force processing"""

    print("Force Rollover Test")
    print("=" * 30)

    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        db = get_db()

        # Get current state
        all_weeks = transaction_manager.get_all_weeks()
        default_savings = transaction_manager.get_default_savings_account()

        print(f"BEFORE force processing:")
        weeks_sorted = sorted(all_weeks, key=lambda w: w.week_number)
        for week in weeks_sorted:
            print(f"  Week {week.week_number}: ${week.running_total:.2f}, rollover_applied: {week.rollover_applied}")
        print(f"  Savings: ${default_savings.running_total:.2f}")

        # Reset rollover flags for Weeks 1 and 2 to force reprocessing
        week1 = next((w for w in all_weeks if w.week_number == 1), None)
        week2 = next((w for w in all_weeks if w.week_number == 2), None)

        if week1:
            print(f"\nResetting Week 1 rollover flag...")
            week1.rollover_applied = False
        if week2:
            print(f"Resetting Week 2 rollover flag...")
            week2.rollover_applied = False

        db.commit()

        # Force processing
        print(f"\nForcing rollover processing...")
        paycheck_processor.check_and_process_rollovers()

        # Check results
        print(f"\nAFTER force processing:")
        updated_weeks = transaction_manager.get_all_weeks()
        updated_savings = transaction_manager.get_default_savings_account()

        weeks_sorted_after = sorted(updated_weeks, key=lambda w: w.week_number)
        for week in weeks_sorted_after:
            print(f"  Week {week.week_number}: ${week.running_total:.2f}, rollover_applied: {week.rollover_applied}")
        print(f"  Savings: ${updated_savings.running_total:.2f}")

        # Check transactions
        all_transactions = transaction_manager.get_all_transactions()
        rollover_transactions = [t for t in all_transactions if 'rollover' in t.description.lower()]

        print(f"\nRollover transactions after processing:")
        for tx in rollover_transactions:
            print(f"  Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    force_rollover_test()