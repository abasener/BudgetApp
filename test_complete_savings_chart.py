"""
Complete test of new savings chart logic with real rollover transactions
"""

from datetime import date, timedelta
from services.paycheck_processor import PaycheckProcessor
from services.transaction_manager import TransactionManager
from models import get_db, Week, Transaction, TransactionType

def test_complete_savings_chart():
    """Test the complete savings chart logic with realistic data"""

    print("Complete Savings Chart Test")
    print("=" * 30)

    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        db = get_db()

        # Get current savings account balance
        default_savings = transaction_manager.get_default_savings_account()
        initial_balance = default_savings.running_total
        print(f"Initial savings balance: ${initial_balance:.2f}")

        # Create a complete bi-weekly period for testing
        test_week1 = Week(
            week_number=601,
            start_date=date(2025, 8, 1),  # Fixed date for predictable results
            end_date=date(2025, 8, 7),
            running_total=400.0,
            rollover_applied=False
        )

        test_week2 = Week(
            week_number=602,
            start_date=date(2025, 8, 8),
            end_date=date(2025, 8, 14),
            running_total=400.0,
            rollover_applied=False
        )

        db.add(test_week1)
        db.add(test_week2)
        db.commit()

        print(f"\\nCreated test bi-weekly period:")
        print(f"  Week {test_week1.week_number}: {test_week1.start_date} to {test_week1.end_date}")
        print(f"  Week {test_week2.week_number}: {test_week2.start_date} to {test_week2.end_date}")

        # Add some realistic spending to both weeks
        # Week 1: Spend $300 out of $400 → $100 surplus
        week1_spending = Transaction(
            transaction_type=TransactionType.SPENDING.value,
            week_number=test_week1.week_number,
            amount=300.0,
            date=date(2025, 8, 3),
            description="Week 1 spending",
            category="Food",
            include_in_analytics=True
        )

        # Week 2: Spend $250 out of $400 → $150 surplus (but receives $100 from Week 1)
        week2_spending = Transaction(
            transaction_type=TransactionType.SPENDING.value,
            week_number=test_week2.week_number,
            amount=250.0,
            date=date(2025, 8, 10),
            description="Week 2 spending",
            category="Gas",
            include_in_analytics=True
        )

        db.add(week1_spending)
        db.add(week2_spending)
        db.commit()

        print(f"\\nAdded spending transactions:")
        print(f"  Week {test_week1.week_number}: Spent $300 -> $100 surplus expected")
        print(f"  Week {test_week2.week_number}: Spent $250 -> Will receive $100 from Week 1")

        # Add a manual savings transaction during the period (like auto-save)
        manual_savings = Transaction(
            transaction_type=TransactionType.SAVING.value,
            week_number=test_week1.week_number,
            amount=50.0,
            date=date(2025, 8, 5),
            description="Manual savings during Week 1",
            account_id=default_savings.id,
            account_saved_to=default_savings.name
        )

        db.add(manual_savings)
        db.commit()

        print(f"  Added manual savings: $50 to {default_savings.name}")

        # Process the rollovers
        print(f"\\nProcessing rollovers...")
        paycheck_processor.check_and_process_rollovers()

        # Check final savings balance
        final_savings = transaction_manager.get_default_savings_account()
        final_balance = final_savings.running_total
        print(f"Final savings balance: ${final_balance:.2f}")
        print(f"Total change: ${final_balance - initial_balance:.2f}")

        # Now get all transactions for this account to see what the chart should show
        all_transactions = transaction_manager.get_all_transactions()
        account_transactions = [
            t for t in all_transactions
            if (t.transaction_type == TransactionType.SAVING.value and
                ((hasattr(t, 'account_id') and t.account_id == default_savings.id) or
                 (hasattr(t, 'account_saved_to') and t.account_saved_to == default_savings.name)) and
                date(2025, 8, 1) <= t.date <= date(2025, 8, 14))
        ]

        print(f"\\nTransactions during test period ({len(account_transactions)}):")
        for tx in account_transactions:
            print(f"  - {tx.date}: +${tx.amount:.2f} - {tx.description}")

        # Calculate what the chart should show for this period
        period_start_balance = initial_balance
        period_changes = sum(tx.amount for tx in account_transactions)
        period_end_balance = period_start_balance + period_changes

        print(f"\\nExpected chart calculation for this bi-weekly period:")
        print(f"  Start: ${period_start_balance:.2f}")
        print(f"  Changes: +${period_changes:.2f}")
        print(f"  End: ${period_end_balance:.2f}")

        # Verify this matches the actual balance
        if abs(period_end_balance - final_balance) < 0.01:
            print(f"\\n[SUCCESS] Chart calculation should be accurate!")
        else:
            print(f"\\n[ISSUE] Expected ${period_end_balance:.2f}, actual ${final_balance:.2f}")

        print(f"\\nThis demonstrates the new chart logic:")
        print(f"  - Start with account balance at beginning of period")
        print(f"  - Add all saving transactions during the period")
        print(f"  - Result shows how account grew during that paycheck cycle")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up test data
        try:
            db.query(Transaction).filter(Transaction.week_number.in_([601, 602])).delete()
            db.query(Week).filter(Week.week_number.in_([601, 602])).delete()
            db.commit()
            print("\\nTest data cleaned up")
        except:
            pass

        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    test_complete_savings_chart()