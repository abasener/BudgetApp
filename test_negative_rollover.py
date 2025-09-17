"""
Test script to verify negative rollover handling for overspending scenarios
"""

from datetime import date, timedelta
from services.paycheck_processor import PaycheckProcessor
from services.transaction_manager import TransactionManager
from models import get_db, Week, Transaction, TransactionType

def test_negative_rollover_week_to_week():
    """Test Week 1 overspend reducing Week 2"""

    print("Testing Negative Rollover: Week 1 overspend -> reduce Week 2")
    print("=" * 55)

    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        db = get_db()

        # Create Week 1 with deficit (overspend)
        week1 = Week(
            week_number=701,  # Odd = Week 1
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 7),
            running_total=300.0,  # Allocated $300
            rollover_applied=False
        )

        # Create Week 2 that should receive negative rollover
        week2 = Week(
            week_number=702,  # Even = Week 2
            start_date=date(2025, 9, 8),
            end_date=date(2025, 9, 14),
            running_total=300.0,  # Allocated $300
            rollover_applied=False
        )

        db.add(week1)
        db.add(week2)
        db.commit()

        # Add overspending to Week 1 (spend $450 out of $300 -> -$150 deficit)
        overspending = Transaction(
            transaction_type=TransactionType.SPENDING.value,
            week_number=week1.week_number,
            amount=450.0,
            date=date(2025, 9, 3),
            description="Week 1 overspending",
            category="Food",
            include_in_analytics=True
        )

        db.add(overspending)
        db.commit()

        print(f"Week 1: Allocated ${week1.running_total:.2f}, Spent ${overspending.amount:.2f}")
        print(f"Expected deficit: ${week1.running_total - overspending.amount:.2f}")
        print(f"Week 2 initial total: ${week2.running_total:.2f}")

        # Process rollover
        print(f"\nProcessing rollover...")
        paycheck_processor.check_and_process_rollovers()

        # Check Week 2's new total
        week2_after = transaction_manager.get_week_by_number(702)
        print(f"Week 2 total after rollover: ${week2_after.running_total:.2f}")
        print(f"Expected Week 2 total: ${300 - 150:.2f}")

        # Check for rollover transaction in Week 2
        all_transactions = transaction_manager.get_all_transactions()
        rollover_transactions = [
            t for t in all_transactions
            if t.week_number == 702 and "rollover from week 701" in t.description.lower()
        ]

        print(f"\nRollover transactions in Week 2: {len(rollover_transactions)}")
        for tx in rollover_transactions:
            print(f"  - Type: {tx.transaction_type}, Amount: ${tx.amount:.2f}")
            print(f"    Description: {tx.description}")

        if rollover_transactions:
            print("\n[SUCCESS] Negative rollover from Week 1 to Week 2 works!")
        else:
            print("\n[ISSUE] No rollover transaction found")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        try:
            db.query(Transaction).filter(Transaction.week_number.in_([701, 702])).delete()
            db.query(Week).filter(Week.week_number.in_([701, 702])).delete()
            db.commit()
            print("\nTest data cleaned up")
        except:
            pass

        transaction_manager.close()
        paycheck_processor.close()

