"""
Test Week 2 rollover to savings
"""

from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor
from models import get_db, Week, Transaction

def test_week2_rollover():
    """Test Week 2 rollover to savings"""

    print("=== WEEK 2 ROLLOVER TO SAVINGS TEST ===")

    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        db = get_db()

        # STEP 1: Current state
        print("\n1. CURRENT STATE:")
        all_weeks = db.query(Week).order_by(Week.week_number).all()
        for week in all_weeks:
            print(f"  Week {week.week_number}: ${week.running_total:.2f}, rollover_applied: {week.rollover_applied}")

        savings = transaction_manager.get_default_savings_account()
        print(f"  Savings: ${savings.running_total:.2f}")

        # STEP 2: Calculate Week 2 rollover
        print("\n2. WEEK 2 ROLLOVER CALCULATION:")
        week2_transactions = db.query(Transaction).filter(Transaction.week_number == 2).all()
        print(f"  Week 2 transactions:")
        for tx in week2_transactions:
            print(f"    {tx.transaction_type}: ${tx.amount:.2f} - {tx.description}")

        rollover = paycheck_processor.calculate_week_rollover(2)
        print(f"  Week 2 allocated: ${rollover.allocated_amount:.2f}")
        print(f"  Week 2 spent: ${rollover.spent_amount:.2f}")
        print(f"  Week 2 rollover: ${rollover.rollover_amount:.2f}")

        # STEP 3: Mark Week 1 as processed and test Week 2 rollover to savings
        print("\n3. PROCESSING WEEK 2 ROLLOVER TO SAVINGS:")
        week1 = db.query(Week).filter(Week.week_number == 1).first()
        if week1:
            week1.rollover_applied = True
            db.commit()
            print("  Marked Week 1 as processed")

        # Process Week 2 rollover to savings
        paycheck_processor.process_week_rollover(2)  # No target = rollover to savings

        # STEP 4: Check results
        print("\n4. RESULTS:")
        updated_weeks = db.query(Week).order_by(Week.week_number).all()
        for week in updated_weeks:
            print(f"  Week {week.week_number}: ${week.running_total:.2f}, rollover_applied: {week.rollover_applied}")

        updated_savings = transaction_manager.get_default_savings_account()
        print(f"  Savings: ${updated_savings.running_total:.2f}")

        # Check savings transactions
        savings_transactions = db.query(Transaction).filter(
            Transaction.account_id == updated_savings.id
        ).all()
        print(f"  Savings transactions: {len(savings_transactions)}")
        for tx in savings_transactions:
            print(f"    Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    test_week2_rollover()