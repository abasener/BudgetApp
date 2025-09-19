"""
Test the updated PaycheckProcessor with the new AccountHistory system
"""

from datetime import date
from models import get_db, create_tables, drop_tables
from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor


def test_updated_paycheck_processor():
    """Test PaycheckProcessor with automatic AccountHistory integration"""

    # Fresh database for testing
    drop_tables()
    create_tables()

    tm = TransactionManager()
    processor = PaycheckProcessor()

    print("=== Testing Updated PaycheckProcessor ===")

    # Test 1: Set up accounts and bills
    print("\n1. Setting up accounts and bills...")

    # Add default savings account
    emergency_fund = tm.add_account(
        name="Emergency Fund",
        goal_amount=5000.0,
        auto_save_amount=150.0,  # Auto-save $150 per paycheck
        is_default_save=True,
        initial_balance=1000.0
    )
    print(f"   Created emergency fund: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Add another savings account
    vacation_fund = tm.add_account(
        name="Vacation Fund",
        goal_amount=2000.0,
        auto_save_amount=50.0,  # Auto-save $50 per paycheck
        is_default_save=False,
        initial_balance=300.0
    )
    print(f"   Created vacation fund: ${vacation_fund.get_current_balance(tm.db):.2f}")

    # Add bills
    rent_bill = tm.add_bill(
        name="Rent",
        bill_type="Housing",
        payment_frequency="monthly",
        typical_amount=1200.0,
        amount_to_save=300.0,  # Save $300 per paycheck
        initial_balance=200.0
    )
    print(f"   Created rent bill: ${rent_bill.get_current_balance(tm.db):.2f}")

    utilities_bill = tm.add_bill(
        name="Utilities",
        bill_type="Housing",
        payment_frequency="monthly",
        typical_amount=150.0,
        amount_to_save=75.0,  # Save $75 per paycheck
        initial_balance=50.0
    )
    print(f"   Created utilities bill: ${utilities_bill.get_current_balance(tm.db):.2f}")

    # Test 2: Process a paycheck
    print("\n2. Processing a bi-weekly paycheck...")

    paycheck_amount = 2000.0
    paycheck_date = date(2024, 1, 15)
    week_start_date = date(2024, 1, 15)

    print(f"   Gross paycheck: ${paycheck_amount:.2f}")

    # Calculate what should be deducted
    expected_bills_deduction = 300.0 + 75.0  # Rent + Utilities
    expected_account_auto_savings = 150.0 + 50.0  # Emergency + Vacation
    expected_remaining = paycheck_amount - expected_bills_deduction - expected_account_auto_savings
    expected_week_allocation = expected_remaining / 2

    print(f"   Expected bills deduction: ${expected_bills_deduction:.2f}")
    print(f"   Expected account auto-savings: ${expected_account_auto_savings:.2f}")
    print(f"   Expected remaining for weeks: ${expected_remaining:.2f}")
    print(f"   Expected per-week allocation: ${expected_week_allocation:.2f}")

    # Process the paycheck
    paycheck_split = processor.process_new_paycheck(
        paycheck_amount=paycheck_amount,
        paycheck_date=paycheck_date,
        week_start_date=week_start_date
    )

    print(f"   Actual paycheck split: {paycheck_split}")

    # Test 3: Check account balances after paycheck processing
    print("\n3. Checking account balances after paycheck processing...")

    emergency_balance = emergency_fund.get_current_balance(tm.db)
    vacation_balance = vacation_fund.get_current_balance(tm.db)
    rent_balance = rent_bill.get_current_balance(tm.db)
    utilities_balance = utilities_bill.get_current_balance(tm.db)

    print(f"   Emergency fund: ${emergency_balance:.2f} (expected: ${1000 + 150:.2f})")
    print(f"   Vacation fund: ${vacation_balance:.2f} (expected: ${300 + 50:.2f})")
    print(f"   Rent bill: ${rent_balance:.2f} (expected: ${200 + 300:.2f})")
    print(f"   Utilities bill: ${utilities_balance:.2f} (expected: ${50 + 75:.2f})")

    # Verify balances are correct
    assert abs(emergency_balance - 1150.0) < 0.01, f"Emergency fund expected 1150, got {emergency_balance}"
    assert abs(vacation_balance - 350.0) < 0.01, f"Vacation fund expected 350, got {vacation_balance}"
    assert abs(rent_balance - 500.0) < 0.01, f"Rent bill expected 500, got {rent_balance}"
    assert abs(utilities_balance - 125.0) < 0.01, f"Utilities bill expected 125, got {utilities_balance}"

    # Test 4: Check weeks were created properly
    print("\n4. Checking created weeks...")

    weeks = tm.get_all_weeks()
    print(f"   Created {len(weeks)} weeks")

    for week in weeks:
        print(f"   Week {week.week_number}: ${week.running_total:.2f} ({week.start_date} to {week.end_date})")

    # Should have 2 weeks with expected allocations
    assert len(weeks) == 2, f"Expected 2 weeks, got {len(weeks)}"
    for week in weeks:
        assert abs(week.running_total - expected_week_allocation) < 0.01

    # Test 5: Check transaction history
    print("\n5. Checking account transaction histories...")

    print("   Emergency Fund history:")
    emergency_history = emergency_fund.get_account_history(tm.db)
    for i, entry in enumerate(emergency_history):
        print(f"     {i+1}. {entry}")

    print("   Rent Bill history:")
    rent_history = rent_bill.get_account_history(tm.db)
    for i, entry in enumerate(rent_history):
        print(f"     {i+1}. {entry}")

    # Each account should have 2 entries: starting balance + auto-save transaction
    assert len(emergency_history) == 2, f"Expected 2 emergency history entries, got {len(emergency_history)}"
    assert len(rent_history) == 2, f"Expected 2 rent history entries, got {len(rent_history)}"

    # Test 6: Test bill payment to verify negative transactions work
    print("\n6. Testing bill payment...")

    print(f"   Rent balance before payment: ${rent_bill.get_current_balance(tm.db):.2f}")

    # Pay rent
    rent_payment_data = {
        "transaction_type": "bill_pay",
        "week_number": 1,
        "amount": 1200.0,
        "date": date(2024, 1, 30),
        "description": "January rent payment",
        "bill_id": rent_bill.id,
        "bill_type": "Housing"
    }
    payment_tx = tm.add_transaction(rent_payment_data)
    print(f"   Payment transaction: {payment_tx}")

    rent_balance_after = rent_bill.get_current_balance(tm.db)
    print(f"   Rent balance after payment: ${rent_balance_after:.2f}")

    # Expected: 500 - 1200 = -700 (overpaid)
    expected_after_payment = 500.0 - 1200.0
    assert abs(rent_balance_after - expected_after_payment) < 0.01

    print("\n=== All PaycheckProcessor Tests Passed! ===")

    processor.close()
    tm.close()


if __name__ == "__main__":
    test_updated_paycheck_processor()