def test_negative_rollover_week_to_savings():
    """Test Week 2 overspend reducing Savings"""

    print("\n\nTesting Negative Rollover: Week 2 overspend -> reduce Savings")
    print("=" * 55)

    transaction_manager = TransactionManager()
    paycheck_processor = PaycheckProcessor()

    try:
        db = get_db()

        # Get current savings balance
        default_savings = transaction_manager.get_default_savings_account()
        savings_before = default_savings.running_total
        print(f"Savings balance before test: ${savings_before:.2f}")

        # Create Week 2 with deficit (overspend) - make it old so it's considered complete
        week2 = Week(
            week_number=704,  # Even = Week 2 (should go to savings)
            start_date=date.today() - timedelta(days=14),  # Make it old enough
            end_date=date.today() - timedelta(days=8),     # Ended 8 days ago
            running_total=300.0,  # Allocated $300
            rollover_applied=False
        )

        db.add(week2)
        db.commit()

        # Add overspending to Week 2 (spend $500 out of $300 -> -$200 deficit)
        overspending = Transaction(
            transaction_type=TransactionType.SPENDING.value,
            week_number=week2.week_number,
            amount=500.0,
            date=week2.start_date + timedelta(days=2),  # During the week
            description="Week 2 overspending",
            category="Emergency",
            include_in_analytics=True
        )

        db.add(overspending)
        db.commit()

        print(f"Week 2: Allocated ${week2.running_total:.2f}, Spent ${overspending.amount:.2f}")
        print(f"Expected deficit: ${week2.running_total - overspending.amount:.2f}")

        # Process rollover
        print(f"\nProcessing rollover...")
        paycheck_processor.check_and_process_rollovers()

        # Force fresh connection to get updated balance
        transaction_manager.close()
        transaction_manager = TransactionManager()

        # Check savings balance - get fresh account object
        savings_account_after = transaction_manager.get_default_savings_account()
        savings_balance_after = savings_account_after.running_total
        print(f"Savings balance after rollover: ${savings_balance_after:.2f}")
        print(f"Expected savings change: ${-200:.2f}")
        print(f"Actual savings change: ${savings_balance_after - savings_before:.2f}")

        # Check for rollover transaction - look for both SAVING and SPENDING types
        all_transactions = transaction_manager.get_all_transactions()
        savings_transactions = [
            t for t in all_transactions
            if (t.week_number == 704 and
                hasattr(t, 'account_id') and t.account_id == default_savings.id and
                "end-of-period" in t.description.lower())
        ]

        print(f"\nSavings rollover transactions: {len(savings_transactions)}")
        for tx in savings_transactions:
            print(f"  - Type: {tx.transaction_type}, Amount: ${tx.amount:.2f}")
            print(f"    Description: {tx.description}")
            print(f"    Account ID: {getattr(tx, 'account_id', 'None')}")

        # Also check all transactions for week 704 to see what was created
        week_704_transactions = [t for t in all_transactions if t.week_number == 704]
        print(f"\nAll Week 704 transactions: {len(week_704_transactions)}")
        for tx in week_704_transactions:
            print(f"  - Type: {tx.transaction_type}, Amount: ${tx.amount:.2f}")
            print(f"    Description: {tx.description}")
            print(f"    Account ID: {getattr(tx, 'account_id', 'None')}")

        # Manual calculation: Sum all SAVING transactions for this account
        all_transactions = transaction_manager.get_all_transactions()
        savings_account_transactions = [
            t for t in all_transactions
            if (t.transaction_type == TransactionType.SAVING.value and
                hasattr(t, 'account_id') and t.account_id == default_savings.id)
        ]

        calculated_balance = sum(tx.amount for tx in savings_account_transactions)
        print(f"\nManual calculation:")
        print(f"  Total saving transactions: {len(savings_account_transactions)}")
        print(f"  Sum of all saving amounts: ${calculated_balance:.2f}")
        print(f"  Database stored balance: ${savings_balance_after:.2f}")

        if abs((savings_balance_after - savings_before) - (-200)) < 0.01:
            print("\n[SUCCESS] Negative rollover from Week 2 to Savings works!")
        else:
            print("\n[ISSUE] Savings balance change doesn't match expected deficit")

            # Check if the calculated balance matches what we expect
            expected_calculated = savings_before + (-200)
            if abs(calculated_balance - expected_calculated) < 0.01:
                print(f"[INFO] Transaction sum is correct (${calculated_balance:.2f}), but stored balance is wrong")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        try:
            db.query(Transaction).filter(Transaction.week_number == 704).delete()
            db.query(Week).filter(Week.week_number == 704).delete()
            db.commit()
            print("\nTest data cleaned up")
        except:
            pass

        transaction_manager.close()
        paycheck_processor.close()

if __name__ == "__main__":
    test_negative_rollover_week_to_week()
    test_negative_rollover_week_to_savings()