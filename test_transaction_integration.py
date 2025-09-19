"""
Test integration between the unified Transaction model and AccountHistory
"""

from datetime import date
from models import get_db, create_tables, drop_tables, Transaction, TransactionType, AccountHistory, AccountHistoryManager


def test_transaction_integration():
    """Test that transactions and account history work together"""

    # Fresh database for testing
    drop_tables()
    create_tables()

    db = get_db()
    history_manager = AccountHistoryManager(db)

    print("=== Testing Transaction + AccountHistory Integration ===")

    # Test 1: Create a savings account and initialize history
    print("\n1. Setting up savings account...")
    history_manager.initialize_account_history(
        account_id=1,
        account_type="savings",
        starting_balance=500.0,
        start_date=date(2024, 1, 1)
    )
    db.commit()

    # Test 2: Create a savings transaction and link it to history
    print("\n2. Creating savings transaction...")
    savings_tx = Transaction(
        transaction_type=TransactionType.SAVING.value,
        week_number=1,
        amount=100.0,
        date=date(2024, 1, 15),
        description="Paycheck auto-save",
        account_id=1,
        account_saved_to="Emergency Fund"
    )
    db.add(savings_tx)
    db.flush()  # Get the transaction ID

    # Add corresponding history entry
    history_entry = history_manager.add_transaction_change(
        account_id=1,
        account_type="savings",
        transaction_id=savings_tx.id,
        change_amount=savings_tx.get_change_amount_for_account(),
        transaction_date=savings_tx.date
    )
    db.commit()

    print(f"   Created transaction: {savings_tx}")
    print(f"   Created history entry: {history_entry}")
    print(f"   Transaction affects account: {savings_tx.affects_account}")
    print(f"   Account type: {savings_tx.account_type}")
    print(f"   Change amount: ${savings_tx.get_change_amount_for_account():.2f}")

    # Test 3: Create a bill account and test bill saving transaction
    print("\n3. Setting up bill account...")
    history_manager.initialize_account_history(
        account_id=1,
        account_type="bill",
        starting_balance=0.0,
        start_date=date(2024, 1, 1)
    )
    db.commit()

    print("\n4. Creating bill savings transaction...")
    bill_savings_tx = Transaction(
        transaction_type=TransactionType.SAVING.value,
        week_number=1,
        amount=300.0,
        date=date(2024, 1, 15),
        description="Rent savings from paycheck",
        bill_id=1,
        bill_type="Housing"
    )
    db.add(bill_savings_tx)
    db.flush()

    # Add corresponding history entry
    bill_history_entry = history_manager.add_transaction_change(
        account_id=1,
        account_type="bill",
        transaction_id=bill_savings_tx.id,
        change_amount=bill_savings_tx.get_change_amount_for_account(),
        transaction_date=bill_savings_tx.date
    )
    db.commit()

    print(f"   Created bill transaction: {bill_savings_tx}")
    print(f"   Created bill history entry: {bill_history_entry}")

    # Test 4: Create a bill payment transaction
    print("\n5. Creating bill payment transaction...")
    bill_payment_tx = Transaction(
        transaction_type=TransactionType.BILL_PAY.value,
        week_number=2,
        amount=250.0,  # Paying $250 rent
        date=date(2024, 1, 30),
        description="Rent payment",
        bill_id=1,
        bill_type="Housing"
    )
    db.add(bill_payment_tx)
    db.flush()

    # Add corresponding history entry (negative change because money is leaving the bill account)
    payment_history_entry = history_manager.add_transaction_change(
        account_id=1,
        account_type="bill",
        transaction_id=bill_payment_tx.id,
        change_amount=bill_payment_tx.get_change_amount_for_account(),
        transaction_date=bill_payment_tx.date
    )
    db.commit()

    print(f"   Created payment transaction: {bill_payment_tx}")
    print(f"   Created payment history entry: {payment_history_entry}")
    print(f"   Change amount for bill payment: ${bill_payment_tx.get_change_amount_for_account():.2f}")

    # Test 5: Create a spending transaction (no account impact)
    print("\n6. Creating spending transaction...")
    spending_tx = Transaction(
        transaction_type=TransactionType.SPENDING.value,
        week_number=2,
        amount=45.0,
        date=date(2024, 1, 25),
        description="Grocery shopping",
        category="Food",
        include_in_analytics=True
    )
    db.add(spending_tx)
    db.commit()

    print(f"   Created spending transaction: {spending_tx}")
    print(f"   Affects account: {spending_tx.affects_account}")
    print(f"   Change amount: ${spending_tx.get_change_amount_for_account():.2f}")

    # Test 6: Check final account balances
    print("\n7. Final account balances:")
    savings_balance = history_manager.get_current_balance(1, "savings")
    bill_balance = history_manager.get_current_balance(1, "bill")
    print(f"   Savings account balance: ${savings_balance:.2f}")
    print(f"   Bill account balance: ${bill_balance:.2f}")

    # Expected: Savings = 500 + 100 = 600, Bill = 0 + 300 - 250 = 50
    assert savings_balance == 600.0, f"Expected 600.0, got {savings_balance}"
    assert bill_balance == 50.0, f"Expected 50.0, got {bill_balance}"

    # Test 7: Test relationship navigation
    print("\n8. Testing relationship navigation...")

    # Get transaction and navigate to its history entries
    saved_tx = db.query(Transaction).filter(Transaction.id == savings_tx.id).first()
    print(f"   Transaction: {saved_tx}")
    print(f"   History entries for this transaction: {len(saved_tx.history_entries)}")
    for entry in saved_tx.history_entries:
        print(f"     - {entry}")

    # Get history entry and navigate to its transaction
    saved_history = db.query(AccountHistory).filter(AccountHistory.transaction_id == savings_tx.id).first()
    print(f"   History entry: {saved_history}")
    print(f"   Related transaction: {saved_history.transaction}")

    print("\n=== All Integration Tests Passed! ===")
    db.close()


if __name__ == "__main__":
    test_transaction_integration()