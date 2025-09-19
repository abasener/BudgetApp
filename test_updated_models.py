"""
Test the updated Bills and Account models with AccountHistory integration
"""

from datetime import date
from models import get_db, create_tables, drop_tables, Bill, Account, Transaction, TransactionType


def test_updated_models():
    """Test that both Bills and Accounts work with the new AccountHistory system"""

    # Fresh database for testing
    drop_tables()
    create_tables()

    db = get_db()

    print("=== Testing Updated Bills and Account Models ===")

    # Test 1: Create and initialize a Bill
    print("\n1. Creating and testing Bill model...")
    rent_bill = Bill(
        name="Rent",
        bill_type="Housing",
        payment_frequency="monthly",
        typical_amount=1200.0,
        amount_to_save=300.0,  # Save $300 bi-weekly
        is_variable=False,
        notes="Monthly rent payment"
    )
    db.add(rent_bill)
    db.commit()
    db.refresh(rent_bill)

    # Initialize history for the bill
    rent_bill.initialize_history(db, starting_balance=0.0, start_date=date(2024, 1, 1))
    db.commit()

    print(f"   Created bill: {rent_bill}")
    print(f"   Initial balance: ${rent_bill.get_current_balance(db):.2f}")
    print(f"   Savings progress: {rent_bill.savings_progress_percent:.1f}%")
    print(f"   Fully funded: {rent_bill.is_fully_funded}")

    # Test 2: Add money to the bill via a transaction
    print("\n2. Adding money to bill via transaction...")
    bill_savings_tx = Transaction(
        transaction_type=TransactionType.SAVING.value,
        week_number=1,
        amount=300.0,
        date=date(2024, 1, 15),
        description="Bi-weekly rent savings",
        bill_id=rent_bill.id,
        bill_type="Housing"
    )
    db.add(bill_savings_tx)
    db.flush()

    # Add to history
    from models.account_history import AccountHistoryManager
    history_manager = AccountHistoryManager(db)
    history_manager.add_transaction_change(
        account_id=rent_bill.id,
        account_type="bill",
        transaction_id=bill_savings_tx.id,
        change_amount=bill_savings_tx.get_change_amount_for_account(),
        transaction_date=bill_savings_tx.date
    )
    db.commit()

    print(f"   Bill after savings: {rent_bill}")
    print(f"   Balance: ${rent_bill.get_current_balance(db):.2f}")
    print(f"   Savings progress: {rent_bill.savings_progress_percent:.1f}%")
    print(f"   Savings needed: ${rent_bill.savings_needed:.2f}")

    # Test 3: Create and initialize a Savings Account
    print("\n3. Creating and testing Account model...")
    emergency_fund = Account(
        name="Emergency Fund",
        goal_amount=5000.0,
        auto_save_amount=200.0,
        is_default_save=True
    )
    db.add(emergency_fund)
    db.commit()
    db.refresh(emergency_fund)

    # Initialize history for the account
    emergency_fund.initialize_history(db, starting_balance=1000.0, start_date=date(2024, 1, 1))
    db.commit()

    print(f"   Created account: {emergency_fund}")
    print(f"   Initial balance: ${emergency_fund.get_current_balance(db):.2f}")
    print(f"   Goal progress: {emergency_fund.goal_progress_percent:.1f}%")
    print(f"   Goal remaining: ${emergency_fund.goal_remaining:.2f}")
    print(f"   Goal reached: {emergency_fund.is_goal_reached}")

    # Test 4: Add money to the savings account via a transaction
    print("\n4. Adding money to savings account via transaction...")
    savings_tx = Transaction(
        transaction_type=TransactionType.SAVING.value,
        week_number=1,
        amount=500.0,
        date=date(2024, 1, 15),
        description="Paycheck auto-save to emergency fund",
        account_id=emergency_fund.id,
        account_saved_to="Emergency Fund"
    )
    db.add(savings_tx)
    db.flush()

    # Add to history
    history_manager.add_transaction_change(
        account_id=emergency_fund.id,
        account_type="savings",
        transaction_id=savings_tx.id,
        change_amount=savings_tx.get_change_amount_for_account(),
        transaction_date=savings_tx.date
    )
    db.commit()

    print(f"   Account after savings: {emergency_fund}")
    print(f"   Balance: ${emergency_fund.get_current_balance(db):.2f}")
    print(f"   Goal progress: {emergency_fund.goal_progress_percent:.1f}%")
    print(f"   Goal remaining: ${emergency_fund.goal_remaining:.2f}")

    # Test 5: Test backward compatibility properties
    print("\n5. Testing backward compatibility...")
    print(f"   Bill running_total property: ${rent_bill.running_total:.2f}")
    print(f"   Account running_total property: ${emergency_fund.running_total:.2f}")

    # Test setting running_total (should be ignored)
    old_bill_balance = rent_bill.running_total
    old_account_balance = emergency_fund.running_total

    rent_bill.running_total = 9999.99
    emergency_fund.running_total = 8888.88

    print(f"   After setting running_total to 9999.99 and 8888.88:")
    print(f"   Bill balance (should be unchanged): ${rent_bill.running_total:.2f}")
    print(f"   Account balance (should be unchanged): ${emergency_fund.running_total:.2f}")

    assert rent_bill.running_total == old_bill_balance
    assert emergency_fund.running_total == old_account_balance

    # Test 6: Test account history viewing
    print("\n6. Testing account history retrieval...")
    bill_history = rent_bill.get_account_history(db)
    account_history = emergency_fund.get_account_history(db)

    print(f"   Bill history entries: {len(bill_history)}")
    for i, entry in enumerate(bill_history):
        print(f"     {i+1}. {entry}")

    print(f"   Account history entries: {len(account_history)}")
    for i, entry in enumerate(account_history):
        print(f"     {i+1}. {entry}")

    # Test 7: Create a second savings account to test non-default
    print("\n7. Testing multiple accounts...")
    vacation_fund = Account(
        name="Vacation Fund",
        goal_amount=2000.0,
        auto_save_amount=50.0,
        is_default_save=False
    )
    db.add(vacation_fund)
    db.commit()
    db.refresh(vacation_fund)

    vacation_fund.initialize_history(db, starting_balance=500.0)
    db.commit()

    print(f"   Created second account: {vacation_fund}")
    print(f"   Is default save: {vacation_fund.is_default_save}")
    print(f"   Emergency fund is default: {emergency_fund.is_default_save}")

    print("\n=== All Model Tests Passed! ===")
    db.close()


if __name__ == "__main__":
    test_updated_models()