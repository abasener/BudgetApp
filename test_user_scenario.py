"""
Test the user's specific scenario with corrected rollover timing
"""

from datetime import date, timedelta
from models import get_db, create_tables, drop_tables
from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor


def test_user_scenario():
    """Test user's scenario: correct numbers with proper rollover timing"""

    # Fresh database for testing
    drop_tables()
    create_tables()

    tm = TransactionManager()
    processor = PaycheckProcessor()

    print("=== User Scenario Test (Fixed Rollover Timing) ===")

    # Create Emergency Fund account
    emergency_fund = tm.add_account(
        name="Emergency Fund",
        goal_amount=5000.0,
        auto_save_amount=200.0,  # $200 auto-save per paycheck
        is_default_save=True,
        initial_balance=1000.0  # Starting with $1000
    )

    # Create Bill
    rent_bill = tm.add_bill(
        name="Rent",
        bill_type="Housing",
        payment_frequency="monthly",
        typical_amount=1200.0,
        amount_to_save=300.0,  # $300 per paycheck
        initial_balance=100.0
    )

    print(f"Emergency Fund starting balance: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Process paycheck with user's amounts
    today = date.today()
    paycheck_date = today - timedelta(days=1)  # Yesterday

    paycheck_amount = 3350.0
    bills_savings = 300.0  # Rent bill saving
    account_savings = 200.0  # Emergency fund auto-save
    total_savings = bills_savings + account_savings
    weekly_allocation = (paycheck_amount - total_savings) / 2  # Should be $1425 per week

    print(f"\nPaycheck breakdown:")
    print(f"  Gross paycheck: ${paycheck_amount}")
    print(f"  Bill savings: ${bills_savings}")
    print(f"  Account savings: ${account_savings}")
    print(f"  Total deducted for savings: ${total_savings}")
    print(f"  Remaining for weeks: ${paycheck_amount - total_savings}")
    print(f"  Per week allocation: ${weekly_allocation}")

    # Process the paycheck
    split = processor.process_new_paycheck(
        paycheck_amount=paycheck_amount,
        paycheck_date=paycheck_date,
        week_start_date=paycheck_date
    )

    print(f"\nAfter paycheck:")
    print(f"  Emergency Fund: ${emergency_fund.get_current_balance(tm.db):.2f}")
    print(f"  Rent Bill: ${rent_bill.get_current_balance(tm.db):.2f}")

    # Week 1 spending
    print(f"\n--- Week 1 Spending ---")
    week1_spending = 150.0
    tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 1,
        "amount": week1_spending,
        "date": paycheck_date + timedelta(days=1),
        "description": "Groceries",
        "category": "Food",
        "include_in_analytics": True
    })

    print(f"Week 1 spent: ${week1_spending}")
    print(f"Week 1 allocation: ${weekly_allocation}")
    print(f"Week 1 remaining: ${weekly_allocation - week1_spending}")

    # Check Week 2 status
    weeks = tm.get_all_weeks()
    week2_transactions = tm.get_transactions_by_week(2)

    week2_base = weekly_allocation
    week2_rollover = sum(
        t.amount for t in week2_transactions
        if t.transaction_type == "income" and ("rollover" in t.description.lower() or t.category == "Rollover")
    )
    week2_total = week2_base + week2_rollover

    print(f"\nWeek 2 status after Week 1 rollover:")
    print(f"  Week 2 base allocation: ${week2_base}")
    print(f"  Week 2 rollover income: ${week2_rollover}")
    print(f"  Week 2 total allocation: ${week2_total}")

    # Week 2 spending
    print(f"\n--- Week 2 Spending ---")
    week2_spending = 200.0
    tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 2,
        "amount": week2_spending,
        "date": paycheck_date + timedelta(days=8),
        "description": "Dining",
        "category": "Entertainment",
        "include_in_analytics": True
    })

    print(f"Week 2 spent: ${week2_spending}")
    print(f"Week 2 remaining (before rollover to savings): ${week2_total - week2_spending}")

    # Check balances before next paycheck
    print(f"\nBefore next paycheck:")
    print(f"  Emergency Fund: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Process next paycheck (triggers Week 2 rollover to savings)
    print(f"\n--- Next Paycheck (triggers Week 2 rollover) ---")
    next_paycheck_date = today + timedelta(days=14)  # Two weeks later

    split2 = processor.process_new_paycheck(
        paycheck_amount=paycheck_amount,
        paycheck_date=next_paycheck_date,
        week_start_date=next_paycheck_date
    )

    # Final balances
    print(f"\nAfter next paycheck:")
    print(f"  Emergency Fund: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Calculate expected vs actual
    expected_emergency = (
        1000.0 +  # Starting balance
        200.0 +   # First paycheck auto-save
        200.0 +   # Second paycheck auto-save
        (week2_total - week2_spending)  # Week 2 rollover
    )
    actual_emergency = emergency_fund.get_current_balance(tm.db)

    print(f"\n--- Final Verification ---")
    print(f"Expected Emergency Fund: ${expected_emergency:.2f}")
    print(f"  Starting: $1000.00")
    print(f"  Auto-save 1: $200.00")
    print(f"  Auto-save 2: $200.00")
    print(f"  Week 2 rollover: ${week2_total - week2_spending:.2f}")
    print(f"Actual Emergency Fund: ${actual_emergency:.2f}")
    print(f"Difference: ${actual_emergency - expected_emergency:.2f}")

    if abs(actual_emergency - expected_emergency) < 0.01:
        print("\n✓ SUCCESS: Numbers add up correctly!")
    else:
        print(f"\n✗ Issue: Expected ${expected_emergency:.2f}, got ${actual_emergency:.2f}")

    print("\n=== User Scenario Test Complete ===")

    processor.close()
    tm.close()


if __name__ == "__main__":
    test_user_scenario()