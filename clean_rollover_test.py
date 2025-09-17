"""
Clean rollover transactions and test proper rollover processing
"""

from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor
from models import get_db, Week, Transaction
from datetime import date

def clean_rollover_test():
    """Clean existing rollover transactions and test proper processing"""

    print("=== CLEAN ROLLOVER TEST ===")

    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        db = get_db()

        # STEP 1: Clean all rollover transactions
        print("\n1. CLEANING EXISTING ROLLOVER TRANSACTIONS:")
        rollover_transactions = db.query(Transaction).filter(
            Transaction.description.like("%rollover%")
        ).all()

        print(f"  Found {len(rollover_transactions)} rollover transactions")
        for tx in rollover_transactions:
            print(f"    Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}")
            db.delete(tx)

        db.commit()
        print("  All rollover transactions deleted")

        # STEP 2: Reset week totals to original paycheck allocations
        print("\n2. RESETTING WEEK TOTALS:")
        all_weeks = db.query(Week).order_by(Week.week_number).all()
        for week in all_weeks:
            week.running_total = -456.25  # Original allocation after deductions
            week.rollover_applied = False
            print(f"  Week {week.week_number}: Reset to $-456.25, rollover_applied = False")

        db.commit()

        # STEP 3: Check initial state
        print("\n3. INITIAL STATE:")
        for week in all_weeks:
            print(f"  Week {week.week_number}: ${week.running_total:.2f}, rollover_applied: {week.rollover_applied}")

        savings = transaction_manager.get_default_savings_account()
        print(f"  Savings: ${savings.running_total:.2f}")

        # STEP 4: Process Week 1 rollover manually
        print("\n4. PROCESSING WEEK 1 ROLLOVER:")
        rollover = paycheck_processor.calculate_week_rollover(1)
        print(f"  Week 1 rollover amount: ${rollover.rollover_amount:.2f}")

        paycheck_processor.rollover_to_week(rollover, 2)

        # STEP 5: Check results
        print("\n5. RESULTS AFTER WEEK 1 ROLLOVER:")
        updated_weeks = db.query(Week).order_by(Week.week_number).all()
        for week in updated_weeks:
            print(f"  Week {week.week_number}: ${week.running_total:.2f}, rollover_applied: {week.rollover_applied}")

        # Check rollover transactions
        new_rollover_transactions = db.query(Transaction).filter(
            Transaction.description.like("%rollover%")
        ).all()
        print(f"  Rollover transactions created: {len(new_rollover_transactions)}")
        for tx in new_rollover_transactions:
            print(f"    Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}")

        # STEP 6: Test the fix by running it again (should not create duplicates)
        print("\n6. TESTING DUPLICATE PREVENTION:")
        print("  Running Week 1 rollover again...")
        paycheck_processor.rollover_to_week(rollover, 2)

        final_weeks = db.query(Week).order_by(Week.week_number).all()
        print("  Final week totals:")
        for week in final_weeks:
            print(f"    Week {week.week_number}: ${week.running_total:.2f}")

        final_rollover_transactions = db.query(Transaction).filter(
            Transaction.description.like("%rollover%")
        ).all()
        print(f"  Total rollover transactions: {len(final_rollover_transactions)} (should still be 1)")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    clean_rollover_test()