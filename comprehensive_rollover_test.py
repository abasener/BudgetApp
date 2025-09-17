"""
Comprehensive test of the complete rollover system
"""

from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor
from models import get_db, Week, Transaction

def comprehensive_rollover_test():
    """Test the complete rollover system from Week 1 to savings"""

    print("=== COMPREHENSIVE ROLLOVER SYSTEM TEST ===")

    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        db = get_db()

        # STEP 1: Clean slate
        print("\n1. CLEANING SLATE:")
        # Remove all rollover transactions
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

        # Reset all weeks
        all_weeks = db.query(Week).order_by(Week.week_number).all()
        for week in all_weeks:
            week.running_total = -456.25  # Base allocation after deductions
            week.rollover_applied = False
        db.commit()

        # Reset savings account
        savings = transaction_manager.get_default_savings_account()
        original_savings_balance = 0.0  # Start with zero for clean test
        transaction_manager.update_account_balance(savings.id, original_savings_balance)

        print(f"  Reset {len(all_weeks)} weeks to $-456.25, rollover_applied = False")
        print(f"  Reset savings account to ${original_savings_balance:.2f}")

        # STEP 2: Run automatic rollover processing
        print("\n2. RUNNING AUTOMATIC ROLLOVER PROCESSING:")
        paycheck_processor.check_and_process_rollovers()

        # STEP 3: Check final results
        print("\n3. FINAL RESULTS:")
        updated_weeks = db.query(Week).order_by(Week.week_number).all()
        for week in updated_weeks:
            # Calculate effective balance
            week_transactions = db.query(Transaction).filter(Transaction.week_number == week.week_number).all()
            base_allocation = week.running_total
            income_total = sum(t.amount for t in week_transactions if t.transaction_type == "income")
            rollover_deficits = sum(t.amount for t in week_transactions if t.transaction_type == "spending" and "rollover" in t.description.lower())
            effective_balance = base_allocation + income_total - rollover_deficits

            print(f"  Week {week.week_number}:")
            print(f"    Base allocation: ${base_allocation:.2f}")
            print(f"    Effective balance: ${effective_balance:.2f}")
            print(f"    Rollover applied: {week.rollover_applied}")

        updated_savings = transaction_manager.get_default_savings_account()
        print(f"  Savings account: ${updated_savings.running_total:.2f}")

        # STEP 4: Verify expected results
        print("\n4. VERIFICATION:")
        print("  Expected results:")
        print("    Week 1: Base -$456.25, Effective -$456.25 (no rollover in)")
        print("    Week 2: Base -$456.25, Effective -$912.50 (receives -$456.25 from Week 1)")
        print("    Savings: -$912.50 (receives deficit from Week 2)")

        week1 = next((w for w in updated_weeks if w.week_number == 1), None)
        week2 = next((w for w in updated_weeks if w.week_number == 2), None)

        if week1 and week2:
            # Calculate effective balances
            week1_tx = db.query(Transaction).filter(Transaction.week_number == 1).all()
            week1_deficit_rollover = sum(t.amount for t in week1_tx if t.transaction_type == "spending" and "rollover" in t.description.lower())
            week1_effective = week1.running_total - week1_deficit_rollover

            week2_tx = db.query(Transaction).filter(Transaction.week_number == 2).all()
            week2_deficit_rollover = sum(t.amount for t in week2_tx if t.transaction_type == "spending" and "rollover" in t.description.lower())
            week2_effective = week2.running_total - week2_deficit_rollover

            results_correct = (
                abs(week1_effective - (-456.25)) < 0.01 and
                abs(week2_effective - (-912.50)) < 0.01 and
                abs(updated_savings.running_total - (-912.50)) < 0.01
            )

            print(f"  Results correct: {results_correct}")
            if not results_correct:
                print(f"    Week 1 effective: ${week1_effective:.2f} (expected -$456.25)")
                print(f"    Week 2 effective: ${week2_effective:.2f} (expected -$912.50)")
                print(f"    Savings: ${updated_savings.running_total:.2f} (expected -$912.50)")

        # STEP 5: Show all rollover transactions created
        print("\n5. ROLLOVER TRANSACTIONS CREATED:")
        final_rollover_transactions = db.query(Transaction).filter(
            or_(
                Transaction.description.like("%rollover%"),
                Transaction.description.like("%End-of-period%"),
                Transaction.category == "Rollover"
            )
        ).order_by(Transaction.week_number).all()

        print(f"  Total rollover transactions: {len(final_rollover_transactions)}")
        for tx in final_rollover_transactions:
            account_name = ""
            if hasattr(tx, 'account_saved_to') and tx.account_saved_to:
                account_name = f" -> {tx.account_saved_to}"
            print(f"    Week {tx.week_number}: {tx.transaction_type} ${tx.amount:.2f} - {tx.description}{account_name}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    # Import needed for or_ function
    from sqlalchemy import or_
    comprehensive_rollover_test()