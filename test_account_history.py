"""
Test script for the new AccountHistory system
"""

from datetime import date, datetime
from models import get_db, create_tables, drop_tables, AccountHistory, AccountHistoryManager


def test_account_history_basic():
    """Test basic account history functionality"""

    # Fresh database for testing
    drop_tables()
    create_tables()

    db = get_db()
    history_manager = AccountHistoryManager(db)

    print("=== Testing AccountHistory Basic Functionality ===")

    # Test 1: Initialize account with starting balance
    print("\n1. Creating starting balance for Savings Account 1...")
    starting_entry = history_manager.initialize_account_history(
        account_id=1,
        account_type="savings",
        starting_balance=100.0,
        start_date=date(2024, 1, 1)
    )
    db.commit()

    print(f"   Created: {starting_entry}")
    current_balance = history_manager.get_current_balance(1, "savings")
    print(f"   Current balance: ${current_balance:.2f}")
    assert current_balance == 100.0, f"Expected 100.0, got {current_balance}"

    # Test 2: Add transaction changes
    print("\n2. Adding transaction changes...")

    # Add $50 deposit (transaction ID 1)
    deposit_entry = history_manager.add_transaction_change(
        account_id=1,
        account_type="savings",
        transaction_id=1,
        change_amount=50.0,
        transaction_date=date(2024, 1, 15)
    )
    db.commit()

    print(f"   Added deposit: {deposit_entry}")
    current_balance = history_manager.get_current_balance(1, "savings")
    print(f"   Current balance after deposit: ${current_balance:.2f}")
    assert current_balance == 150.0, f"Expected 150.0, got {current_balance}"

    # Add $25 withdrawal (transaction ID 2)
    withdrawal_entry = history_manager.add_transaction_change(
        account_id=1,
        account_type="savings",
        transaction_id=2,
        change_amount=-25.0,
        transaction_date=date(2024, 1, 20)
    )
    db.commit()

    print(f"   Added withdrawal: {withdrawal_entry}")
    current_balance = history_manager.get_current_balance(1, "savings")
    print(f"   Current balance after withdrawal: ${current_balance:.2f}")
    assert current_balance == 125.0, f"Expected 125.0, got {current_balance}"

    # Test 3: View complete history
    print("\n3. Complete account history:")
    history = history_manager.get_account_history(1, "savings")
    for i, entry in enumerate(history):
        print(f"   {i+1}. {entry}")

    assert len(history) == 3, f"Expected 3 entries, got {len(history)}"

    # Test 4: Update a transaction
    print("\n4. Testing transaction update...")
    print(f"   Before update - balance: ${current_balance:.2f}")

    # Change the deposit from $50 to $75 (difference of +$25)
    history_manager.update_transaction_change(
        transaction_id=1,
        new_change_amount=75.0,
        new_date=date(2024, 1, 15)
    )
    db.commit()

    current_balance = history_manager.get_current_balance(1, "savings")
    print(f"   After update - balance: ${current_balance:.2f}")
    assert current_balance == 150.0, f"Expected 150.0 (100 + 75 - 25), got {current_balance}"

    print("\n4a. History after update:")
    history = history_manager.get_account_history(1, "savings")
    for i, entry in enumerate(history):
        print(f"   {i+1}. {entry}")

    # Test 5: Test with a Bill account
    print("\n5. Testing with Bill account...")

    # Initialize bill account
    bill_entry = history_manager.initialize_account_history(
        account_id=1,
        account_type="bill",
        starting_balance=0.0,
        start_date=date(2024, 1, 1)
    )
    db.commit()

    # Add some bill savings
    history_manager.add_transaction_change(
        account_id=1,
        account_type="bill",
        transaction_id=3,
        change_amount=200.0,  # Money saved for rent
        transaction_date=date(2024, 1, 10)
    )
    db.commit()

    bill_balance = history_manager.get_current_balance(1, "bill")
    print(f"   Bill account balance: ${bill_balance:.2f}")
    assert bill_balance == 200.0, f"Expected 200.0, got {bill_balance}"

    # Test 6: Delete a transaction
    print("\n6. Testing transaction deletion...")
    print(f"   Savings balance before deletion: ${history_manager.get_current_balance(1, 'savings'):.2f}")

    # Delete the withdrawal transaction (ID 2, -$25)
    history_manager.delete_transaction_change(transaction_id=2)
    db.commit()

    final_balance = history_manager.get_current_balance(1, "savings")
    print(f"   Savings balance after deletion: ${final_balance:.2f}")
    assert final_balance == 175.0, f"Expected 175.0 (100 + 75), got {final_balance}"

    print("\n6a. Final history after deletion:")
    history = history_manager.get_account_history(1, "savings")
    for i, entry in enumerate(history):
        print(f"   {i+1}. {entry}")

    print("\n=== All Tests Passed! ===")
    db.close()


if __name__ == "__main__":
    test_account_history_basic()