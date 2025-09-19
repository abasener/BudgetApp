"""
Test a complete bi-weekly cycle to verify rollover happens at the right time
"""

from datetime import date, timedelta
from models import get_db, create_tables, drop_tables
from services.transaction_manager import TransactionManager
from services.paycheck_processor import PaycheckProcessor


def test_complete_biweekly_cycle():
    """Test complete bi-weekly cycle with proper timing"""

    # Fresh database for testing
    drop_tables()
    create_tables()

    tm = TransactionManager()
    processor = PaycheckProcessor()

    print("=== Complete Bi-weekly Cycle Test ===")

    # Step 1: Create accounts
    emergency_fund = tm.add_account(
        name="Emergency Fund",
        goal_amount=5000.0,
        auto_save_amount=200.0,
        is_default_save=True,
        initial_balance=1000.0
    )

    # Step 2: First paycheck (creates Week 1 & 2)
    print("\n--- First Paycheck ---")
    today = date.today()
    paycheck1_date = today - timedelta(days=10)  # 10 days ago

    paycheck_split = processor.process_new_paycheck(
        paycheck_amount=3000.0,
        paycheck_date=paycheck1_date,
        week_start_date=paycheck1_date
    )

    print(f"Emergency fund after first paycheck: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Step 3: Add spending to Week 1
    print("\n--- Add spending to Week 1 ---")
    tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 1,
        "amount": 150.0,
        "date": paycheck1_date + timedelta(days=2),
        "description": "Groceries",
        "category": "Food",
        "include_in_analytics": True
    })

    print(f"Emergency fund after Week 1 spending: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Step 4: Add spending to Week 2
    print("\n--- Add spending to Week 2 ---")
    tm.add_transaction({
        "transaction_type": "spending",
        "week_number": 2,
        "amount": 200.0,
        "date": paycheck1_date + timedelta(days=9),
        "description": "Dining",
        "category": "Entertainment",
        "include_in_analytics": True
    })

    print(f"Emergency fund after Week 2 spending: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Step 5: Check Week 2 effective allocation before second paycheck
    print("\n--- Week 2 Status Before Second Paycheck ---")
    week2_transactions = tm.get_transactions_by_week(2)

    week2_base = 1175.0  # Expected from paycheck split
    week2_rollover_income = sum(
        t.amount for t in week2_transactions
        if t.transaction_type == "income" and ("rollover" in t.description.lower() or t.category == "Rollover")
    )
    week2_spending = sum(
        t.amount for t in week2_transactions
        if t.transaction_type in ["spending", "bill_pay"]
    )

    week2_total_allocation = week2_base + week2_rollover_income
    week2_remaining = week2_total_allocation - week2_spending

    print(f"Week 2 base allocation: ${week2_base:.2f}")
    print(f"Week 2 rollover income: ${week2_rollover_income:.2f}")
    print(f"Week 2 total allocation: ${week2_total_allocation:.2f}")
    print(f"Week 2 spending: ${week2_spending:.2f}")
    print(f"Week 2 remaining (should go to savings): ${week2_remaining:.2f}")

    # Step 6: Process second paycheck (should trigger Week 2 rollover to savings)
    print("\n--- Second Paycheck (triggers Week 2 rollover) ---")
    paycheck2_date = today  # Today

    print(f"Emergency fund before second paycheck: ${emergency_fund.get_current_balance(tm.db):.2f}")

    paycheck_split2 = processor.process_new_paycheck(
        paycheck_amount=3000.0,
        paycheck_date=paycheck2_date,
        week_start_date=paycheck2_date
    )

    print(f"Emergency fund after second paycheck: ${emergency_fund.get_current_balance(tm.db):.2f}")

    # Step 7: Verify emergency fund balance
    print("\n--- Final Verification ---")
    expected_balance = 1000.0 + 200.0 + 200.0 + week2_remaining  # initial + auto1 + auto2 + rollover
    actual_balance = emergency_fund.get_current_balance(tm.db)

    print(f"Expected emergency fund balance: ${expected_balance:.2f}")
    print(f"Actual emergency fund balance: ${actual_balance:.2f}")
    print(f"Difference: ${actual_balance - expected_balance:.2f}")

    # Step 8: Check emergency fund history
    print("\n--- Emergency Fund History ---")
    history = emergency_fund.get_account_history(tm.db)
    for i, entry in enumerate(history):
        tx_desc = f" ({entry.transaction.description})" if entry.transaction else ""
        print(f"  {i+1}. {entry.transaction_date}: ${entry.change_amount:+.2f} = ${entry.running_total:.2f}{tx_desc}")

    if abs(actual_balance - expected_balance) < 0.01:
        print("\n✅ SUCCESS: Rollover timing is working correctly!")
    else:
        print(f"\n❌ FAILURE: Expected ${expected_balance:.2f}, got ${actual_balance:.2f}")

    print("\n=== Complete Bi-weekly Cycle Test Complete ===")

    processor.close()
    tm.close()


if __name__ == "__main__":
    test_complete_biweekly_cycle()