"""
Test script for rollover trigger functionality when adding transactions to existing weeks
"""

from datetime import date, timedelta
from services.paycheck_processor import PaycheckProcessor
from services.transaction_manager import TransactionManager
from models import get_db, Week, Transaction, TransactionType

def test_rollover_trigger():
    """Test that adding transactions to existing weeks triggers rollover recalculation"""

    print("Testing Rollover Trigger Functionality")
    print("=" * 50)

    # Initialize services
    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        # Create test weeks that have already been processed
        db = get_db()

        # Create Week 1 (already processed with rollover applied)
        test_week1 = Week(
            week_number=201,
            start_date=date.today() - timedelta(days=14),
            end_date=date.today() - timedelta(days=8),
            running_total=500.0,  # Allocated $500
            rollover_applied=True  # Already processed
        )

        # Create Week 2 (already processed)
        test_week2 = Week(
            week_number=202,
            start_date=date.today() - timedelta(days=7),
            end_date=date.today() - timedelta(days=1),
            running_total=650.0,  # Already includes $150 rollover from Week 1
            rollover_applied=True  # Already processed
        )

        # Add weeks to database
        db.add(test_week1)
        db.add(test_week2)
        db.commit()

        print(f"Created test weeks with rollover already applied:")
        print(f"  Week {test_week1.week_number}: ${test_week1.running_total:.2f}, rollover_applied={test_week1.rollover_applied}")
        print(f"  Week {test_week2.week_number}: ${test_week2.running_total:.2f}, rollover_applied={test_week2.rollover_applied}")

        # Add existing spending transactions (simulate what was already there)
        existing_transaction1 = Transaction(
            transaction_type=TransactionType.SPENDING.value,
            week_number=test_week1.week_number,
            amount=200.0,
            date=test_week1.start_date + timedelta(days=1),
            description="Existing spending for Week 1",
            category="Food",
            include_in_analytics=True
        )

        existing_transaction2 = Transaction(
            transaction_type=TransactionType.SPENDING.value,
            week_number=test_week2.week_number,
            amount=300.0,
            date=test_week2.start_date + timedelta(days=1),
            description="Existing spending for Week 2",
            category="Gas",
            include_in_analytics=True
        )

        # Add existing transactions directly to DB to avoid triggering recalculation
        db.add(existing_transaction1)
        db.add(existing_transaction2)
        db.commit()

        print(f"\\nAdded existing transactions (should NOT trigger rollover):")
        print(f"  Week {test_week1.week_number}: Spent $200")
        print(f"  Week {test_week2.week_number}: Spent $300")

        # Verify rollover flags are still True
        week1_check = transaction_manager.get_week_by_number(test_week1.week_number)
        week2_check = transaction_manager.get_week_by_number(test_week2.week_number)
        print(f"\\nBefore adding new transaction:")
        print(f"  Week {week1_check.week_number} rollover_applied: {week1_check.rollover_applied}")
        print(f"  Week {week2_check.week_number} rollover_applied: {week2_check.rollover_applied}")

        # Now add a NEW transaction using the transaction manager (should trigger rollover)
        print(f"\\nAdding NEW transaction to Week {test_week1.week_number} (SHOULD trigger rollover recalculation)...")

        new_transaction_data = {
            "transaction_type": TransactionType.SPENDING.value,
            "week_number": test_week1.week_number,
            "amount": 75.0,
            "date": test_week1.start_date + timedelta(days=3),
            "description": "Forgot about this expense",
            "category": "Entertainment",
            "include_in_analytics": True
        }

        # This should trigger the rollover recalculation
        new_transaction = transaction_manager.add_transaction(new_transaction_data)
        print(f"Added transaction: ${new_transaction.amount:.2f} for {new_transaction.description}")

        # Check if rollover flag was reset
        week1_after = transaction_manager.get_week_by_number(test_week1.week_number)
        week2_after = transaction_manager.get_week_by_number(test_week2.week_number)

        print(f"\\nAfter adding new transaction:")
        print(f"  Week {week1_after.week_number} rollover_applied: {week1_after.rollover_applied}")
        print(f"  Week {week2_after.week_number} rollover_applied: {week2_after.rollover_applied}")

        # Expected results:
        # - Week 1 rollover_applied should be False (got reset and recalculated)
        # - Week 2 might also be affected if Week 1's rollover changed

        # Calculate new expected totals
        week1_total_spent = 200.0 + 75.0  # $275 total spent out of $500
        week1_expected_rollover = 500.0 - week1_total_spent  # $225 surplus

        print(f"\\nExpected calculations:")
        print(f"  Week {test_week1.week_number} total spent: ${week1_total_spent:.2f}")
        print(f"  Week {test_week1.week_number} expected rollover: ${week1_expected_rollover:.2f}")

        # Check if Week 2's total was updated with new rollover
        week2_expected_total = 650.0 + (week1_expected_rollover - 150.0)  # Adjust for the difference
        print(f"  Week {test_week2.week_number} expected total after rollover adjustment: ${week2_expected_total:.2f}")
        print(f"  Week {test_week2.week_number} actual total: ${week2_after.running_total:.2f}")

        # Test adding a SAVING transaction too
        print(f"\\nAdding SAVING transaction to Week {test_week2.week_number} (SHOULD also trigger rollover recalculation)...")

        saving_transaction_data = {
            "transaction_type": TransactionType.SAVING.value,
            "week_number": test_week2.week_number,
            "amount": 50.0,
            "date": test_week2.start_date + timedelta(days=4),
            "description": "Extra savings this week",
            "account_id": 1  # Assume account exists
        }

        saving_transaction = transaction_manager.add_transaction(saving_transaction_data)
        print(f"Added saving transaction: ${saving_transaction.amount:.2f}")

        # Check rollover flags again
        week2_final = transaction_manager.get_week_by_number(test_week2.week_number)
        print(f"\\nAfter adding saving transaction:")
        print(f"  Week {test_week2.week_number} rollover_applied: {week2_final.rollover_applied}")

        print("\\nTrigger test completed successfully!")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up test data
        try:
            # Delete test transactions
            db.query(Transaction).filter(Transaction.week_number.in_([201, 202])).delete()
            # Delete test weeks
            db.query(Week).filter(Week.week_number.in_([201, 202])).delete()
            db.commit()
            print("\\nTest data cleaned up")
        except:
            pass

        # Close connections
        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    test_rollover_trigger()