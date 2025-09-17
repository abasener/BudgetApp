"""
Final test of simplified rollover logic
"""

from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor
from models import get_db, Week, Transaction
from datetime import date

def final_rollover_test():
    """Test simplified rollover logic without manual total updates"""

    print("=== FINAL ROLLOVER TEST ===")

    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        db = get_db()

        # STEP 1: Clean state
        print("\n1. CLEANING STATE:")
        rollover_transactions = db.query(Transaction).filter(
            Transaction.description.like("%rollover%")
        ).all()
        print(f"  Deleting {len(rollover_transactions)} existing rollover transactions")
        for tx in rollover_transactions:
            db.delete(tx)
        db.commit()

        # Reset all weeks to initial state
        all_weeks = db.query(Week).order_by(Week.week_number).all()
        for week in all_weeks:
            week.running_total = -456.25  # Base allocation after deductions
            week.rollover_applied = False

        db.commit()

        # STEP 2: Check initial state
        print("\n2. INITIAL STATE:")
        for week in all_weeks:
            print(f"  Week {week.week_number}: ${week.running_total:.2f}, rollover_applied: {week.rollover_applied}")

        # STEP 3: Calculate Week 1 rollover
        print("\n3. WEEK 1 ROLLOVER CALCULATION:")
        rollover = paycheck_processor.calculate_week_rollover(1)
        print(f"  Week 1 allocated: ${rollover.allocated_amount:.2f}")
        print(f"  Week 1 spent: ${rollover.spent_amount:.2f}")
        print(f"  Week 1 rollover: ${rollover.rollover_amount:.2f}")

        # STEP 4: Process rollover using simplified logic
        print("\n4. PROCESSING ROLLOVER:")
        paycheck_processor.rollover_to_week(rollover, 2)

        # STEP 5: Check results
        print("\n5. RESULTS:")
        updated_weeks = db.query(Week).order_by(Week.week_number).all()
        for week in updated_weeks:
            print(f"  Week {week.week_number}: ${week.running_total:.2f}, rollover_applied: {week.rollover_applied}")

        # Check created transactions
        rollover_transactions = db.query(Transaction).filter(
            Transaction.description.like("%rollover%")
        ).all()
        print(f"  Rollover transactions: {len(rollover_transactions)}")
        for tx in rollover_transactions:
            print(f"    Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}")

        # STEP 6: Test what the user expects
        print("\n6. USER EXPECTATION TEST:")
        print("  Week 1: $-456.25 (base allocation)")
        print("  Week 1 rollover: $-456.25 (deficit)")
        print("  Week 2 should show: $-456.25 (base) + $-456.25 (rollover) = $-912.50")

        week2 = db.query(Week).filter(Week.week_number == 2).first()
        week2_transactions = db.query(Transaction).filter(Transaction.week_number == 2).all()

        # Calculate Week 2 effective balance: base allocation + transactions
        base_allocation = -456.25
        transactions_total = 0
        for tx in week2_transactions:
            if tx.transaction_type == "income":
                transactions_total += tx.amount
            elif tx.transaction_type in ["spending", "bill_pay", "saving"]:
                transactions_total -= tx.amount

        effective_balance = base_allocation + transactions_total
        print(f"  Week 2 base allocation: ${base_allocation:.2f}")
        print(f"  Week 2 transactions total: ${transactions_total:.2f}")
        print(f"  Week 2 effective balance: ${effective_balance:.2f}")
        print(f"  Week 2 stored running_total: ${week2.running_total:.2f}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    final_rollover_test()