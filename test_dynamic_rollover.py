"""
Test the dynamic rollover recalculation system
"""

from datetime import date, timedelta
from models import get_db, create_tables, drop_tables
from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor


def test_dynamic_rollover():
    """Test that rollover recalculates when transactions are added"""

    # Fresh database for testing
    drop_tables()
    create_tables()

    tm = TransactionManager()
    processor = PaycheckProcessor()

    print("=== Dynamic Rollover Test ===")

    # User's exact setup
    emergency_fund = tm.add_account(
        name="Emergency Fund",
        goal_amount=5000.0,
        auto_save_amount=0.0,  # User wants auto-save = 0
        is_default_save=True,
        initial_balance=1000.0
    )

    rent_bill = tm.add_bill(
        name="Rent",
        bill_type="Housing",
        payment_frequency="monthly",
        typical_amount=1200.0,
        amount_to_save=300.0,  # User's bill sum
        initial_balance=100.0
    )

    print(f"Emergency fund start: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Process paycheck
    today = date.today()
    paycheck_date = today - timedelta(days=1)

    split = processor.process_new_paycheck(
        paycheck_amount=4625.0,
        paycheck_date=paycheck_date,
        week_start_date=paycheck_date
    )

    print(f"\nAfter paycheck - Emergency fund: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Check initial Week 2 allocation
    weeks = tm.get_all_weeks()
    week2_transactions = tm.get_transactions_by_week(2)
    week2_rollover = sum(
        t.amount for t in week2_transactions
        if t.transaction_type == "income" and ("rollover" in t.description.lower() or t.category == "Rollover")
    )
    initial_week2_total = split.week2_allocation + week2_rollover

    print(f"Initial Week 2 total allocation: ${initial_week2_total:.2f}")

    # Step 1: Add Week 1 spending (should trigger rollover recalculation)
    print(f"\n--- Step 1: Add Week 1 Spending ---")
    tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 1,
        "amount": 150.0,
        "date": paycheck_date + timedelta(days=1),
        "description": "Groceries",
        "category": "Food",
        "include_in_analytics": True
    })

    # Check Week 2 after rollover update
    week2_transactions_after = tm.get_transactions_by_week(2)
    week2_rollover_after = sum(
        t.amount for t in week2_transactions_after
        if t.transaction_type == "income" and ("rollover" in t.description.lower() or t.category == "Rollover")
    )
    updated_week2_total = split.week2_allocation + week2_rollover_after

    print(f"Week 2 total after Week 1 spending: ${updated_week2_total:.2f}")
    print(f"Week 2 rollover change: ${week2_rollover_after - week2_rollover:.2f}")

    # Step 2: Add more Week 1 spending (should update rollover again)
    print(f"\n--- Step 2: Add More Week 1 Spending ---")
    tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 1,
        "amount": 75.0,
        "date": paycheck_date + timedelta(days=2),
        "description": "Gas",
        "category": "Transportation",
        "include_in_analytics": True
    })

    # Check Week 2 after second update
    week2_transactions_final = tm.get_transactions_by_week(2)
    week2_rollover_final = sum(
        t.amount for t in week2_transactions_final
        if t.transaction_type == "income" and ("rollover" in t.description.lower() or t.category == "Rollover")
    )
    final_week2_total = split.week2_allocation + week2_rollover_final

    print(f"Week 2 total after more Week 1 spending: ${final_week2_total:.2f}")
    print(f"Week 2 rollover final: ${week2_rollover_final:.2f}")

    # Step 3: Add Week 2 spending (should update savings rollover)
    print(f"\n--- Step 3: Add Week 2 Spending ---")
    print(f"Emergency fund before Week 2 spending: ${emergency_fund.get_current_balance(tm.db):.2f}")

    tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 2,
        "amount": 200.0,
        "date": paycheck_date + timedelta(days=8),
        "description": "Dining",
        "category": "Entertainment",
        "include_in_analytics": True
    })

    print(f"Emergency fund after Week 2 spending: ${emergency_fund.get_current_balance(tm.db):.2f}")
    expected_week2_remaining = final_week2_total - 200.0
    print(f"Expected Week 2 remaining: ${expected_week2_remaining:.2f}")

    # Step 4: Process next paycheck to complete the period and check final rollover
    print(f"\n--- Step 4: Complete Period ---")
    next_paycheck_date = today + timedelta(days=14)
    processor.process_new_paycheck(
        paycheck_amount=4625.0,
        paycheck_date=next_paycheck_date,
        week_start_date=next_paycheck_date
    )

    final_emergency_balance = emergency_fund.get_current_balance(tm.db)
    emergency_change = final_emergency_balance - 1000.0

    print(f"Final emergency fund: ${final_emergency_balance:.2f}")
    print(f"Emergency fund change: ${emergency_change:.2f}")
    print(f"Expected change: ${expected_week2_remaining:.2f}")

    # Verify dynamic behavior worked
    print(f"\n--- Verification ---")
    print(f"Week 1 spending total: $225.00")
    print(f"Week 1 remaining: ${split.week1_allocation - 225:.2f}")
    print(f"Week 2 base + rollover: ${split.week2_allocation + (split.week1_allocation - 225):.2f}")
    print(f"Week 2 remaining: ${split.week2_allocation + (split.week1_allocation - 225) - 200:.2f}")

    success = abs(emergency_change - expected_week2_remaining) < 0.01
    print(f"Dynamic rollover test: {'PASS' if success else 'FAIL'}")

    print("\n=== Dynamic Rollover Test Complete ===")

    processor.close()
    tm.close()


if __name__ == "__main__":
    test_dynamic_rollover()