"""
Test Week 2 rollover to savings
"""

from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor
from models import get_db, Week, Transaction

def test_week2_savings_rollover():
    """Test that Week 2 properly rolls over to savings"""

    print("=== WEEK 2 SAVINGS ROLLOVER TEST ===")

    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        db = get_db()

        # STEP 1: Check current state
        print("\n1. CURRENT STATE:")
        weeks = db.query(Week).order_by(Week.week_number).all()
        savings = transaction_manager.get_default_savings_account()

        for week in weeks:
            print(f"  Week {week.week_number}: rollover_applied={week.rollover_applied}")

        print(f"  Savings balance: ${savings.running_total:.2f}")

        # STEP 2: Mark Week 1 as processed and force Week 2 rollover
        print("\n2. FORCING WEEK 2 ROLLOVER TO SAVINGS:")
        week1 = next((w for w in weeks if w.week_number == 1), None)
        week2 = next((w for w in weeks if w.week_number == 2), None)

        if week1:
            week1.rollover_applied = True
            print(f"  Marked Week 1 as processed")

        if week2:
            week2.rollover_applied = False
            print(f"  Reset Week 2 rollover flag")

        db.commit()

        # Force rollover processing specifically for Week 2
        print("\n3. PROCESSING WEEK 2 ROLLOVER:")
        rollover2 = paycheck_processor.calculate_week_rollover(2)
        print(f"  Week 2 rollover calculation:")
        print(f"    Allocated: ${rollover2.allocated_amount:.2f}")
        print(f"    Spent: ${rollover2.spent_amount:.2f}")
        print(f"    Rollover: ${rollover2.rollover_amount:.2f}")

        # Process Week 2 rollover to savings (no target week = goes to savings)
        paycheck_processor.process_week_rollover(2)

        # STEP 4: Check results
        print("\n4. RESULTS AFTER WEEK 2 ROLLOVER:")
        updated_savings = transaction_manager.get_default_savings_account()
        print(f"  Savings balance: ${updated_savings.running_total:.2f}")

        # Check for savings transactions
        savings_transactions = db.query(Transaction).filter(
            Transaction.account_id == updated_savings.id
        ).all()
        print(f"  Savings transactions: {len(savings_transactions)}")
        for tx in savings_transactions:
            print(f"    Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}")

        # STEP 5: Verify expected result
        print("\n5. VERIFICATION:")
        expected_savings = -912.50  # Week 2 deficit should go to savings
        actual_savings = updated_savings.running_total

        print(f"  Expected savings: ${expected_savings:.2f}")
        print(f"  Actual savings: ${actual_savings:.2f}")

        # Check if close enough (allowing for existing balance)
        new_deficit_added = any(
            tx.week_number == 2 and tx.amount == -912.50
            for tx in savings_transactions
        )

        print(f"  Week 2 deficit transaction added: {new_deficit_added}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    test_week2_savings_rollover()