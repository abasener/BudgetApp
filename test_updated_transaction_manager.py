"""
Test the updated TransactionManager with automatic AccountHistory integration
"""

from datetime import date
from models import get_db, create_tables, drop_tables, TransactionType
from services.transaction_manager import TransactionManager


def test_updated_transaction_manager():
    """Test TransactionManager with automatic AccountHistory integration"""

    # Fresh database for testing
    drop_tables()
    create_tables()

    tm = TransactionManager()

    print("=== Testing Updated TransactionManager ===")

    # Test 1: Add accounts and bills with automatic history initialization
    print("\n1. Adding accounts and bills...")

    # Add savings account
    emergency_fund = tm.add_account(
        name="Emergency Fund",
        goal_amount=5000.0,
        auto_save_amount=200.0,
        is_default_save=True,
        initial_balance=1000.0
    )
    print(f"   Created account: {emergency_fund}")
    print(f"   Initial balance: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Add bill
    rent_bill = tm.add_bill(
        name="Rent",
        bill_type="Housing",
        payment_frequency="monthly",
        typical_amount=1200.0,
        amount_to_save=300.0,
        initial_balance=100.0
    )
    print(f"   Created bill: {rent_bill}")
    print(f"   Initial balance: ${rent_bill.get_current_balance(tm.db):.2f}")

    # Test 2: Add transactions that automatically create history entries
    print("\n2. Adding transactions with automatic history tracking...")

    # Savings transaction
    savings_tx_data = {
        "transaction_type": TransactionType.SAVING.value,
        "week_number": 1,
        "amount": 300.0,
        "date": date(2024, 1, 15),
        "description": "Emergency fund deposit",
        "account_id": emergency_fund.id,
        "account_saved_to": "Emergency Fund"
    }
    savings_tx = tm.add_transaction(savings_tx_data)
    print(f"   Added savings transaction: {savings_tx}")
    print(f"   Emergency fund balance: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Bill savings transaction
    bill_savings_tx_data = {
        "transaction_type": TransactionType.SAVING.value,
        "week_number": 1,
        "amount": 250.0,
        "date": date(2024, 1, 15),
        "description": "Rent savings",
        "bill_id": rent_bill.id,
        "bill_type": "Housing"
    }
    bill_savings_tx = tm.add_transaction(bill_savings_tx_data)
    print(f"   Added bill savings transaction: {bill_savings_tx}")
    print(f"   Rent bill balance: ${rent_bill.get_current_balance(tm.db):.2f}")

    # Spending transaction (no account impact)
    spending_tx_data = {
        "transaction_type": TransactionType.SPENDING.value,
        "week_number": 1,
        "amount": 45.0,
        "date": date(2024, 1, 16),
        "description": "Groceries",
        "category": "Food",
        "include_in_analytics": True
    }
    spending_tx = tm.add_transaction(spending_tx_data)
    print(f"   Added spending transaction: {spending_tx}")

    # Bill payment transaction
    bill_payment_tx_data = {
        "transaction_type": TransactionType.BILL_PAY.value,
        "week_number": 2,
        "amount": 200.0,
        "date": date(2024, 1, 30),
        "description": "Partial rent payment",
        "bill_id": rent_bill.id,
        "bill_type": "Housing"
    }
    bill_payment_tx = tm.add_transaction(bill_payment_tx_data)
    print(f"   Added bill payment transaction: {bill_payment_tx}")
    print(f"   Rent bill balance after payment: ${rent_bill.get_current_balance(tm.db):.2f}")

    # Test 3: Update a transaction and verify history changes
    print("\n3. Testing transaction updates...")
    print(f"   Emergency fund balance before update: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Change the savings amount from $300 to $500
    updated_tx = tm.update_transaction(savings_tx.id, {"amount": 500.0})
    print(f"   Updated transaction: {updated_tx}")
    print(f"   Emergency fund balance after update: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Expected: 1000 + 500 = 1500
    expected_balance = 1500.0
    actual_balance = emergency_fund.get_current_balance(tm.db)
    assert abs(actual_balance - expected_balance) < 0.01, f"Expected {expected_balance}, got {actual_balance}"

    # Test 4: Change transaction account association
    print("\n4. Testing account association changes...")

    # Create a second savings account
    vacation_fund = tm.add_account(
        name="Vacation Fund",
        goal_amount=2000.0,
        auto_save_amount=50.0,
        is_default_save=False,
        initial_balance=500.0
    )

    print(f"   Created vacation fund: ${vacation_fund.get_current_balance(tm.db):.2f}")
    print(f"   Emergency fund before reassignment: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Move the savings transaction from emergency fund to vacation fund
    tm.update_transaction(savings_tx.id, {"account_id": vacation_fund.id, "account_saved_to": "Vacation Fund"})

    print(f"   Emergency fund after reassignment: ${emergency_fund.get_current_balance(tm.db):.2f}")
    print(f"   Vacation fund after reassignment: ${vacation_fund.get_current_balance(tm.db):.2f}")

    # Expected: Emergency = 1000, Vacation = 500 + 500 = 1000
    assert abs(emergency_fund.get_current_balance(tm.db) - 1000.0) < 0.01
    assert abs(vacation_fund.get_current_balance(tm.db) - 1000.0) < 0.01

    # Test 5: Delete a transaction and verify history cleanup
    print("\n5. Testing transaction deletion...")
    print(f"   Vacation fund before deletion: ${vacation_fund.get_current_balance(tm.db):.2f}")

    success = tm.delete_transaction(savings_tx.id)
    print(f"   Transaction deleted: {success}")
    print(f"   Vacation fund after deletion: ${vacation_fund.get_current_balance(tm.db):.2f}")

    # Expected: Vacation fund back to 500
    assert abs(vacation_fund.get_current_balance(tm.db) - 500.0) < 0.01

    # Test 6: View account histories
    print("\n6. Checking account histories...")

    emergency_history = emergency_fund.get_account_history(tm.db)
    print(f"   Emergency fund history ({len(emergency_history)} entries):")
    for i, entry in enumerate(emergency_history):
        print(f"     {i+1}. {entry}")

    vacation_history = vacation_fund.get_account_history(tm.db)
    print(f"   Vacation fund history ({len(vacation_history)} entries):")
    for i, entry in enumerate(vacation_history):
        print(f"     {i+1}. {entry}")

    rent_history = rent_bill.get_account_history(tm.db)
    print(f"   Rent bill history ({len(rent_history)} entries):")
    for i, entry in enumerate(rent_history):
        print(f"     {i+1}. {entry}")

    # Test 7: Verify final balances
    print("\n7. Final balance verification:")
    print(f"   Emergency Fund: ${emergency_fund.get_current_balance(tm.db):.2f}")
    print(f"   Vacation Fund: ${vacation_fund.get_current_balance(tm.db):.2f}")
    print(f"   Rent Bill: ${rent_bill.get_current_balance(tm.db):.2f}")

    # Expected final balances:
    # Emergency: 1000 (starting balance only)
    # Vacation: 500 (starting balance only, savings tx was deleted)
    # Rent: 100 + 250 - 200 = 150
    assert abs(emergency_fund.get_current_balance(tm.db) - 1000.0) < 0.01
    assert abs(vacation_fund.get_current_balance(tm.db) - 500.0) < 0.01
    assert abs(rent_bill.get_current_balance(tm.db) - 150.0) < 0.01

    print("\n=== All TransactionManager Tests Passed! ===")
    tm.close()


if __name__ == "__main__":
    test_updated_transaction_manager()