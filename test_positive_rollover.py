"""
Test script to create a positive rollover to savings and verify the transaction is created
"""

from datetime import date, timedelta
from services.paycheck_processor import PaycheckProcessor
from services.transaction_manager import TransactionManager
from models import get_db, Week, Transaction, TransactionType

def test_positive_rollover():
    """Test creating a positive rollover to savings and verify transaction creation"""

    print("Testing Positive Rollover to Savings")
    print("=" * 40)

    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        db = get_db()

        # Create a test week that will have a surplus
        test_week = Week(
            week_number=500,
            start_date=date.today() - timedelta(days=7),
            end_date=date.today() - timedelta(days=1),
            running_total=300.0,  # Allocated $300
            rollover_applied=False
        )

        db.add(test_week)
        db.commit()

        # Add a small spending transaction (spend $100 out of $300 → $200 surplus)
        spending_transaction = Transaction(
            transaction_type=TransactionType.SPENDING.value,
            week_number=test_week.week_number,
            amount=100.0,
            date=test_week.start_date + timedelta(days=2),
            description="Test spending to create surplus",
            category="Food",
            include_in_analytics=True
        )

        db.add(spending_transaction)
        db.commit()

        print(f"Created test Week {test_week.week_number}")
        print(f"Allocated: ${test_week.running_total:.2f}")
        print(f"Spent: ${spending_transaction.amount:.2f}")
        print(f"Expected surplus: ${test_week.running_total - spending_transaction.amount:.2f}")

        # Get savings account balance before
        default_savings = transaction_manager.get_default_savings_account()
        balance_before = default_savings.running_total
        print(f"\\nSavings account balance before: ${balance_before:.2f}")

        # Process the rollover (this should be a Week 2 rollover to savings)
        # Let's manually set this as a Week 2 by making week_number even
        test_week.week_number = 500  # Even number = Week 2
        db.commit()

        print(f"\\nProcessing rollover for Week {test_week.week_number} (should go to savings)...")
        paycheck_processor.check_and_process_rollovers()

        # Check savings account balance after
        default_savings_after = transaction_manager.get_default_savings_account()
        balance_after = default_savings_after.running_total
        print(f"Savings account balance after: ${balance_after:.2f}")
        print(f"Balance change: ${balance_after - balance_before:.2f}")

        # Check if rollover transaction was created
        all_transactions = transaction_manager.get_all_transactions()
        rollover_transactions = [
            t for t in all_transactions
            if (t.transaction_type == TransactionType.SAVING.value and
                t.description and "end-of-period surplus" in t.description.lower() and
                t.week_number == test_week.week_number)
        ]

        print(f"\\nRollover transactions found: {len(rollover_transactions)}")
        for tx in rollover_transactions:
            print(f"  - {tx.date}: ${tx.amount:.2f}")
            print(f"    Description: {tx.description}")
            print(f"    Account ID: {getattr(tx, 'account_id', 'None')}")
            print(f"    Account Name: {getattr(tx, 'account_saved_to', 'None')}")

        # Verify the transaction is properly linked
        if rollover_transactions:
            tx = rollover_transactions[0]
            if hasattr(tx, 'account_id') and tx.account_id == default_savings.id:
                print("\\n✅ SUCCESS: Rollover transaction properly linked to savings account!")
            else:
                print("\\n❌ ISSUE: Rollover transaction not properly linked to savings account")
        else:
            print("\\n❌ ISSUE: No rollover transaction was created")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up test data
        try:
            db.query(Transaction).filter(Transaction.week_number == 500).delete()
            db.query(Week).filter(Week.week_number == 500).delete()
            db.commit()
            print("\\nTest data cleaned up")
        except:
            pass

        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    test_positive_rollover()