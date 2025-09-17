"""
Test script for cascading rollover updates:
Week 1 transaction change -> Week 1 rollover recalculation -> Week 2 rollover recalculation -> Savings update
"""

from datetime import date, timedelta
from services.paycheck_processor import PaycheckProcessor
from services.transaction_manager import TransactionManager
from models import get_db, Week, Transaction, TransactionType

def test_cascading_rollover():
    """Test that adjusting Week 1 causes Week 2 rollover to savings to be recalculated"""

    print("Testing Cascading Rollover Updates")
    print("=" * 50)

    # Initialize services
    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        # Create test weeks in a bi-weekly pair
        db = get_db()

        # Week 1 of bi-weekly period
        test_week1 = Week(
            week_number=301,
            start_date=date.today() - timedelta(days=14),
            end_date=date.today() - timedelta(days=8),
            running_total=500.0,  # Allocated $500
            rollover_applied=False
        )

        # Week 2 of bi-weekly period (paired with Week 1)
        test_week2 = Week(
            week_number=302,
            start_date=date.today() - timedelta(days=7),
            end_date=date.today() - timedelta(days=1),
            running_total=500.0,  # Allocated $500
            rollover_applied=False
        )

        # Add weeks to database
        db.add(test_week1)
        db.add(test_week2)
        db.commit()

        print(f"Created bi-weekly pair:")
        print(f"  Week {test_week1.week_number}: ${test_week1.running_total:.2f}")
        print(f"  Week {test_week2.week_number}: ${test_week2.running_total:.2f}")

        # Add initial spending to both weeks
        week1_spending = Transaction(
            transaction_type=TransactionType.SPENDING.value,
            week_number=test_week1.week_number,
            amount=300.0,  # Spend $300 out of $500 → $200 surplus
            date=test_week1.start_date + timedelta(days=2),
            description="Initial Week 1 spending",
            category="Food",
            include_in_analytics=True
        )

        week2_spending = Transaction(
            transaction_type=TransactionType.SPENDING.value,
            week_number=test_week2.week_number,
            amount=400.0,  # Spend $400 out of $500 → $100 surplus
            date=test_week2.start_date + timedelta(days=2),
            description="Initial Week 2 spending",
            category="Gas",
            include_in_analytics=True
        )

        # Add via DB to avoid triggering rollover yet
        db.add(week1_spending)
        db.add(week2_spending)
        db.commit()

        print(f"\\nInitial spending added:")
        print(f"  Week {test_week1.week_number}: Spent $300 -> $200 surplus expected")
        print(f"  Week {test_week2.week_number}: Spent $400 -> $100 surplus expected")

        # Process initial rollovers
        print(f"\\nProcessing initial rollovers...")
        paycheck_processor.check_and_process_rollovers()

        # Check initial state
        week1_after_initial = transaction_manager.get_week_by_number(test_week1.week_number)
        week2_after_initial = transaction_manager.get_week_by_number(test_week2.week_number)

        print(f"After initial rollover processing:")
        print(f"  Week {week1_after_initial.week_number}: total=${week1_after_initial.running_total:.2f}, rollover_applied={week1_after_initial.rollover_applied}")
        print(f"  Week {week2_after_initial.week_number}: total=${week2_after_initial.running_total:.2f}, rollover_applied={week2_after_initial.rollover_applied}")

        # Expected: Week 1's $200 surplus should go to Week 2, making Week 2 total = $500 + $200 = $700
        # Week 2 surplus should be $700 - $400 = $300, which goes to savings

        # Get savings account balance before
        default_savings = transaction_manager.get_default_savings_account()
        savings_balance_before = default_savings.running_total if default_savings else 0
        print(f"  Savings account balance: ${savings_balance_before:.2f}")

        # Now add MORE spending to Week 1 (this should cascade)
        print(f"\\nAdding additional spending to Week {test_week1.week_number} (should cascade to Week 2 and Savings)...")

        additional_spending_data = {
            "transaction_type": TransactionType.SPENDING.value,
            "week_number": test_week1.week_number,
            "amount": 150.0,  # Spend additional $150
            "date": test_week1.start_date + timedelta(days=4),
            "description": "Additional Week 1 spending - should cascade",
            "category": "Entertainment",
            "include_in_analytics": True
        }

        # This should trigger rollover recalculation for Week 1
        additional_transaction = transaction_manager.add_transaction(additional_spending_data)
        print(f"Added transaction: ${additional_transaction.amount:.2f}")

        # Check state after cascading update
        week1_final = transaction_manager.get_week_by_number(test_week1.week_number)
        week2_final = transaction_manager.get_week_by_number(test_week2.week_number)
        default_savings_final = transaction_manager.get_default_savings_account()
        savings_balance_after = default_savings_final.running_total if default_savings_final else 0

        print(f"\\nAfter cascading update:")
        print(f"  Week {week1_final.week_number}: total=${week1_final.running_total:.2f}, rollover_applied={week1_final.rollover_applied}")
        print(f"  Week {week2_final.week_number}: total=${week2_final.running_total:.2f}, rollover_applied={week2_final.rollover_applied}")
        print(f"  Savings account balance: ${savings_balance_after:.2f}")

        # Calculate expected values
        week1_total_spent = 300.0 + 150.0  # $450 total spent
        week1_expected_surplus = 500.0 - week1_total_spent  # $50 surplus (reduced from $200)
        week2_expected_total = 500.0 + week1_expected_surplus  # $550 (down from $700)
        week2_expected_surplus = week2_expected_total - 400.0  # $150 surplus (down from $300)

        print(f"\\nExpected calculations:")
        print(f"  Week {test_week1.week_number} total spent: ${week1_total_spent:.2f}")
        print(f"  Week {test_week1.week_number} expected surplus: ${week1_expected_surplus:.2f}")
        print(f"  Week {test_week2.week_number} expected total: ${week2_expected_total:.2f}")
        print(f"  Week {test_week2.week_number} expected surplus to savings: ${week2_expected_surplus:.2f}")

        # Check if the cascading worked
        savings_change = savings_balance_after - savings_balance_before
        print(f"  Savings balance change: ${savings_change:.2f}")

        # Verify cascading behavior
        if week2_final.rollover_applied == False:
            print("\\n[SUCCESS] Week 2 rollover flag was reset (cascading worked)")
        else:
            print("\\n[ISSUE] Week 2 rollover flag was NOT reset (cascading may not work)")

        expected_week2_total = 500.0 + week1_expected_surplus
        if abs(week2_final.running_total - expected_week2_total) < 0.01:
            print("[SUCCESS] Week 2 total was correctly updated with new Week 1 rollover")
        else:
            print(f"[ISSUE] Week 2 total is ${week2_final.running_total:.2f}, expected ${expected_week2_total:.2f}")

        print("\\nCascading rollover test completed!")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up test data
        try:
            # Delete test transactions
            db.query(Transaction).filter(Transaction.week_number.in_([301, 302])).delete()
            # Delete test weeks
            db.query(Week).filter(Week.week_number.in_([301, 302])).delete()
            db.commit()
            print("\\nTest data cleaned up")
        except:
            pass

        # Close connections
        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    test_cascading_rollover()