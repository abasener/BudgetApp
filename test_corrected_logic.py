"""
Test the corrected week balance and rollover logic
"""

from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor
from models import get_db, Week, Transaction
from sqlalchemy import or_

def test_corrected_logic():
    """Test the corrected week balance calculation"""

    print("=== CORRECTED LOGIC TEST ===")

    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        db = get_db()

        # STEP 1: Clean slate
        print("\n1. CLEANING STATE:")
        # Remove rollover transactions only
        rollover_transactions = db.query(Transaction).filter(
            or_(
                Transaction.description.like("%rollover%"),
                Transaction.description.like("%End-of-period%"),
                Transaction.category == "Rollover"
            )
        ).all()
        print(f"  Removing {len(rollover_transactions)} rollover transactions")
        for tx in rollover_transactions:
            db.delete(tx)
        db.commit()

        # Reset week rollover flags only
        all_weeks = db.query(Week).order_by(Week.week_number).all()
        for week in all_weeks:
            week.rollover_applied = False
        db.commit()

        # STEP 2: Check current state (should have paycheck and bill allocations)
        print("\n2. CURRENT STATE (after removing rollovers):")
        for week in all_weeks:
            print(f"  Week {week.week_number}: base allocation ${week.running_total:.2f}")

        week1_transactions = db.query(Transaction).filter(Transaction.week_number == 1).all()
        print(f"  Week 1 transactions ({len(week1_transactions)}):")
        for tx in week1_transactions:
            print(f"    {tx.transaction_type}: ${tx.amount:.2f} - {tx.description}")

        # STEP 3: Test Week 1 rollover calculation
        print("\n3. WEEK 1 ROLLOVER CALCULATION:")
        rollover = paycheck_processor.calculate_week_rollover(1)
        print(f"  Week 1 allocated: ${rollover.allocated_amount:.2f}")
        print(f"  Week 1 spent: ${rollover.spent_amount:.2f}")
        print(f"  Week 1 rollover: ${rollover.rollover_amount:.2f}")

        print(f"\n  Expected logic:")
        print(f"    Allocated: ${-456.25:.2f} (after bills deducted)")
        print(f"    Spent: $0.00 (no spending transactions)")
        print(f"    Rollover: ${-456.25:.2f} (deficit)")

        # STEP 4: Test corrected UI calculation
        print("\n4. WEEK BALANCE CALCULATION (UI Logic):")

        # Week 1 (should have no rollover income/deficit)
        week1 = next((w for w in all_weeks if w.week_number == 1), None)
        week1_tx = db.query(Transaction).filter(Transaction.week_number == 1).all()

        base_allocation = week1.running_total
        rollover_income = sum(t.amount for t in week1_tx if t.transaction_type == "income" and "rollover" in t.description.lower())
        rollover_deficit = sum(t.amount for t in week1_tx if t.transaction_type == "spending" and "rollover" in t.description.lower())
        week1_starting = base_allocation + rollover_income - rollover_deficit

        print(f"  Week 1:")
        print(f"    Base allocation: ${base_allocation:.2f}")
        print(f"    Rollover income: ${rollover_income:.2f}")
        print(f"    Rollover deficit: ${rollover_deficit:.2f}")
        print(f"    Starting amount: ${week1_starting:.2f}")

        # STEP 5: Process rollover and test Week 2
        print("\n5. PROCESSING WEEK 1 ROLLOVER:")
        paycheck_processor.rollover_to_week(rollover, 2)

        # Check Week 2 after rollover
        week2 = next((w for w in all_weeks if w.week_number == 2), None)
        week2_tx = db.query(Transaction).filter(Transaction.week_number == 2).all()

        base_allocation_2 = week2.running_total
        rollover_income_2 = sum(t.amount for t in week2_tx if t.transaction_type == "income" and "rollover" in t.description.lower())
        rollover_deficit_2 = sum(t.amount for t in week2_tx if t.transaction_type == "spending" and "rollover" in t.description.lower())
        week2_starting = base_allocation_2 + rollover_income_2 - rollover_deficit_2

        print(f"  Week 2 after rollover:")
        print(f"    Base allocation: ${base_allocation_2:.2f}")
        print(f"    Rollover income: ${rollover_income_2:.2f}")
        print(f"    Rollover deficit: ${rollover_deficit_2:.2f}")
        print(f"    Starting amount: ${week2_starting:.2f}")

        # STEP 6: Verify expected results
        print("\n6. VERIFICATION:")
        print(f"  Expected results:")
        print(f"    Week 1 starting: ${-456.25:.2f}")
        print(f"    Week 2 starting: ${-912.50:.2f} (base ${-456.25:.2f} + rollover ${-456.25:.2f})")

        results_correct = (
            abs(week1_starting - (-456.25)) < 0.01 and
            abs(week2_starting - (-912.50)) < 0.01
        )

        print(f"  Results correct: {results_correct}")
        if not results_correct:
            print(f"    Week 1 actual: ${week1_starting:.2f} (expected ${-456.25:.2f})")
            print(f"    Week 2 actual: ${week2_starting:.2f} (expected ${-912.50:.2f})")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    test_corrected_logic()