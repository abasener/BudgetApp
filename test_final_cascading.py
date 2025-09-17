"""
Final test demonstrating complete cascading rollover functionality
"""

from datetime import date, timedelta
from services.paycheck_processor import PaycheckProcessor
from services.transaction_manager import TransactionManager
from models import get_db, Week, Transaction, TransactionType

def test_final_cascading():
    """Demonstrate complete cascading rollover updates"""

    print("Final Cascading Rollover Test")
    print("=" * 40)

    # Initialize services
    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        db = get_db()

        # Create Week 1 and Week 2 (bi-weekly pair)
        week1 = Week(
            week_number=401,
            start_date=date.today() - timedelta(days=14),
            end_date=date.today() - timedelta(days=8),
            running_total=500.0,
            rollover_applied=False
        )

        week2 = Week(
            week_number=402,
            start_date=date.today() - timedelta(days=7),
            end_date=date.today() - timedelta(days=1),
            running_total=500.0,
            rollover_applied=False
        )

        db.add(week1)
        db.add(week2)
        db.commit()

        # Add initial spending: Week 1 spends $200, Week 2 spends $300
        db.add(Transaction(
            transaction_type=TransactionType.SPENDING.value,
            week_number=401,
            amount=200.0,
            date=week1.start_date + timedelta(days=1),
            description="Initial Week 1 spending",
            category="Food",
            include_in_analytics=True
        ))

        db.add(Transaction(
            transaction_type=TransactionType.SPENDING.value,
            week_number=402,
            amount=300.0,
            date=week2.start_date + timedelta(days=1),
            description="Initial Week 2 spending",
            category="Gas",
            include_in_analytics=True
        ))
        db.commit()

        print("INITIAL STATE:")
        print(f"  Week 401: $500 allocated, spent $200 -> $300 surplus")
        print(f"  Week 402: $500 allocated, spent $300 -> $200 surplus")

        # Process initial rollovers
        print("\\nProcessing initial rollovers...")
        paycheck_processor.check_and_process_rollovers()

        # Check state after initial rollover
        savings_before = transaction_manager.get_default_savings_account().running_total
        week1_after = transaction_manager.get_week_by_number(401)
        week2_after = transaction_manager.get_week_by_number(402)

        print("\\nAFTER INITIAL ROLLOVER:")
        print(f"  Week 401: ${week1_after.running_total:.2f} (rollover applied: {week1_after.rollover_applied})")
        print(f"  Week 402: ${week2_after.running_total:.2f} (rollover applied: {week2_after.rollover_applied})")
        print(f"  Savings account: ${savings_before:.2f}")
        print(f"  Expected: Week 401 $300 -> Week 402 (now $800), Week 402 $500 -> Savings")

        # Now add a "forgotten" expense to Week 1
        print("\\nAdding forgotten expense to Week 401 (should cascade)...")
        forgotten_expense = {
            "transaction_type": TransactionType.SPENDING.value,
            "week_number": 401,
            "amount": 200.0,  # Additional $200 spending
            "date": week1.start_date + timedelta(days=3),
            "description": "Forgotten expense - triggers cascade",
            "category": "Entertainment",
            "include_in_analytics": True
        }

        # This should trigger the cascade: Week 401 -> Week 402 -> Savings
        transaction_manager.add_transaction(forgotten_expense)

        # Check final state
        savings_after = transaction_manager.get_default_savings_account().running_total
        week1_final = transaction_manager.get_week_by_number(401)
        week2_final = transaction_manager.get_week_by_number(402)

        print("\\nAFTER CASCADING UPDATE:")
        print(f"  Week 401: ${week1_final.running_total:.2f} (rollover applied: {week1_final.rollover_applied})")
        print(f"  Week 402: ${week2_final.running_total:.2f} (rollover applied: {week2_final.rollover_applied})")
        print(f"  Savings account: ${savings_after:.2f}")

        # Calculate expected values
        week1_total_spent = 200.0 + 200.0  # $400 total
        week1_expected_surplus = 500.0 - week1_total_spent  # $100 surplus
        week2_expected_total = 500.0 + week1_expected_surplus  # $600
        week2_expected_surplus = week2_expected_total - 300.0  # $300 surplus

        print("\\nEXPECTED vs ACTUAL:")
        print(f"  Week 401 surplus: Expected $100, Calculated ${500.0 - week1_total_spent:.2f}")
        print(f"  Week 402 total: Expected $600, Actual ${week2_final.running_total:.2f}")
        print(f"  Week 402 surplus to savings: Expected $300")
        print(f"  Savings change: ${savings_after - savings_before:.2f}")

        # Summary
        cascade_worked = (
            abs(week2_final.running_total - 600.0) < 0.01 and
            abs((savings_after - savings_before) - (300.0 - 500.0)) < 0.01
        )

        print(f"\\nCASCADING ROLLOVER TEST: {'PASSED' if cascade_worked else 'FAILED'}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        try:
            db.query(Transaction).filter(Transaction.week_number.in_([401, 402])).delete()
            db.query(Week).filter(Week.week_number.in_([401, 402])).delete()
            db.commit()
            print("\\nTest data cleaned up")
        except:
            pass

        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    test_final_cascading()