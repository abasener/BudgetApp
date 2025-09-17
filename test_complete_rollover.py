"""
Test the complete rollover flow to ensure UI will display correctly
"""

from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor
from models import get_db, Week, Transaction

def test_complete_rollover():
    """Test complete rollover flow including Week 2 rollover to savings"""

    print("=== COMPLETE ROLLOVER FLOW TEST ===")

    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        db = get_db()

        # STEP 1: Check current state after paycheck processing
        print("\n1. CURRENT STATE (after paycheck):")
        weeks = db.query(Week).order_by(Week.week_number).all()
        transactions = db.query(Transaction).order_by(Transaction.week_number, Transaction.id).all()

        for week in weeks:
            print(f"  Week {week.week_number}: allocation=${week.running_total:.2f}, rollover_applied={week.rollover_applied}")

        print(f"  Transactions: {len(transactions)}")
        for tx in transactions:
            print(f"    Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}")

        # STEP 2: Calculate UI display values for each week
        print("\n2. UI DISPLAY VALUES:")
        for week in weeks:
            week_tx = [tx for tx in transactions if tx.week_number == week.week_number]

            base_allocation = week.running_total
            rollover_income = sum(tx.amount for tx in week_tx if tx.transaction_type == "income" and "rollover" in tx.description.lower())
            rollover_deficit = sum(tx.amount for tx in week_tx if tx.transaction_type == "spending" and "rollover" in tx.description.lower())
            starting_amount = base_allocation + rollover_income - rollover_deficit

            actual_spending = sum(tx.amount for tx in week_tx if tx.transaction_type == "spending" and "rollover" not in tx.description.lower())
            current_amount = starting_amount - actual_spending

            print(f"  Week {week.week_number} UI values:")
            print(f"    Base allocation: ${base_allocation:.2f}")
            print(f"    Rollover income: ${rollover_income:.2f}")
            print(f"    Rollover deficit: ${rollover_deficit:.2f}")
            print(f"    Starting amount: ${starting_amount:.2f}")
            print(f"    Actual spending: ${actual_spending:.2f}")
            print(f"    Current amount: ${current_amount:.2f}")

        # STEP 3: Force process all rollovers
        print("\n3. FORCING ROLLOVER PROCESSING:")
        # Reset rollover flags
        for week in weeks:
            week.rollover_applied = False
        db.commit()

        # Process all rollovers
        paycheck_processor.check_and_process_rollovers()

        # STEP 4: Check results after rollover processing
        print("\n4. AFTER ROLLOVER PROCESSING:")
        updated_weeks = db.query(Week).order_by(Week.week_number).all()
        updated_transactions = db.query(Transaction).order_by(Transaction.week_number, Transaction.id).all()
        updated_savings = transaction_manager.get_default_savings_account()

        for week in updated_weeks:
            print(f"  Week {week.week_number}: allocation=${week.running_total:.2f}, rollover_applied={week.rollover_applied}")

        print(f"  Total transactions: {len(updated_transactions)}")
        rollover_transactions = [tx for tx in updated_transactions if "rollover" in tx.description.lower() or "end-of-period" in tx.description.lower()]
        print(f"  Rollover transactions: {len(rollover_transactions)}")
        for tx in rollover_transactions:
            account_info = ""
            if hasattr(tx, 'account_saved_to') and tx.account_saved_to:
                account_info = f" -> {tx.account_saved_to}"
            print(f"    Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}{account_info}")

        print(f"  Savings account balance: ${updated_savings.running_total:.2f}")

        # STEP 5: Calculate final UI display values
        print("\n5. FINAL UI DISPLAY VALUES:")
        for week in updated_weeks:
            week_tx = [tx for tx in updated_transactions if tx.week_number == week.week_number]

            base_allocation = week.running_total
            rollover_income = sum(tx.amount for tx in week_tx if tx.transaction_type == "income" and "rollover" in tx.description.lower())
            rollover_deficit = sum(tx.amount for tx in week_tx if tx.transaction_type == "spending" and "rollover" in tx.description.lower())
            starting_amount = base_allocation + rollover_income - rollover_deficit

            actual_spending = sum(tx.amount for tx in week_tx if tx.transaction_type == "spending" and "rollover" not in tx.description.lower())
            current_amount = starting_amount - actual_spending

            print(f"  Week {week.week_number} final UI values:")
            print(f"    Starting amount: ${starting_amount:.2f}")
            print(f"    Actual spending: ${actual_spending:.2f}")
            print(f"    Current amount: ${current_amount:.2f}")

        # STEP 6: Expected results verification
        print("\n6. EXPECTED RESULTS:")
        print(f"  Week 1 starting: $-456.25 (no rollover in)")
        print(f"  Week 2 starting: $-912.50 (base $-456.25 + rollover deficit $-456.25)")
        print(f"  Savings: $-912.50 (receives Week 2 deficit)")

        week1 = next((w for w in updated_weeks if w.week_number == 1), None)
        week2 = next((w for w in updated_weeks if w.week_number == 2), None)

        if week1 and week2:
            week1_tx = [tx for tx in updated_transactions if tx.week_number == 1]
            week2_tx = [tx for tx in updated_transactions if tx.week_number == 2]

            week1_starting = week1.running_total + sum(tx.amount for tx in week1_tx if tx.transaction_type == "income" and "rollover" in tx.description.lower()) - sum(tx.amount for tx in week1_tx if tx.transaction_type == "spending" and "rollover" in tx.description.lower())
            week2_starting = week2.running_total + sum(tx.amount for tx in week2_tx if tx.transaction_type == "income" and "rollover" in tx.description.lower()) - sum(tx.amount for tx in week2_tx if tx.transaction_type == "spending" and "rollover" in tx.description.lower())

            results_correct = (
                abs(week1_starting - (-456.25)) < 0.01 and
                abs(week2_starting - (-912.50)) < 0.01 and
                abs(updated_savings.running_total - (-912.50)) < 0.01
            )

            print(f"  Results correct: {results_correct}")
            if not results_correct:
                print(f"    Week 1 actual: ${week1_starting:.2f} (expected $-456.25)")
                print(f"    Week 2 actual: ${week2_starting:.2f} (expected $-912.50)")
                print(f"    Savings actual: ${updated_savings.running_total:.2f} (expected $-912.50)")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    test_complete_rollover()