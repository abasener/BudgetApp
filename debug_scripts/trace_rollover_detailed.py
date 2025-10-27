"""
Detailed trace of rollover processing to find where it's failing
"""

from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor
from models import get_db, Week, Transaction
from datetime import date

def trace_rollover_detailed():
    """Trace rollover processing step by step"""

    print("=== DETAILED ROLLOVER TRACE ===")

    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        db = get_db()

        # STEP 1: Check current state
        print("\n1. CURRENT STATE:")
        all_weeks = db.query(Week).order_by(Week.week_number).all()
        for week in all_weeks:
            print(f"  Week {week.week_number}: ${week.running_total:.2f}, rollover_applied: {week.rollover_applied}")

        savings = transaction_manager.get_default_savings_account()
        print(f"  Savings: ${savings.running_total:.2f}")

        # STEP 2: Check which weeks should be processed
        print("\n2. WEEKS THAT SHOULD BE PROCESSED:")
        weeks_pending = db.query(Week).filter(Week.rollover_applied == False).order_by(Week.week_number).all()

        for week in weeks_pending:
            next_week = db.query(Week).filter(Week.week_number == week.week_number + 1).first()
            week_ended = date.today() > week.end_date

            print(f"  Week {week.week_number}:")
            print(f"    Has next week: {next_week is not None}")
            print(f"    Week ended: {week_ended}")
            print(f"    Should process: {next_week or week_ended}")

        # STEP 3: Test rollover calculation for Week 1
        print("\n3. WEEK 1 ROLLOVER CALCULATION:")
        try:
            week1_rollover = paycheck_processor.calculate_week_rollover(1)
            print(f"  Week 1 allocated: ${week1_rollover.allocated_amount:.2f}")
            print(f"  Week 1 spent: ${week1_rollover.spent_amount:.2f}")
            print(f"  Week 1 remaining: ${week1_rollover.remaining_amount:.2f}")
            print(f"  Week 1 rollover amount: ${week1_rollover.rollover_amount:.2f}")

            # Check transactions that contribute to spent amount
            week1_transactions = transaction_manager.get_transactions_by_week(1)
            print(f"  Week 1 transactions:")
            for tx in week1_transactions:
                print(f"    {tx.transaction_type}: ${tx.amount:.2f} - {tx.description}")

        except Exception as e:
            print(f"  ERROR calculating Week 1 rollover: {e}")

        # STEP 4: Manual rollover processing with detailed logging
        print("\n4. MANUAL ROLLOVER PROCESSING:")

        # Reset Week 1 rollover flag
        week1 = db.query(Week).filter(Week.week_number == 1).first()
        if week1:
            print(f"  Resetting Week 1 rollover flag...")
            week1.rollover_applied = False
            db.commit()

        # Process Week 1 rollover manually with debug
        try:
            print(f"  Processing Week 1 rollover...")
            rollover = paycheck_processor.calculate_week_rollover(1)
            print(f"    Calculated rollover: ${rollover.rollover_amount:.2f}")

            if rollover.rollover_amount != 0:
                print(f"    Rollover amount is not zero, proceeding...")
                week2 = db.query(Week).filter(Week.week_number == 2).first()
                if week2:
                    print(f"    Week 2 exists, rolling over to Week 2")
                    print(f"    Week 2 current total: ${week2.running_total:.2f}")

                    # Call rollover_to_week directly
                    paycheck_processor.rollover_to_week(rollover, 2)

                    # Check result
                    updated_week2 = db.query(Week).filter(Week.week_number == 2).first()
                    print(f"    Week 2 total after rollover: ${updated_week2.running_total:.2f}")

                    # Check for rollover transaction
                    rollover_transactions = db.query(Transaction).filter(
                        Transaction.week_number == 2,
                        Transaction.description.like("%Rollover from Week 1%")
                    ).all()
                    print(f"    Rollover transactions found: {len(rollover_transactions)}")
                    for tx in rollover_transactions:
                        print(f"      {tx.transaction_type}: ${tx.amount:.2f} - {tx.description}")
                else:
                    print(f"    Week 2 not found!")
            else:
                print(f"    Rollover amount is zero, skipping")

        except Exception as e:
            print(f"  ERROR during manual rollover: {e}")
            import traceback
            traceback.print_exc()

        # STEP 5: Final state
        print("\n5. FINAL STATE:")
        final_weeks = db.query(Week).order_by(Week.week_number).all()
        for week in final_weeks:
            print(f"  Week {week.week_number}: ${week.running_total:.2f}, rollover_applied: {week.rollover_applied}")

        final_savings = transaction_manager.get_default_savings_account()
        print(f"  Savings: ${final_savings.running_total:.2f}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    trace_rollover_detailed()